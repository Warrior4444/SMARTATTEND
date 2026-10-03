from flask import Flask, request, redirect, session, jsonify, Response
import sqlite3
import os
import shutil
import subprocess
import sys
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smartattend_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "smartattend.db"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "trainer.yml"
)

THRESHOLD = 150


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# FACE MODEL
# =========================================================

recognizer = None

try:

    if os.path.exists(MODEL_PATH):

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(MODEL_PATH)

        print("FACE MODEL LOADED")

    else:

        print("FACE MODEL NOT FOUND")

except Exception as e:

    print("MODEL ERROR:", e)


# =========================================================
# ATTENDANCE
# =========================================================

def mark_attendance(student_id):

    conn = get_db()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    cur.execute(
        """
        SELECT id
        FROM attendance
        WHERE student_id=? AND date=?
        """,
        (student_id, today)
    )

    existing = cur.fetchone()

    if existing:

        conn.close()

        return False, "Already marked today"

    cur.execute(
        """
        INSERT INTO attendance
        (student_id, date, time, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            student_id,
            today,
            current_time,
            "Present"
        )
    )

    conn.commit()
    conn.close()

    return True, "Attendance marked"


# =========================================================
# CSS
# =========================================================

CSS = """
<style>

* {
    box-sizing: border-box;
    font-family: Arial, sans-serif;
}

body {
    margin: 0;
    background: #0b1020;
    color: #f5f7ff;
}

.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 240px;
    height: 100vh;
    background: #11182d;
    padding: 25px 15px;
    border-right: 1px solid #26304d;
}

.logo {
    font-size: 25px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 35px;
    color: #62d9ff;
}

.logo span {
    color: white;
}

.nav {
    display: block;
    padding: 14px 18px;
    margin: 8px 0;
    color: #b9c4df;
    text-decoration: none;
    border-radius: 10px;
    transition: .2s;
}

.nav:hover {
    background: #1d2948;
    color: white;
}

.logout {
    margin-top: 35px;
    color: #ff6b81;
}

.main {
    margin-left: 240px;
    padding: 30px;
}

.title {
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 8px;
}

.subtitle {
    color: #8995b5;
    margin-bottom: 30px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 30px;
}

.card {
    background: #131c34;
    border: 1px solid #273452;
    border-radius: 15px;
    padding: 22px;
}

.card h3 {
    margin: 0;
    color: #8f9bb8;
    font-size: 14px;
}

.card .number {
    font-size: 32px;
    font-weight: bold;
    margin-top: 12px;
}

.panel {
    background: #131c34;
    border: 1px solid #273452;
    border-radius: 15px;
    padding: 22px;
    margin-bottom: 25px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    color: #7f8baa;
    text-align: left;
    padding: 14px;
    border-bottom: 1px solid #293653;
}

td {
    padding: 14px;
    border-bottom: 1px solid #202b45;
}

input,
select {
    background: #0d1428;
    border: 1px solid #30405f;
    color: white;
    padding: 12px;
    border-radius: 8px;
    width: 100%;
    margin: 7px 0;
}

button,
.btn {
    background: #1d9bf0;
    color: white;
    border: 0;
    padding: 11px 18px;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin-top: 8px;
}

button:hover,
.btn:hover {
    opacity: .85;
}

.delete {
    background: #e74c5b;
}

.green {
    color: #55e69b;
}

.red {
    color: #ff7182;
}

.badge {
    padding: 6px 10px;
    border-radius: 20px;
    background: #173f32;
    color: #5cf0a4;
}

.search {
    max-width: 350px;
    margin-bottom: 15px;
}

/* CAMERA */

.camera-box {
    position: relative;
    width: 100%;
    max-width: 900px;
    height: 560px;
    margin: 0 auto;
    background: #000;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid #263241;
}

.camera-box video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scaleX(-1);
}

.camera-overlay {
    position: absolute;
    left: 20px;
    right: 20px;
    bottom: 20px;
    text-align: center;
    pointer-events: none;
}

.recognition-name {
    display: inline-block;
    background: rgba(0, 0, 0, .78);
    border: 2px solid #42e8a0;
    color: #42e8a0;
    padding: 12px 25px;
    border-radius: 12px;
    font-size: 25px;
    font-weight: bold;
    min-width: 250px;
}

.status {
    max-width: 900px;
    margin: 15px auto;
    padding: 13px;
    background: #111a30;
    border-radius: 10px;
    text-align: center;
    color: #aab5cf;
}

.camera-buttons {
    text-align: center;
    margin: 20px;
}

.stop {
    background: #e74c5b;
}

.login-box {
    width: 380px;
    margin: 100px auto;
    background: #131c34;
    padding: 35px;
    border-radius: 18px;
    border: 1px solid #293653;
}

.login-box h1 {
    text-align: center;
    color: #62d9ff;
}

