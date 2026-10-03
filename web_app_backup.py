from flask import Flask, render_template_string, request, redirect, session, send_file
import sqlite3
import os
import csv
import subprocess
import sys
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smartattend_secure_key_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "smartattend.db")
APP_DIR = os.path.join(BASE_DIR, "app")
LIVE_ATTENDANCE = os.path.join(APP_DIR, "live_attendance.py")


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def get_dashboard_data():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE date = ?
        AND status = 'Present'
    """, (today,))

    present_today = cursor.fetchone()[0]

    absent_today = max(total_students - present_today, 0)

    percentage = (
        round((present_today / total_students) * 100)
        if total_students > 0 else 0
    )

    cursor.execute("""
        SELECT
            students.name,
            students.roll_no,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        INNER JOIN students
        ON attendance.student_id = students.id
        ORDER BY attendance.id DESC
        LIMIT 10
    """)

    records = cursor.fetchall()

    connection.close()

    return (
        total_students,
        present_today,
        absent_today,
        percentage,
        records
    )


# =========================================================
# COMMON STYLE
# =========================================================

STYLE = """
<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: white;
}

.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 240px;
    height: 100vh;
    background: #111827;
    padding: 30px 20px;
}

.logo {
    font-size: 22px;
    font-weight: bold;
    text-align: center;
}

.logo-sub {
    color: #64748b;
    font-size: 9px;
    text-align: center;
    margin-top: 5px;
    margin-bottom: 40px;
}

.menu {
    display: block;
    padding: 13px;
    color: #cbd5e1;
    border-radius: 7px;
    margin-bottom: 6px;
    text-decoration: none;
}

.menu:hover,
.menu.active {
    background: #1e293b;
    color: white;
}

.logout {
    position: absolute;
    bottom: 30px;
    left: 20px;
    right: 20px;
    text-align: center;
}

.logout a {
    color: #ef4444;
    text-decoration: none;
}

.main {
    margin-left: 240px;
    padding: 35px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    margin: 0;
    font-size: 30px;
}

.header p {
    color: #64748b;
}

.admin {
    background: #1e293b;
    padding: 10px 15px;
    border-radius: 8px;
    color: #cbd5e1;
}

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-top: 25px;
}

.card {
    background: #1e293b;
    padding: 23px;
    border-radius: 10px;
    border-left: 4px solid #3b82f6;
}

.card:nth-child(2) {
    border-color: #22c55e;
}

.card:nth-child(3) {
    border-color: #ef4444;
}

.card:nth-child(4) {
    border-color: #a855f7;
}

.card-title {
    color: #94a3b8;
    font-size: 11px;
    font-weight: bold;
}

.card-value {
    font-size: 30px;
    font-weight: bold;
    margin-top: 8px;
}

