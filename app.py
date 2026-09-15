"""
app.py
------
CAAS - Cybersecurity Assessment and Awareness System
Flask backend tying together all six prototypes described in the
methodology: UI, Assessment, Training, Network Scanner, Dashboard, Reports.
"""

import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
)
from werkzeug.security import check_password_hash

from database import models
from scanner import scanner as network_scanner
from reports import report_generator
from quiz_data import QUIZZES

app = Flask(__name__)
app.secret_key = os.environ.get("CAAS_SECRET_KEY", "dev-secret-key-change-in-production")

with app.app_context():
    models.init_db(seed=True)


# ---------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    return {"current_user": session.get("username")}


# ---------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = models.get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        if not username or not password:
            flash("Username and password are required.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif models.get_user_by_username(username):
            flash("That username is already taken.", "danger")
        else:
            models.create_user(username, password)
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------
# Dashboard (Prototype 5)
# ---------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    stats = models.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


# ---------------------------------------------------------------------
# Assessment Module (Prototype 2)
# ---------------------------------------------------------------------
@app.route("/assessment")
@login_required
def assessment():
    smes = models.get_all_smes()
    assessments = models.get_all_assessments()
    return render_template("assessment.html", smes=smes, assessments=assessments)


@app.route("/assessment/new", methods=["GET", "POST"])
@login_required
def assessment_new():
    if request.method == "POST":
        sme_mode = request.form.get("sme_mode")
        if sme_mode == "existing" and request.form.get("sme_id_existing"):
            sme_id = int(request.form.get("sme_id_existing"))
        else:
            sme_id = models.create_sme(
                request.form.get("company_name", "").strip(),
                request.form.get("sector", "").strip(),
                request.form.get("address", "").strip(),
                request.form.get("email", "").strip(),
                request.form.get("phone", "").strip(),
            )

        answers = {field: 1 if request.form.get(field) == "on" else 0
                   for field, _ in models.CHECKLIST_FIELDS}
        score, risk_level = models.create_assessment(sme_id, answers)
        flash(f"Assessment saved. Security score: {score}% ({risk_level} Risk).", "success")
        return redirect(url_for("assessment"))

    smes = models.get_all_smes()
    return render_template("assessment_new.html", smes=smes, checklist=models.CHECKLIST_FIELDS)


# ---------------------------------------------------------------------
# Training Module (Prototype 3)
# ---------------------------------------------------------------------
@app.route("/training")
@login_required
def training():
    results = models.get_all_training_results()
    return render_template("training.html", topics=QUIZZES, results=results)


@app.route("/training/quiz/<topic>", methods=["GET", "POST"])
@login_required
def training_quiz(topic):
    quiz = QUIZZES.get(topic)
    if not quiz:
        flash("Unknown training topic.", "danger")
        return redirect(url_for("training"))

    if request.method == "POST":
        employee_name = request.form.get("employee_name", "").strip() or session.get("username", "Anonymous")
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()

        correct = 0
        for i, q in enumerate(quiz["questions"]):
            selected = request.form.get(f"q{i}")
            if selected is not None and int(selected) == q["answer"]:
                correct += 1
        score = round((correct / len(quiz["questions"])) * 100, 1)

        employee_id = models.get_or_create_employee(employee_name, department, email)
        status = models.record_training_result(employee_id, quiz["title"], score)

        return render_template(
            "training_quiz.html", topic=topic, quiz=quiz, submitted=True,
            score=score, status=status, correct=correct, total=len(quiz["questions"])
        )

    return render_template("training_quiz.html", topic=topic, quiz=quiz, submitted=False)


# ---------------------------------------------------------------------
# Network Scanner (Prototype 4)
# ---------------------------------------------------------------------
@app.route("/scanner", methods=["GET", "POST"])
@login_required
def scanner_page():
    result = None
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        if target:
            result = network_scanner.scan_host(target)
            if not result.get("error"):
                models.save_scan_result(
                    device_ip=result["device_ip"],
                    device_name=result["device_name"],
                    open_ports=", ".join(result["open_ports_named"]) or "None",
                    vulnerability="; ".join(result["vulnerabilities"]) or "None detected",
                )
        else:
            flash("Please enter an IP address or hostname to scan.", "warning")

    history = models.get_all_scans()
    return render_template("scanner.html", result=result, history=history)


# ---------------------------------------------------------------------
# Reports (Prototype 6)
# ---------------------------------------------------------------------
@app.route("/reports")
@login_required
def reports_page():
    return render_template("reports.html")


@app.route("/reports/download/<report_type>/<fmt>")
@login_required
def download_report(report_type, fmt):
    if report_type == "assessment":
        headers = ["Company", "Sector", "Score (%)", "Risk Level", "Date"]
        rows = [
            (a["company_name"], a["sector"], a["security_score"], a["risk_level"], a["created_at"])
            for a in models.get_all_assessments()
        ]
    elif report_type == "training":
        headers = ["Employee", "Department", "Topic", "Score (%)", "Status", "Date"]
        rows = [
            (t["employee_name"], t["department"], t["topic"], t["quiz_score"], t["status"], t["completion_date"])
            for t in models.get_all_training_results()
        ]
    elif report_type == "vulnerability":
        headers = ["Device/IP", "Device Name", "Open Ports", "Vulnerability", "Scan Date"]
        rows = [
            (s["device_ip"], s["device_name"], s["open_ports"], s["vulnerability"], s["scan_date"])
            for s in models.get_all_scans()
        ]
    else:
        flash("Unknown report type.", "danger")
        return redirect(url_for("reports_page"))

    buffer, mimetype, ext = report_generator.build_report(report_type, fmt, headers, rows)
    filename = f"caas_{report_type}_report.{ext}"
    return send_file(buffer, mimetype=mimetype, as_attachment=True, download_name=filename)


# ---------------------------------------------------------------------
# JSON endpoint for dashboard chart data (used by static/js/app.js)
# ---------------------------------------------------------------------
@app.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    stats = models.get_dashboard_stats()
    return jsonify({
        "risk_distribution": {row["risk_level"]: row["count"] for row in stats["risk_distribution"]},
        "score_by_sme": [
            {"company": row["company_name"], "score": row["security_score"], "date": row["created_at"]}
            for row in stats["score_by_sme"]
        ],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