@media(max-width: 900px) {

    .cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .sidebar {
        width: 190px;
    }

    .main {
        margin-left: 190px;
    }
}

</style>
"""


# =========================================================
# SIDEBAR
# =========================================================

def sidebar():

    return """
    <div class="sidebar">

        <div class="logo">
            SMART<span>ATTEND</span>
            <br>
            <small style="font-size:12px;color:#7d8aaa;">
                AI ATTENDANCE
            </small>
        </div>

        <a class="nav" href="/dashboard">
            🏠 Dashboard
        </a>

        <a class="nav" href="/students">
            👨‍🎓 Students
        </a>

        <a class="nav" href="/face">
            📷 Face Recognition
        </a>

        <a class="nav" href="/attendance">
            📋 Attendance
        </a>

        <a class="nav" href="/reports">
            📊 Reports
        </a>

        <a class="nav logout" href="/logout">
            🚪 Logout
        </a>

    </div>
    """



# =========================================================
# LOGIN
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "SmartAttend@2026":

            session["logged_in"] = True

            return redirect("/dashboard")

        return f"""
        {CSS}

        <div class="login-box">

            <h1>SMARTATTEND AI</h1>

            <p style="color:#ff7182;text-align:center;">
                Invalid username or password
            </p>

            <form method="post">

                <input
                    name="username"
                    placeholder="Username"
                    autocomplete="username"
                    required
                >

                <div style="position:relative;">

                    <input
                        id="loginPassword"
                        name="password"
                        type="password"
                        placeholder="Password"
                        autocomplete="current-password"
                        required
                        style="padding-right:50px;"
                    >

                    <span
                        id="loginEye"
                        onclick="toggleLoginPassword()"
                        style="
                            position:absolute;
                            right:15px;
                            top:50%;
                            transform:translateY(-50%);
                            cursor:pointer;
                            font-size:18px;
                            user-select:none;
                        "
                    >👁️</span>

                </div>

                <button style="width:100%;margin-top:15px;">
                    LOGIN
                </button>

            </form>

        </div>

        <script>
        function toggleLoginPassword() {{
            const password = document.getElementById("loginPassword");
            const eye = document.getElementById("loginEye");

            if (password.type === "password") {{
                password.type = "text";
                eye.innerHTML = "🙈";
            }} else {{
                password.type = "password";
                eye.innerHTML = "👁️";
            }}
        }}
        </script>
        """

    return f"""
    {CSS}

    <div class="login-box">

        <h1>SMARTATTEND AI</h1>

        <p style="text-align:center;color:#8995b5;">
            Face Recognition Attendance System
        </p>

        <form method="post">

            <input
                name="username"
                placeholder="Username"
                autocomplete="username"
                required
            >

            <div style="position:relative;">

                <input
                    id="loginPassword"
                    name="password"
                    type="password"
                    placeholder="Password"
                    autocomplete="current-password"
                    required
                    style="padding-right:50px;"
                >

                <span
                    id="loginEye"
                    onclick="toggleLoginPassword()"
                    style="
                        position:absolute;
                        right:15px;
                        top:50%;
                        transform:translateY(-50%);
                        cursor:pointer;
                        font-size:18px;
                        user-select:none;
                    "
                >👁️</span>

            </div>

            <button style="width:100%;margin-top:15px;">
                LOGIN
            </button>

        </form>

    </div>

    <script>
    function toggleLoginPassword() {{
        const password = document.getElementById("loginPassword");
        const eye = document.getElementById("loginEye");

        if (password.type === "password") {{
            password.type = "text";
            eye.innerHTML = "🙈";
        }} else {{
            password.type = "password";
            eye.innerHTML = "👁️";
        }}
    }}
    </script>
    """
# =========================================================
# LOGIN CHECK
# =========================================================

def logged_in():

    return session.get("logged_in", False)

# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not logged_in():
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM students"
    )

    total_students = cur.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute(
        """
        SELECT COUNT(DISTINCT student_id)
        FROM attendance
        WHERE date=?
        """,
        (today,)
    )

    present = cur.fetchone()[0]

    absent = max(
        total_students - present,
        0
    )

    percentage = 0

    if total_students > 0:

        percentage = round(
            (present / total_students) * 100,
            1
        )

    cur.execute(
        """
        SELECT
            students.name,
            students.roll_no,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        ORDER BY attendance.id DESC
        LIMIT 10
        """
    )

    rows = cur.fetchall()

    conn.close()

    # -----------------------------------------
    # RECENT ATTENDANCE TABLE
    # -----------------------------------------

    table = ""

    for index, row in enumerate(rows, start=1):

        table += f"""
        <tr>

            <td>{index}</td>

            <td>{row['name']}</td>

            <td>{row['roll_no']}</td>

            <td>{row['date']}</td>

            <td>{row['time']}</td>

            <td>
                <span class="badge">
                    {row['status']}
                </span>
            </td>

        </tr>
        """

    return f"""
    {CSS}
    {sidebar()}

    <div class="main">

        <div class="title">
            Dashboard
        </div>

        <div class="subtitle">
            AI Face Recognition Attendance Analytics
        </div>

        <div class="cards">

            <div class="card">

                <h3>TOTAL STUDENTS</h3>

                <div class="number">
                    {total_students}
                </div>

            </div>

            <div class="card">

                <h3>PRESENT TODAY</h3>

                <div class="number green">
                    {present}
                </div>

            </div>

            <div class="card">

                <h3>ABSENT TODAY</h3>

                <div class="number red">
                    {absent}
                </div>

            </div>

            <div class="card">

                <h3>ATTENDANCE</h3>

                <div class="number">
                    {percentage}%
                </div>

            </div>

        </div>

        <div class="panel">

            <h2>
                Recent Attendance
            </h2>

            <table>

                <tr>

                    <th>S.No</th>

                    <th>Name</th>

                    <th>Roll No</th>

                    <th>Date</th>

                    <th>Time</th>

                    <th>Status</th>

                </tr>

                {table}

            </table>

        </div>

    </div>
    """

# =========================================================
# STUDENTS
# =========================================================

@app.route("/students")
def students():

    if not logged_in():
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    search = request.args.get(
        "search",
        ""
    ).strip()

    if search:

        cur.execute(
            """
            SELECT *
            FROM students
            WHERE name LIKE ?
               OR roll_no LIKE ?
            ORDER BY id DESC
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        )

    else:

        cur.execute(
            """
            SELECT *
            FROM students
            ORDER BY id DESC
            """
        )

    student_rows = cur.fetchall()

    conn.close()

    rows = ""

    for student in student_rows:

        if student["face_registered"]:

            face_status = """
            <span class="badge">
                REGISTERED
            </span>
            """

        else:

            face_status = """
            <span class="red">
                NOT REGISTERED
            </span>
            """

        rows += f"""
        <tr>

            <td>{student['id']}</td>

            <td>{student['name']}</td>

            <td>{student['roll_no']}</td>

            <td>{student['department']}</td>

            <td>{student['year']}</td>

            <td>{face_status}</td>

            <td>

                <a
                    class="btn"
                    href="/register_face/{student['id']}"
                >
                    REGISTER FACE
                </a>

                <a
                    class="btn delete"
                    href="/delete_student/{student['id']}"
                    onclick="return confirm('Delete {student['name']} permanently?')"
                >
                    DELETE
                </a>

            </td>

        </tr>
        """        

    return f"""
    {CSS}
    {sidebar()}

    <div class="main">

        <div class="title">
            Student Management
        </div>

        <div class="subtitle">
            Manage registered students
        </div>

        <div class="panel">

            <h2>
                Add Student
            </h2>

            <form
                method="post"
                action="/add_student"
            >

                <div
                    style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;"
                >

                    <input
                        name="name"
                        placeholder="Student Name"
                        required
                    >

                    <input
                        name="roll_no"
                        placeholder="Roll Number"
                        required
                    >

                    <input
                        name="department"
                        placeholder="Branch / Department"
                        required
                    >

                    <input
                        name="year"
                        placeholder="Year"
                        required
                    >

                </div>

                <button type="submit">
                    + ADD STUDENT
                </button>

            </form>

        </div>

        <div class="panel">

            <h2>
                Registered Students
            </h2>
           
            <div style="margin:15px 0;">

    <a
        class="btn"
        href="/train"
        style="display:inline-block;"
    >
        ⚡ TRAIN MODEL
    </a>

</div>

            <form method="get">

                <input
                    class="search"
                    name="search"
                    value="{search}"
                    placeholder="Search name or roll number"
                >

                <button>
                    SEARCH
                </button>

            </form>

            <table>

                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Roll No</th>
                    <th>Department</th>
                    <th>Year</th>
                    <th>Face</th>
                    <th>ACTION</th>
                </tr>

                {rows}

            </table>

        </div>

    </div>
    """


# =========================================================
# DELETE STUDENT
# =========================================================

@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):

    if not logged_in():
        return redirect("/")

    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    conn = get_db()
    cur = conn.cursor()

    # Delete attendance records
    cur.execute(
        "DELETE FROM attendance WHERE student_id = ?",
        (student_id,)
    )

    # Delete student
    cur.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    # -----------------------------------------
    # DELETE FACE DATA
    # -----------------------------------------

    face_folder = os.path.join(
        BASE_DIR,
        "data",
        "faces",
        str(student_id)
    )

    if os.path.exists(face_folder):

        shutil.rmtree(
            face_folder
        )

    # -----------------------------------------
    # DELETE OLD MODEL
    # -----------------------------------------

    model_path = os.path.join(
        BASE_DIR,
        "models",
        "trainer.yml"
    )

    if os.path.exists(model_path):

        os.remove(
            model_path
        )

    # -----------------------------------------
    # RETRAIN REMAINING STUDENTS
    # -----------------------------------------

    train_script = os.path.join(
        BASE_DIR,
        "app",
        "train_model.py"
    )

    try:

        result = subprocess.run(
            [
                sys.executable,
                train_script
            ],
            capture_output=True,
            text=True
        )

        print(
            "DELETE + RETRAIN:"
        )

        print(
            result.stdout
        )

        if result.stderr:

            print(
                result.stderr
            )

    except Exception as e:

        print(
            "RETRAIN ERROR:",
            e
        )

    return redirect("/students")
# =========================================================
# REGISTER FACE
# =========================================================

@app.route("/register_face/<int:student_id>")
def register_face(student_id):

    if not logged_in():
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM students
        WHERE id=?
        """,
        (student_id,)
    )

    student = cur.fetchone()
    conn.close()

    if not student:
        return redirect("/students")

    return f"""
    {CSS}
    {sidebar()}

    <div class="main">

        <div class="title">
            Register Face
        </div>

        <div class="subtitle">
            Register face for {student['name']}
        </div>

        <div class="camera-box">

            <video
                id="camera"
                autoplay
                playsinline
                muted
            ></video>

            <div class="camera-overlay">

                <div
                    id="captureStatus"
                    class="recognition-name"
                >
                    Starting camera...
                </div>

            </div>

        </div>

        <div
            id="progress"
            class="status"
        >
            Preparing face registration...
        </div>

        <div class="camera-buttons">

            <button onclick="startCapture()">
                START FACE CAPTURE
            </button>

            <button
                class="stop"
                onclick="stopCamera()"
            >
                STOP
            </button>

        </div>

        <canvas
            id="canvas"
            style="display:none;"
        ></canvas>

    </div>

<script>

let stream = null;
let capturing = false;
let count = 0;

const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const statusBox = document.getElementById("captureStatus");
const progress = document.getElementById("progress");

async function startCapture() {{

    if (capturing) {{
        return;
    }}

    try {{

        stream = await navigator.mediaDevices.getUserMedia({{
            video: {{
                width: {{ideal: 1280}},
                height: {{ideal: 720}},
                facingMode: "user"
            }},
            audio: false
        }});

        video.srcObject = stream;

        await video.play();

        count = 0;
        capturing = true;

        statusBox.innerText = "LOOK AT CAMERA";
        progress.innerText = "Capturing 0 / 10";

        captureImages();

    }}
    catch(error) {{

        console.log(error);

        statusBox.innerText = "CAMERA ERROR";

        progress.innerText =
            "Camera permission denied or unavailable.";

    }}
}}

async function captureImages() {{

    if (!capturing || count >= 10) {{
        return;
    }}

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    const blob = await new Promise(resolve => {{

        canvas.toBlob(
            resolve,
            "image/jpeg",
            0.90
        );

    }});

    if (!blob) {{
        return;
    }}

    const formData = new FormData();

    formData.append(
        "frame",
        blob,
        "face.jpg"
    );

    const response = await fetch(
        "/save_face/{student['id']}",
        {{
            method: "POST",
            body: formData
        }}
    );

    const data = await response.json();

    if (data.success) {{

        count++;

        progress.innerText =
            "Capturing " + count + " / 10";

        statusBox.innerText =
            "FACE SAMPLE " + count + " SAVED";

        if (count < 10) {{

            setTimeout(
                captureImages,
                1000
            );

        }}
        else {{

            capturing = false;

            statusBox.innerText =
                "✓ FACE REGISTERED";

            progress.innerText =
                "10 / 10 samples completed";

            stopCamera();

        }}

    }}
    else {{

        statusBox.innerText =
            data.message || "Capture failed";

        setTimeout(
            captureImages,
            1000
        );

    }}
}}

function stopCamera() {{

    capturing = false;

    if (stream) {{

        stream
            .getTracks()
            .forEach(track => {{
                track.stop();
            }});

        stream = null;
    }}

    video.srcObject = null;
}}

</script>
    """
# =========================================================
# SAVE FACE SAMPLE
# =========================================================

@app.route("/save_face/<int:student_id>", methods=["POST"])
def save_face(student_id):

    if not logged_in():
        return jsonify({
            "success": False,
            "message": "Login required"
        })

    if "frame" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image received"
        })

    try:

        face_folder = os.path.join(
            BASE_DIR,
            "data",
            "faces",
            str(student_id)
        )

        os.makedirs(
            face_folder,
            exist_ok=True
        )

        existing = [
            f for f in os.listdir(face_folder)
            if f.lower().endswith(".jpg")
        ]

        count = len(existing) + 1

        file = request.files["frame"]

        file_path = os.path.join(
            face_folder,
            f"{count}.jpg"
        )

        file.save(file_path)

        if count >= 10:

            conn = get_db()
            cur = conn.cursor()

            cur.execute(
                """
                UPDATE students
                SET face_registered=1
                WHERE id=?
                """,
                (student_id,)
            )

            conn.commit()
            conn.close()

        return jsonify({
            "success": True,
            "count": count
        })

    except Exception as e:

        print("FACE SAVE ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        })
# =========================================================
# TRAIN MODEL
# =========================================================

@app.route("/train")
def train():

    if not logged_in():
        return redirect("/")

    try:

        result = subprocess.run(
            [
                sys.executable,
                os.path.join(
                    BASE_DIR,
                    "app",
                    "train_model.py"
                )
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:

            return f"""
            {CSS}
            {sidebar()}

            <div class="main">

                <div class="title">
                    Model Training
                </div>

                <div class="subtitle">
                    Face recognition model training completed
                </div>

                <div class="panel">

                    <h2>
                        ✓ TRAINING SUCCESSFUL
                    </h2>

                    <p>
                        The face recognition model has been updated.
                    </p>

                    <p>
                        You can now use Face Recognition.
                    </p>

                    <a
                        class="btn"
                        href="/face"
                    >
                        START FACE RECOGNITION
                    </a>

                    <a
                        class="btn"
                        href="/students"
                    >
                        BACK TO STUDENTS
                    </a>

                </div>

            </div>
            """

        else:

            return f"""
            {CSS}
            {sidebar()}

            <div class="main">

                <div class="title">
                    Model Training
                </div>

                <div class="panel">

                    <h2>
                        ❌ TRAINING FAILED
                    </h2>

                    <pre>{result.stderr}</pre>

                    <a
                        class="btn"
                        href="/students"
                    >
                        BACK
                    </a>

                </div>

            </div>
            """

    except Exception as e:

        return f"""
        {CSS}
        {sidebar()}

        <div class="main">

            <div class="title">
                Model Training
            </div>

            <div class="panel">

                <h2>
                    ❌ ERROR
                </h2>

                <pre>{str(e)}</pre>

                <a
                    class="btn"
                    href="/students"
                >
                    BACK
                </a>

            </div>

        </div>
        """
#=========================================================
# FACE RECOGNITION
# =========================================================

@app.route("/face")
def face():

    if not logged_in():
        return redirect("/")

    return f"""
    {CSS}
    {sidebar()}

    <div class="main">

        <div class="title">
            Face Recognition
        </div>

        <div class="subtitle">
            AI-powered live attendance
        </div>

        <div class="camera-box">

            <video
                id="camera"
                autoplay
                playsinline
                muted
            ></video>

            <div class="camera-overlay">

                <div
                    id="nameBox"
                    class="recognition-name"
                >
                    Starting camera...
                </div>

            </div>

        </div>

        <div class="camera-buttons">

            <button onclick="startCamera()">
                START CAMERA
            </button>

            <button
                class="stop"
                onclick="stopCamera()"
            >
                STOP CAMERA
            </button>

        </div>

        <div
            id="status"
            class="status"
        >
            Starting camera...
        </div>

        <canvas
            id="canvas"
            style="display:none;"
        ></canvas>

    </div>


<script>

let stream = null;
let timer = null;
let busy = false;

const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const nameBox = document.getElementById("nameBox");
const statusBox = document.getElementById("status");


async function startCamera() {{

    if (stream) {{
        return;
    }}

    try {{

        stream =
            await navigator.mediaDevices.getUserMedia({{
                video: {{
                    width: {{ideal: 1280}},
                    height: {{ideal: 720}},
                    facingMode: "user"
                }},
                audio: false
            }});

        video.srcObject = stream;

        await video.play();

        statusBox.innerText =
            "● CAMERA ACTIVE — Looking for face...";

        nameBox.innerText =
            "Scanning...";

        nameBox.style.color =
            "#62d9ff";

        nameBox.style.borderColor =
            "#62d9ff";

        if (timer) {{
            clearInterval(timer);
        }}

        timer =
            setInterval(recognizeFace, 500);

    }}
    catch(error) {{

        console.log(error);

        statusBox.innerText =
            "Camera permission denied or camera unavailable.";

        nameBox.innerText =
            "CAMERA ERROR";

        nameBox.style.color =
            "#ff7182";

        nameBox.style.borderColor =
            "#ff7182";
    }}
}}


function stopCamera() {{

    if (timer) {{

        clearInterval(timer);

        timer = null;
    }}

    if (stream) {{

        stream
            .getTracks()
            .forEach(track => {{
                track.stop();
            }});

        stream = null;
    }}

    video.srcObject = null;

    nameBox.innerText =
        "Camera stopped";

    nameBox.style.color =
        "#ffffff";

    nameBox.style.borderColor =
        "#ffffff";

    statusBox.innerText =
        "Camera stopped.";
}}