.box {
    background: #1e293b;
    margin-top: 30px;
    border-radius: 10px;
    padding: 25px;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

label {
    display: block;
    color: #94a3b8;
    font-size: 11px;
    font-weight: bold;
    margin-bottom: 7px;
}

input,
select {
    width: 100%;
    padding: 13px;
    background: #0f172a;
    color: white;
    border: 1px solid #334155;
    border-radius: 7px;
    outline: none;
}

input:focus,
select:focus {
    border-color: #3b82f6;
}

button {
    padding: 13px 25px;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 7px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #1d4ed8;
}

.green-button {
    background: #16a34a;
}

.green-button:hover {
    background: #15803d;
}

.search {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.search input {
    max-width: 350px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    color: #94a3b8;
    font-size: 11px;
    text-align: left;
    padding: 14px;
    background: #334155;
}

td {
    padding: 14px;
    border-bottom: 1px solid #334155;
    color: #cbd5e1;
}

.status {
    color: #22c55e;
    font-weight: bold;
}

.not-status {
    color: #f59e0b;
    font-weight: bold;
}

.message {
    padding: 12px;
    background: #14532d;
    color: #bbf7d0;
    border-radius: 7px;
    margin-bottom: 18px;
}

.error {
    padding: 12px;
    background: #450a0a;
    color: #fca5a5;
    border-radius: 7px;
    margin-bottom: 18px;
}

.action-box {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.big-action {
    padding: 18px 25px;
    min-width: 220px;
    text-align: center;
    text-decoration: none;
    color: white;
    background: #2563eb;
    border-radius: 10px;
    font-weight: bold;
}

.big-action:hover {
    background: #1d4ed8;
}

</style>
"""


# =========================================================
# LOGIN PAGE
# =========================================================

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>SMARTATTEND AI | Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
""" + STYLE + """
<style>

body {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-box {
    width: 390px;
    background: #1e293b;
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.45);
}

.login-logo {
    text-align: center;
    font-size: 27px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    margin: 7px 0 35px;
}

.login-box input {
    margin-bottom: 20px;
}

.login-box button {
    width: 100%;
}

</style>
</head>

<body>

<div class="login-box">

<div class="login-logo">
SMARTATTEND AI
</div>

<div class="subtitle">
AI-BASED ATTENDANCE MANAGEMENT SYSTEM
</div>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form method="POST">

<label>USERNAME</label>

<input
type="text"
name="username"
placeholder="Enter username"
required>

<label>PASSWORD</label>

<input
type="password"
name="password"
placeholder="Enter password"
required>

<button type="submit">
ADMIN LOGIN
</button>

</form>

</div>

</body>
</html>
"""


# =========================================================
# SIDEBAR
# =========================================================

def sidebar(active):

    return f"""
    <div class="sidebar">

        <div class="logo">
            SMARTATTEND
        </div>

        <div class="logo-sub">
            AI ATTENDANCE SYSTEM
        </div>

        <a class="menu {'active' if active == 'dashboard' else ''}"
           href="/dashboard">
           ⌂ &nbsp; Dashboard
        </a>

        <a class="menu {'active' if active == 'students' else ''}"
           href="/students">
           👨‍🎓 &nbsp; Students
        </a>

        <a class="menu {'active' if active == 'face' else ''}"
           href="/face">
           📷 &nbsp; Face Recognition
        </a>

        <a class="menu {'active' if active == 'attendance' else ''}"
           href="/attendance">
           ✓ &nbsp; Attendance
        </a>

        <a class="menu {'active' if active == 'reports' else ''}"
           href="/reports">
           📊 &nbsp; Reports
        </a>

        <div class="logout">
            <a href="/logout">LOGOUT</a>
        </div>

    </div>
    """


# =========================================================
# DASHBOARD
# =========================================================

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>SMARTATTEND AI | Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
""" + STYLE + """
</head>

<body>

{{ sidebar|safe }}

<div class="main">

<div class="header">

<div>
<h1>Dashboard</h1>
<p>Smart Attendance Management System</p>
</div>

<div class="admin">
👤 Admin
</div>

</div>

<div class="cards">

<div class="card">
<div class="card-title">TOTAL STUDENTS</div>
<div class="card-value">{{ total }}</div>
</div>

<div class="card">
<div class="card-title">PRESENT TODAY</div>
<div class="card-value">{{ present }}</div>
</div>

<div class="card">
<div class="card-title">ABSENT TODAY</div>
<div class="card-value">{{ absent }}</div>
</div>

<div class="card">
<div class="card-title">ATTENDANCE</div>
<div class="card-value">{{ percentage }}%</div>
</div>

</div>

<div class="box">

<h2>Recent Attendance</h2>

<table>

<tr>
<th>STUDENT</th>
<th>ROLL NUMBER</th>
<th>DATE</th>
<th>TIME</th>
<th>STATUS</th>
</tr>

{% for record in records %}

<tr>
<td>{{ record[0] }}</td>
<td>{{ record[1] }}</td>
<td>{{ record[2] }}</td>
<td>{{ record[3] }}</td>
<td class="status">{{ record[4] }}</td>
</tr>

{% endfor %}

</table>

</div>

</div>

</body>
</html>
"""


# =========================================================
# STUDENT PAGE
# =========================================================

STUDENT_PAGE = """
<!DOCTYPE html>
<html>
<head>

<title>SMARTATTEND AI | Students</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + STYLE + """

</head>

<body>

{{ sidebar|safe }}

<div class="main">

<div class="header">

<div>
<h1>Student Management</h1>
<p>Manage student profiles and face registration</p>
</div>

<div class="admin">
👤 Admin
</div>

</div>

<div class="box">

<h2>Add New Student</h2>

{% if message %}
<div class="message">
{{ message }}
</div>
{% endif %}

{% if error %}
<div class="error">
{{ error }}
</div>
{% endif %}

<form method="POST" action="/students">

<div class="form-grid">

<div>
<label>STUDENT NAME</label>
<input
type="text"
name="name"
placeholder="Enter student name"
required>
</div>

<div>
<label>ROLL NUMBER</label>
<input
type="text"
name="roll"
placeholder="Enter roll number"
required>
</div>

<div>
<label>BRANCH / DEPARTMENT</label>

<select name="department" required>

<option value="">Select Branch</option>
<option>ECE</option>
<option>CSE</option>
<option>EEE</option>
<option>MECH</option>
<option>CIVIL</option>
<option>AI & DS</option>
<option>AI & ML</option>
<option>IT</option>

</select>

</div>

<div>

<label>YEAR</label>

<select name="year" required>

<option value="">Select Year</option>
<option>1st Year</option>
<option>2nd Year</option>
<option>3rd Year</option>
<option>4th Year</option>

</select>

</div>

</div>

<br>

<button type="submit">
+ ADD STUDENT
</button>

</form>

</div>

<div class="box">

<h2>Registered Students</h2>

<form method="GET"
action="/students"
class="search">

<input
type="text"
name="search"
value="{{ search }}"
placeholder="Search name, roll number or branch">

<button type="submit">
SEARCH
</button>

</form>

<table>

<tr>
<th>ID</th>
<th>STUDENT NAME</th>
<th>ROLL NUMBER</th>
<th>BRANCH</th>
<th>YEAR</th>
<th>FACE STATUS</th>
</tr>

{% for student in students %}

<tr>

<td>{{ student[0] }}</td>
<td>{{ student[1] }}</td>
<td>{{ student[2] }}</td>
<td>{{ student[3] }}</td>
<td>{{ student[4] }}</td>

<td>

{% if student[5] %}

<span class="status">
● REGISTERED
</span>

{% else %}

<span class="not-status">
○ NOT REGISTERED
</span>

{% endif %}

</td>

</tr>

{% endfor %}

</table>

</div>

</div>

</body>
</html>
"""


# =========================================================
# ATTENDANCE PAGE
# =========================================================

ATTENDANCE_PAGE = """
<!DOCTYPE html>
<html>
<head>

<title>SMARTATTEND AI | Attendance</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + STYLE + """

</head>

<body>

{{ sidebar|safe }}

<div class="main">

<div class="header">

<div>
<h1>Attendance</h1>
<p>Student attendance records</p>
</div>

<div class="admin">
👤 Admin
</div>

</div>

<div class="box">

<h2>Attendance Records</h2>

<br>

<table>

<tr>
<th>S.NO</th>
<th>STUDENT</th>
<th>ROLL NUMBER</th>
<th>DATE</th>
<th>TIME</th>
<th>STATUS</th>
</tr>

{% for record in records %}

<tr>

<td>{{ loop.index }}</td>
<td>{{ record[0] }}</td>
<td>{{ record[1] }}</td>
<td>{{ record[2] }}</td>
<td>{{ record[3] }}</td>

<td class="status">
● {{ record[4] }}
</td>

</tr>

{% endfor %}

</table>

</div>

</div>

</body>
</html>
"""


# =========================================================
# REPORTS PAGE
# =========================================================

REPORTS_PAGE = """
<!DOCTYPE html>
<html>
<head>

<title>SMARTATTEND AI | Reports</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + STYLE + """

</head>

<body>

{{ sidebar|safe }}

<div class="main">

<div class="header">

<div>
<h1>Attendance Reports</h1>
<p>Analyze and export attendance records</p>
</div>

<div class="admin">
👤 Admin
</div>

</div>

<div class="box">

<h2>Filter Attendance</h2>

<form method="GET" action="/reports" class="search">

<input
type="date"
name="date"
value="{{ selected_date }}">

<button type="submit">
FILTER
</button>

<a href="/reports"
class="big-action"
style="padding:13px 20px; min-width:120px;">
SHOW ALL
</a>

<a href="/export"
class="big-action"
style="padding:13px 20px; min-width:150px;">
EXPORT CSV
</a>

</form>

</div>

<div class="box">

<h2>Report Data</h2>

<br>

<table>

<tr>
<th>S.NO</th>
<th>STUDENT</th>
<th>ROLL NUMBER</th>
<th>BRANCH</th>
<th>DATE</th>
<th>TIME</th>
<th>STATUS</th>
</tr>

{% for record in records %}

<tr>

<td>{{ loop.index }}</td>
<td>{{ record[0] }}</td>
<td>{{ record[1] }}</td>
<td>{{ record[2] }}</td>
<td>{{ record[3] }}</td>
<td>{{ record[4] }}</td>
<td class="status">{{ record[5] }}</td>

</tr>

{% endfor %}

</table>

</div>

</div>

</body>
</html>
"""


# =========================================================
# FACE RECOGNITION PAGE
# =========================================================

FACE_PAGE = """
<!DOCTYPE html>
<html>
<head>

<title>SMARTATTEND AI | Face Recognition</title>

<meta name="viewport"
content="width=device-width, initial-scale=1">

""" + STYLE + """

</head>

<body>

{{ sidebar|safe }}

<div class="main">

<div class="header">

<div>
<h1>Face Recognition</h1>
<p>AI-based live attendance recognition</p>
</div>

<div class="admin">
👤 Admin
</div>

</div>

<div class="box">

<h2>Live Face Recognition</h2>

<p style="color:#94a3b8;">
Start the camera to recognize registered students
and mark attendance automatically.
</p>

<br>

<a href="/start-camera"
class="big-action">
📷 START CAMERA
</a>

</div>

<div class="box">

<h2>System Status</h2>

<p>
<span class="status">● DATABASE CONNECTED</span>
</p>

<p>
<span class="{{ model_class }}">
● {{ model_status }}
</span>
</p>

</div>

</div>

</body>
</html>
"""


# =========================================================
# LOGIN
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/dashboard")

        error = "Invalid username or password."

    return render_template_string(
        LOGIN_PAGE,
        error=error
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect("/")

    data = get_dashboard_data()

    return render_template_string(
        DASHBOARD_PAGE,
        sidebar=sidebar("dashboard"),
        total=data[0],
        present=data[1],
        absent=data[2],
        percentage=data[3],
        records=data[4]
    )


# =========================================================
# STUDENTS
# =========================================================

@app.route("/students", methods=["GET", "POST"])
def students():

    if not session.get("admin"):
        return redirect("/")

    message = None
    error = None

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        roll = request.form.get("roll", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO students
                (name, roll_no, department, year)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                roll,
                department,
                year
            ))

            connection.commit()
            connection.close()

            return redirect("/students?added=1")

        except sqlite3.IntegrityError:

            error = "Roll number already exists."

    search = request.args.get("search", "").strip()

    if request.args.get("added") == "1":
        message = "Student added successfully."

    connection = get_connection()
    cursor = connection.cursor()

    if search:

        cursor.execute("""
            SELECT
                id,
                name,
                roll_no,
                department,
                year,
                face_registered
            FROM students
            WHERE name LIKE ?
            OR roll_no LIKE ?
            OR department LIKE ?
            ORDER BY id DESC
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("""
            SELECT
                id,
                name,
                roll_no,
                department,
                year,
                face_registered
            FROM students
            ORDER BY id DESC
        """)

    student_list = cursor.fetchall()

    connection.close()

    return render_template_string(
        STUDENT_PAGE,
        sidebar=sidebar("students"),
        students=student_list,
        search=search,
        message=message,
        error=error
    )


# =========================================================
# ATTENDANCE
# =========================================================

@app.route("/attendance")
def attendance():

    if not session.get("admin"):
        return redirect("/")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            students.name,
            students.roll_no,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        INNER JOIN students
        ON attendance.student_id = students.id
        ORDER BY attendance.id DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return render_template_string(
        ATTENDANCE_PAGE,
        sidebar=sidebar("attendance"),
        records=records
    )


# =========================================================
# REPORTS
# =========================================================

@app.route("/reports")
def reports():

    if not session.get("admin"):
        return redirect("/")

    selected_date = request.args.get("date", "").strip()

    connection = get_connection()
    cursor = connection.cursor()

    if selected_date:

        cursor.execute("""
            SELECT
                students.name,
                students.roll_no,
                students.department,
                students.year,
                attendance.date,
                attendance.time,
                attendance.status
            FROM attendance
            INNER JOIN students
            ON attendance.student_id = students.id
            WHERE attendance.date = ?
            ORDER BY attendance.id DESC
        """, (selected_date,))

    else:

        cursor.execute("""
            SELECT
                students.name,
                students.roll_no,
                students.department,
                students.year,
                attendance.date,
                attendance.time,
                attendance.status
            FROM attendance
            INNER JOIN students
            ON attendance.student_id = students.id
            ORDER BY attendance.id DESC
        """)

    records = cursor.fetchall()

    connection.close()

    return render_template_string(
        REPORTS_PAGE,
        sidebar=sidebar("reports"),
        records=records,
        selected_date=selected_date
    )


# =========================================================
# EXPORT CSV
# =========================================================

@app.route("/export")
def export_csv():

    if not session.get("admin"):
        return redirect("/")

    export_dir = os.path.join(BASE_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)

    file_path = os.path.join(
        export_dir,
        "attendance_report.csv"
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            students.name,
            students.roll_no,
            students.department,
            students.year,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        INNER JOIN students
        ON attendance.student_id = students.id
        ORDER BY attendance.id DESC
    """)

    records = cursor.fetchall()

    connection.close()

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Student Name",
            "Roll Number",
            "Department",
            "Year",
            "Date",
            "Time",
            "Status"
        ])

        writer.writerows(records)

    return send_file(
        file_path,
        as_attachment=True,
        download_name="attendance_report.csv"
    )


# =========================================================
# FACE RECOGNITION
# =========================================================

@app.route("/face")
def face():

    if not session.get("admin"):
        return redirect("/")

    model_path = os.path.join(
        BASE_DIR,
        "models",
        "trainer.yml"
    )

    if os.path.exists(model_path):

        model_status = "MODEL READY"
        model_class = "status"

    else:

        model_status = "MODEL NOT TRAINED"
        model_class = "not-status"

    return render_template_string(
        FACE_PAGE,
        sidebar=sidebar("face"),
        model_status=model_status,
        model_class=model_class
    )


# =========================================================
# START CAMERA
# =========================================================

@app.route("/start-camera")
def start_camera():

    if not session.get("admin"):
        return redirect("/")

    if not os.path.exists(LIVE_ATTENDANCE):

        return """
        <h2>Live attendance file not found.</h2>
        <a href="/face">Go Back</a>
        """

    try:

        subprocess.Popen(
            [sys.executable, LIVE_ATTENDANCE],
            cwd=BASE_DIR
        )

    except Exception as error:

        return f"""
        <h2>Camera could not be started.</h2>
        <p>{error}</p>
        <a href="/face">Go Back</a>
        """

    return redirect("/face")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("========================================")
    print("       SMARTATTEND AI WEB SERVER")
    print("========================================")
    print("Chrome:")
    print("http://127.0.0.1:5000")
    print("========================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )