"""
database/models.py
-------------------
All database access for the Cybersecurity Assessment and Awareness
System (CAAS) lives here. SQLite is used to keep the system lightweight,
as specified in the Non-Functional Requirements (NFR).

Tables (matches Section 4.4 of the methodology, plus a Users table
required to satisfy the "user login & authentication" Functional
Requirement, which the original 5-table design did not explicitly list):

    Users          id, username, password_hash, role
    SMEs           id, company_name, sector, address, email, phone, assessment_date
    Assessment     assessment_id, sme_id, password_policy, firewall, antivirus,
                   backup, wifi_security, mfa, security_score, risk_level, created_at
    Employees      employee_id, employee_name, department, email
    Training       training_id, employee_id, topic, quiz_score, completion_date, status
    NetworkScan    scan_id, device_ip, device_name, open_ports, vulnerability, scan_date
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed=True):
    """Create all tables if they do not exist yet, and seed a default
    admin user + sample data on first run so the dashboard/reports are
    not empty when a marker/lecturer opens the app."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'manager'
        );

        CREATE TABLE IF NOT EXISTS SMEs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            sector TEXT,
            address TEXT,
            email TEXT,
            phone TEXT,
            assessment_date TEXT
        );

        CREATE TABLE IF NOT EXISTS Assessment (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sme_id INTEGER NOT NULL,
            password_policy INTEGER NOT NULL DEFAULT 0,
            firewall INTEGER NOT NULL DEFAULT 0,
            antivirus INTEGER NOT NULL DEFAULT 0,
            backup INTEGER NOT NULL DEFAULT 0,
            wifi_security INTEGER NOT NULL DEFAULT 0,
            mfa INTEGER NOT NULL DEFAULT 0,
            security_score REAL NOT NULL,
            risk_level TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (sme_id) REFERENCES SMEs (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS Employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            department TEXT,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS Training (
            training_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            quiz_score REAL NOT NULL,
            completion_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES Employees (employee_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS NetworkScan (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_ip TEXT NOT NULL,
            device_name TEXT,
            open_ports TEXT,
            vulnerability TEXT,
            scan_date TEXT NOT NULL
        );
        """
    )
    conn.commit()

    if seed:
        _seed_defaults(conn)

    conn.close()


def _seed_defaults(conn):
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Users")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", generate_password_hash("admin123"), "manager"),
        )

    cur.execute("SELECT COUNT(*) FROM SMEs")
    if cur.fetchone()[0] == 0:
        sample_smes = [
            ("Kalahari Traders", "Retail", "Independence Ave, Windhoek", "info@kalahari.na", "0811234567"),
            ("Windhoek IT Solutions", "IT Services", "Nelson Mandela Ave, Windhoek", "hello@wits.na", "0817654321"),
            ("Namib Fresh Foods", "Food & Beverage", "Klein Windhoek", "contact@namibfresh.na", "0812223344"),
        ]
        today = datetime.now().strftime("%Y-%m-%d")
        for name, sector, address, email, phone in sample_smes:
            cur.execute(
                "INSERT INTO SMEs (company_name, sector, address, email, phone, assessment_date) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (name, sector, address, email, phone, today),
            )
    conn.commit()


# ---------------------------------------------------------------------
# SMEs
# ---------------------------------------------------------------------
def create_sme(company_name, sector, address, email, phone):
    conn = get_db_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    cur = conn.execute(
        "INSERT INTO SMEs (company_name, sector, address, email, phone, assessment_date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (company_name, sector, address, email, phone, today),
    )
    conn.commit()
    sme_id = cur.lastrowid
    conn.close()
    return sme_id


def get_all_smes():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM SMEs ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def get_sme(sme_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM SMEs WHERE id = ?", (sme_id,)).fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------------
# Assessment (Prototype 2)
# ---------------------------------------------------------------------
CHECKLIST_FIELDS = [
    ("password_policy", "Does your company have a documented password policy?"),
    ("firewall", "Is a firewall enabled on your network?"),
    ("antivirus", "Is antivirus/anti-malware software installed on all devices?"),
    ("backup", "Are data backups performed regularly?"),
    ("wifi_security", "Is your Wi-Fi network password protected (WPA2/WPA3)?"),
    ("mfa", "Is multi-factor authentication (MFA) enabled for key accounts?"),
]


def calculate_score(answers: dict):
    """answers: dict of field -> 1 (yes) / 0 (no). Returns (score, risk_level)."""
    total = len(CHECKLIST_FIELDS)
    yes_count = sum(int(answers.get(field, 0)) for field, _ in CHECKLIST_FIELDS)
    score = round((yes_count / total) * 100, 1) if total else 0.0

    if score >= 80:
        risk_level = "Low"
    elif score >= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"
    return score, risk_level


def create_assessment(sme_id, answers: dict):
    score, risk_level = calculate_score(answers)
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO Assessment
           (sme_id, password_policy, firewall, antivirus, backup, wifi_security, mfa,
            security_score, risk_level, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            sme_id,
            int(answers.get("password_policy", 0)),
            int(answers.get("firewall", 0)),
            int(answers.get("antivirus", 0)),
            int(answers.get("backup", 0)),
            int(answers.get("wifi_security", 0)),
            int(answers.get("mfa", 0)),
            score,
            risk_level,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ),
    )
    conn.commit()
    conn.close()
    return score, risk_level


def get_all_assessments():
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT Assessment.*, SMEs.company_name, SMEs.sector
           FROM Assessment JOIN SMEs ON Assessment.sme_id = SMEs.id
           ORDER BY Assessment.assessment_id DESC"""
    ).fetchall()
    conn.close()
    return rows


def get_assessments_for_sme(sme_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM Assessment WHERE sme_id = ? ORDER BY assessment_id DESC", (sme_id,)
    ).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------
# Employees & Training (Prototype 3)
# ---------------------------------------------------------------------
def get_or_create_employee(employee_name, department, email):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM Employees WHERE employee_name = ? AND email = ?",
        (employee_name, email),
    ).fetchone()
    if row:
        conn.close()
        return row["employee_id"]
    cur = conn.execute(
        "INSERT INTO Employees (employee_name, department, email) VALUES (?, ?, ?)",
        (employee_name, department, email),
    )
    conn.commit()
    emp_id = cur.lastrowid
    conn.close()
    return emp_id


def record_training_result(employee_id, topic, quiz_score, passing_score=70):
    status = "Passed" if quiz_score >= passing_score else "Failed"
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO Training (employee_id, topic, quiz_score, completion_date, status)
           VALUES (?, ?, ?, ?, ?)""",
        (employee_id, topic, quiz_score, datetime.now().strftime("%Y-%m-%d %H:%M"), status),
    )
    conn.commit()
    conn.close()
    return status


def get_all_training_results():
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT Training.*, Employees.employee_name, Employees.department
           FROM Training JOIN Employees ON Training.employee_id = Employees.employee_id
           ORDER BY Training.training_id DESC"""
    ).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------
# Network Scan (Prototype 4)
# ---------------------------------------------------------------------
def save_scan_result(device_ip, device_name, open_ports, vulnerability):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO NetworkScan (device_ip, device_name, open_ports, vulnerability, scan_date)
           VALUES (?, ?, ?, ?, ?)""",
        (device_ip, device_name, open_ports, vulnerability, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()


def get_all_scans():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM NetworkScan ORDER BY scan_id DESC").fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------
# Dashboard aggregates (Prototype 5)
# ---------------------------------------------------------------------
def get_dashboard_stats():
    conn = get_db_connection()

    total_assessments = conn.execute("SELECT COUNT(*) FROM Assessment").fetchone()[0]
    avg_score_row = conn.execute("SELECT AVG(security_score) FROM Assessment").fetchone()[0]
    avg_score = round(avg_score_row, 1) if avg_score_row else 0
    high_risk = conn.execute(
        "SELECT COUNT(*) FROM Assessment WHERE risk_level = 'High'"
    ).fetchone()[0]
    completed_training = conn.execute(
        "SELECT COUNT(*) FROM Training WHERE status = 'Passed'"
    ).fetchone()[0]
    open_vulns = conn.execute(
        "SELECT COUNT(*) FROM NetworkScan WHERE vulnerability != 'None detected'"
    ).fetchone()[0]
    avg_quiz_row = conn.execute("SELECT AVG(quiz_score) FROM Training").fetchone()[0]
    avg_quiz_score = round(avg_quiz_row, 1) if avg_quiz_row else 0

    risk_distribution = conn.execute(
        "SELECT risk_level, COUNT(*) as count FROM Assessment GROUP BY risk_level"
    ).fetchall()

    score_by_sme = conn.execute(
        """SELECT SMEs.company_name, Assessment.security_score, Assessment.created_at
           FROM Assessment JOIN SMEs ON Assessment.sme_id = SMEs.id
           ORDER BY Assessment.assessment_id ASC"""
    ).fetchall()

    conn.close()
    return {
        "total_assessments": total_assessments,
        "avg_score": avg_score,
        "high_risk": high_risk,
        "completed_training": completed_training,
        "open_vulns": open_vulns,
        "avg_quiz_score": avg_quiz_score,
        "risk_distribution": risk_distribution,
        "score_by_sme": score_by_sme,
    }


# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
def get_user_by_username(username):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


def create_user(username, password, role="manager"):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), role),
    )
    conn.commit()
    conn.close()