async function recognizeFace() {{

    if (
        !stream ||
        video.readyState < 2 ||
        busy
    ) {{
        return;
    }}

    busy = true;

    try {{

        canvas.width =
            video.videoWidth;

        canvas.height =
            video.videoHeight;

        if (
            canvas.width === 0 ||
            canvas.height === 0
        ) {{

            busy = false;

            return;
        }}

        const ctx =
            canvas.getContext("2d");

        ctx.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );

        const blob =
            await new Promise(resolve => {{

                canvas.toBlob(
                    resolve,
                    "image/jpeg",
                    0.85
                );

            }});

        if (!blob) {{

            busy = false;

            return;
        }}

        const formData =
            new FormData();

        formData.append(
            "frame",
            blob,
            "camera.jpg"
        );

        const response =
            await fetch(
                "/recognize",
                {{
                    method: "POST",
                    body: formData
                }}
            );

        const data =
            await response.json();

        if (data.recognized) {{

            nameBox.innerText =
                "✓ " + data.name;

            nameBox.style.color =
                "#42e8a0";

            nameBox.style.borderColor =
                "#42e8a0";

            statusBox.innerText =
                data.message +
                " | Match: " +
                data.distance;

        }}
        else {{

            nameBox.innerText =
                data.name || "Unknown";

            nameBox.style.color =
                "#ffcf5a";

            nameBox.style.borderColor =
                "#ffcf5a";

            statusBox.innerText =
                data.message ||
                "Face not recognized";
        }}

    }}
    catch(error) {{

        console.log(error);

        statusBox.innerText =
            "Recognition server error.";

    }}

    busy = false;
}}


// AUTO START CAMERA
window.addEventListener(
    "load",
    function() {{
        startCamera();
    }}
);

