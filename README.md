# CAAS — Cybersecurity Assessment and Awareness System

A lightweight Flask web application built for the research project
*"Enhancing Network Security in Small and Medium Enterprises (SMEs) in
Windhoek: Development of a Cybersecurity Assessment and Awareness
System."* It implements all six prototypes from the methodology:

1. **System Interface (UI)** — Bootstrap-based layout, navigation, theme
2. **Assessment Module** — SME registration + security checklist + scoring
3. **Awareness Training Module** — interactive quizzes across 8 topics
4. **Network Scanner** — lightweight port/vulnerability scan
5. **Dashboard & Reports (charts)** — Chart.js widgets
6. **Reports** — PDF / Excel / CSV export

## Quick Start (local)

```bash
cd caas_project
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

**Demo login:** `admin` / `admin123` (seeded automatically on first run,
along with 3 sample SMEs so the dashboard isn't empty).

The database file `database.db` is created automatically the first time
the app runs — nothing to configure.

## Deploying to Render (step-by-step)

1. **Push this project to a GitHub repo** (Render deploys from Git — a plain
   zip upload isn't supported). Create a new repo, then from inside the
   `caas_project` folder:
   ```bash
   git init
   git add .
   git commit -m "Initial CAAS prototype"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
2. Go to **render.com** → **New +** → **Web Service** → connect the GitHub
   repo you just pushed.
3. Render should auto-detect Python. Confirm/set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type:** Free (fine for a prototype/demo)
4. Under **Environment**, add a variable `CAAS_SECRET_KEY` with a random
   string value (don't leave the dev default in production).
5. Click **Create Web Service**. Render will build and deploy; you'll get a
   URL like `https://caas-project.onrender.com`.

A `render.yaml` Blueprint file is included in this project too — if you'd
rather not click through the dashboard, use **New +** → **Blueprint** and
point it at the repo; it reads `render.yaml` and configures the service
(including a generated secret key) automatically.

### ⚠️ Free-tier caveats to know before your demo/defense

- **The database resets on every redeploy.** Render's free web service
  filesystem is ephemeral — `database.db` (and anything in `uploads/`) is
  wiped whenever the service restarts or you push a new commit. The
  admin login and 3 sample SMEs will always re-seed automatically, but
  any assessments/training/scans you've entered will be lost. For a
  live demo this is usually fine (re-enter a few records beforehand); if
  you need real persistence, Render's paid plans support an attached
  **Disk** (see the commented-out section in `render.yaml`), or you'd
  swap SQLite for a managed Postgres instance (bigger change, not
  required for this project's scope).
- **Free instances spin down after ~15 minutes of inactivity** and take
  ~30-50 seconds to wake up on the next request. If you're demoing live,
  open the URL a minute or two before you need it.
- The Network Scanner limitation described below still applies on Render.

### ⚠️ Important limitation: the Network Scanner module

The original methodology (Section 4.1) specifies **Anaconda / local
Python** as the development environment specifically because network
scanning must run **on the SME's local network** — a cloud host such as
Render, PythonAnywhere, or Replit has no visibility into a private LAN
(e.g. `192.168.x.x` addresses) and often blocks raw ICMP ping traffic
outbound.

Deploying to a cloud platform (as chosen for this build) means:
- The scanner **will work** against any publicly reachable IP/hostname
  (useful for demonstrating the logic to examiners/lecturers).
- It **cannot** discover or scan devices inside an SME's private office
  network from the cloud.
- For genuine SME site testing (Prototype 4 / UAT), either:
  1. Run the Flask app locally on a laptop connected to the SME's Wi-Fi
     during the site visit, or
  2. Package `scanner/scanner.py` as a small standalone local agent
     script the SME runs on their own network, which posts results back
     to the cloud-hosted app's `/scanner` endpoint (a reasonable
     "future work" extension to mention in your write-up).

## Project Structure

```
caas_project/
├── app.py                     # Flask routes for all 6 prototypes
├── quiz_data.py                # Training quiz question bank
├── requirements.txt
├── database.db                 # SQLite DB (auto-created)
├── database/
│   └── models.py                # Schema, CRUD, scoring logic
├── scanner/
│   └── scanner.py                # Port/vulnerability scanning logic
├── reports/
│   └── report_generator.py       # PDF / Excel / CSV export
├── templates/                   # Jinja2 + Bootstrap templates
└── static/
    ├── css/style.css
    └── js/app.js
```

## Database Schema

| Table | Key Fields |
|---|---|
| Users | id, username, password_hash, role *(added for the login FR)* |
| SMEs | id, company_name, sector, address, email, phone, assessment_date |
| Assessment | assessment_id, sme_id, password_policy, firewall, antivirus, backup, wifi_security, mfa, security_score, risk_level |
| Employees | employee_id, employee_name, department, email |
| Training | training_id, employee_id, quiz_score, completion_date, status |
| NetworkScan | scan_id, device_ip, device_name, open_ports, vulnerability, scan_date |

## Testing Notes (for your UAT writeup)

- **Unit testing**: each module (login, assessment scoring, quiz
  grading, scanner, report export) can be exercised independently
  through its own route/function.
- **Integration testing**: the assessment → dashboard → report pipeline
  and training → dashboard pipeline can be verified end-to-end by
  submitting data and confirming it appears correctly downstream.
- **UAT**: recommended to walk 5–10 SME participants through
  Assessment → Training → (Scanner, with the cloud limitation explained)
  → Dashboard → Reports, and collect structured feedback on usability
  and relevance.