</script>
    """


# =========================================================
# RECOGNIZE FRAME
# =========================================================

LIVE_MATCHES = {}

# Liveness state
LIVENESS_STATE = {}


@app.route("/recognize", methods=["POST"])
def recognize():

    if not logged_in():

        return jsonify({
            "recognized": False,
            "name": "Login required",
            "message": "Please login"
        })

    global recognizer
    global LIVE_MATCHES
    global LIVENESS_STATE

    if recognizer is None:

        return jsonify({
            "recognized": False,
            "name": "Model Missing",
            "message": "Train the face model first"
        })

    if "frame" not in request.files:

        return jsonify({
            "recognized": False,
            "name": "No Frame",
            "message": "Camera frame not received"
        })

    try:

        # -----------------------------------------
        # READ CAMERA FRAME
        # -----------------------------------------

        file = request.files["frame"]

        data = file.read()

        image_array = np.frombuffer(
            data,
            np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            return jsonify({
                "recognized": False,
                "name": "Invalid Frame",
                "message": "Could not read camera"
            })

        # -----------------------------------------
        # GRAYSCALE
        # -----------------------------------------

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # -----------------------------------------
        # FACE DETECTOR
        # -----------------------------------------

        face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(80, 80)
        )

        # -----------------------------------------
        # NO FACE
        # -----------------------------------------

        if len(faces) == 0:

            LIVE_MATCHES.clear()
            LIVENESS_STATE.clear()

            return jsonify({
                "recognized": False,
                "name": "NO FACE",
                "message": "Move your face into the camera"
            })

        # -----------------------------------------
        # LARGEST FACE
        # -----------------------------------------

        x, y, w, h = max(
            faces,
            key=lambda rect: rect[2] * rect[3]
        )

        face_img = gray[
            y:y + h,
            x:x + w
        ]

        face_img = cv2.resize(
            face_img,
            (200, 200)
        )

                # -----------------------------------------
        # FACE RECOGNITION
        # -----------------------------------------

        student_id, distance = recognizer.predict(
            face_img
        )

        distance = round(
            float(distance),
            2
        )

        # -----------------------------------------
        # UNKNOWN FACE
        # -----------------------------------------

        if distance >= THRESHOLD:

            LIVE_MATCHES.clear()
            LIVENESS_STATE.clear()

            return jsonify({

                "recognized": False,

                "name":
                    "UNKNOWN",

                "message":
                    "Face not registered",

                "distance":
                    distance

            })

        # -----------------------------------------
        # GET STUDENT
        # -----------------------------------------

        conn = get_db()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, roll_no
            FROM students
            WHERE id=?
            """,
            (student_id,)
        )

        student = cur.fetchone()

        conn.close()

        if not student:

            LIVE_MATCHES.clear()
            LIVENESS_STATE.clear()

            return jsonify({
                "recognized": False,
                "name": "UNKNOWN",
                "message": "Student not found",
                "distance": distance
            })

        # -----------------------------------------
        # PERSON CORRECTNESS
        # 3 CONSECUTIVE MATCHES
        # -----------------------------------------

        sid = student["id"]

        LIVE_MATCHES[sid] = (
            LIVE_MATCHES.get(sid, 0) + 1
        )

        match_count = LIVE_MATCHES[sid]

        # -----------------------------------------
        # NOT YET CONFIRMED
        # -----------------------------------------

        if match_count < 3:

            return jsonify({

                "recognized": False,

                "name":
                    student["name"],

                "roll_no":
                    student["roll_no"],

                "message":
                    "Checking person... "
                    + str(match_count)
                    + "/3",

                "distance":
                    distance

            })

        # -----------------------------------------
        # PERSON CONFIRMED
        # START LIVENESS
        # -----------------------------------------

        if sid not in LIVENESS_STATE:

            LIVENESS_STATE[sid] = {

                "open_seen": False,

                "closed_seen": False

            }

            return jsonify({

                "recognized": False,

                "name":
                    student["name"],

                "roll_no":
                    student["roll_no"],

                "message":
                    "✓ PERSON CONFIRMED | BLINK ONCE",

                "distance":
                    distance

            })

               # -----------------------------------------
        # SIMPLE BLINK / LIVENESS DETECTION
        # -----------------------------------------

        state = LIVENESS_STATE[sid]

        # Face brightness inside upper-face region
        eye_region = gray[
            y:y + int(h * 0.55),
            x:x + w
        ]

        if eye_region.size == 0:

            return jsonify({

                "recognized": False,

                "name":
                    student["name"],

                "roll_no":
                    student["roll_no"],

                "message":
                    "LIVE CHECK | Adjust your face",

                "distance":
                    distance

            })

        # -----------------------------------------
        # EYE DETECTION
        # -----------------------------------------

        eye_detector = cv2.CascadeClassifier(

            cv2.data.haarcascades +
            "haarcascade_eye_tree_eyeglasses.xml"

        )

        eyes = eye_detector.detectMultiScale(

            eye_region,

            scaleFactor=1.1,

            minNeighbors=3,

            minSize=(15, 15)

        )

        # -----------------------------------------
        # OPEN EYES
        # -----------------------------------------

        if len(eyes) >= 1:

            # If eyes are open after being closed,
            # blink is completed.

            if (
                state["open_seen"]
                and
                state["closed_seen"]
            ):

                success, message = mark_attendance(
                    student["id"]
                )

                LIVE_MATCHES.clear()
                LIVENESS_STATE.clear()

                return jsonify({

                    "recognized": True,

                    "name":
                        student["name"],

                    "roll_no":
                        student["roll_no"],

                    "message":
                        "✓ LIVE VERIFIED | "
                        + message,

                    "distance":
                        distance

                })

            # First open-eye detection

            state["open_seen"] = True

            return jsonify({

                "recognized": False,

                "name":
                    student["name"],

                "roll_no":
                    student["roll_no"],

                "message":
                    "LIVE CHECK | Blink once",

                "distance":
                    distance

            })

        # -----------------------------------------
        # EYES NOT DETECTED
        # -----------------------------------------

        else:

            if state["open_seen"]:

                state["closed_seen"] = True

                return jsonify({

                    "recognized": False,

                    "name":
                        student["name"],

                    "roll_no":
                        student["roll_no"],

                    "message":
                        "LIVE CHECK | Eyes closed detected",

                    "distance":
                        distance

                })

        # -----------------------------------------
        # WAITING
        # -----------------------------------------

        return jsonify({

            "recognized": False,

            "name":
                student["name"],

            "roll_no":
                student["roll_no"],

            "message":
                "LIVE CHECK | Blink once",

            "distance":
                distance

        })

    except Exception as e:

        print(
            "RECOGNITION ERROR:",
            e
        )

        return jsonify({

            "recognized": False,

            "name": "ERROR",

            "message": str(e)

        })
# =========================================================
# ATTENDANCE
# =========================================================

@app.route("/attendance")
def attendance():

    if not logged_in():
        return redirect("/")

    conn = get_db()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            attendance.id,
            students.name,
            students.roll_no,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        ORDER BY attendance.id DESC
        """
    )

    rows = cur.fetchall()

    conn.close()

    table = ""

    for row in rows:

        table += f"""
        <tr>

            <td>{row['id']}</td>

            <td>{row['name']}</td>

            <td>{row['roll_no']}</td>

            <td>{row['date']}</td>

            <td>{row['time']}</td>

            <td>

                <span class="badge">

                    {row['status']}

                </span>

            </td>

        </tr>
        """

    return f"""
    {CSS}

    {sidebar()}

    <div class="main">

        <div class="title">
            Attendance
        </div>

        <div class="subtitle">
            Complete attendance records
        </div>

        <div class="panel">

            <table>

                <tr>

                    <th>ID</th>

                    <th>Name</th>

                    <th>Roll No</th>

                    <th>Date</th>

                    <th>Time</th>

                    <th>Status</th>

                </tr>

                {table}

            </table>

        </div>

    </div>
    """
# =========================================================
# REPORTS
# =========================================================

@app.route("/reports")
def reports():

    if not logged_in():
        return redirect("/")

    selected_date = request.args.get(
        "date",
        datetime.now().strftime("%Y-%m-%d")
    )

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            students.name,
            students.roll_no,
            students.department,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        WHERE attendance.date=?
        ORDER BY attendance.time DESC
        """,
        (selected_date,)
    )

    rows = cur.fetchall()

    conn.close()

    table = ""

    for row in rows:

        table += f"""
        <tr>

            <td>{row['name']}</td>

            <td>{row['roll_no']}</td>

            <td>{row['department']}</td>

            <td>{row['date']}</td>

            <td>{row['time']}</td>

            <td>{row['status']}</td>

        </tr>
        """

    return f"""
    {CSS}
    {sidebar()}

    <div class="main">

        <div class="title">
            Reports
        </div>

        <div class="subtitle">
            Attendance reports by date
        </div>

        <div class="panel">

            <form method="get">

                <input
                    type="date"
                    name="date"
                    value="{selected_date}"
                    style="max-width:250px;"
                >

                <button>
                    SHOW REPORT
                </button>

                <a
                    class="btn"
                    href="/export?date={selected_date}"
                >
                    EXPORT CSV
                </a>

            </form>

        </div>

        <div class="panel">

            <table>

                <tr>
                    <th>Name</th>
                    <th>Roll No</th>
                    <th>Department</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                </tr>

                {table}

            </table>

        </div>

    </div>
    """


# =========================================================
# EXPORT CSV
# =========================================================

@app.route("/export")
def export():

    if not logged_in():
        return redirect("/")

    selected_date = request.args.get(
        "date",
        datetime.now().strftime("%Y-%m-%d")
    )

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            students.name,
            students.roll_no,
            students.department,
            students.year,
            attendance.date,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        WHERE attendance.date=?
        ORDER BY attendance.time
        """,
        (selected_date,)
    )

    rows = cur.fetchall()

    conn.close()

    output = []

    output.append(
        "Name,Roll No,Department,Year,Date,Time,Status"
    )

    for row in rows:

        output.append(
            f"{row['name']},"
            f"{row['roll_no']},"
            f"{row['department']},"
            f"{row['year']},"
            f"{row['date']},"
            f"{row['time']},"
            f"{row['status']}"
        )

    csv_data = "\n".join(output)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment;filename=attendance_{selected_date}.csv"
        }
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================================================
# ADD STUDENT
# =========================================================

@app.route("/add_student", methods=["POST"])
def add_student():

    if not logged_in():
        return redirect("/")

    name = request.form.get(
        "name",
        ""
    ).strip()

    roll_no = request.form.get(
        "roll_no",
        ""
    ).strip()

    department = request.form.get(
        "department",
        ""
    ).strip()

    year = request.form.get(
        "year",
        ""
    ).strip()

    # -----------------------------------------
    # VALIDATION
    # -----------------------------------------

    if (
        not name
        or not roll_no
        or not department
        or not year
    ):

        return redirect(
            "/students?error=Please+fill+all+fields"
        )

    conn = get_db()

    cur = conn.cursor()

    try:

        # -------------------------------------
        # CHECK DUPLICATE ROLL NUMBER
        # -------------------------------------

        cur.execute(
            """
            SELECT id, name
            FROM students
            WHERE roll_no = ?
            """,
            (roll_no,)
        )

        existing = cur.fetchone()

        if existing:

            conn.close()

            return redirect(
                "/students?error=Roll+number+already+exists"
            )

        # -------------------------------------
        # INSERT STUDENT
        # -------------------------------------

        cur.execute(
            """
            INSERT INTO students
            (
                name,
                roll_no,
                department,
                year,
                face_registered
            )
            VALUES (?, ?, ?, ?, 0)
            """,
            (
                name,
                roll_no,
                department,
                year
            )
        )

        conn.commit()

        new_student_id = cur.lastrowid

        conn.close()

        print(
            "STUDENT ADDED:",
            new_student_id,
            name
        )

        return redirect(
            "/students?success=Student+added+successfully"
        )

    except sqlite3.IntegrityError as e:

        conn.rollback()

        conn.close()

        print(
            "ADD STUDENT DATABASE ERROR:",
            e
        )

        return redirect(
            "/students?error=Could+not+add+student"
        )

    except Exception as e:

        conn.rollback()

        conn.close()

        print(
            "ADD STUDENT ERROR:",
            e
        )

        return redirect(
            "/students?error=Unexpected+error"
        )
# =========================================================
# SERVER
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
