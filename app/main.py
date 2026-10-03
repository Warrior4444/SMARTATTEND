import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import sqlite3
import subprocess
from datetime import datetime


# ======================================================
# PROJECT PATHS
# ======================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "smartattend.db"
)

TRAIN_FILE = os.path.join(
    BASE_DIR,
    "app",
    "train_model.py"
)

ATTENDANCE_FILE = os.path.join(
    BASE_DIR,
    "app",
    "live_attendance.py"
)


# Allow imports from project folder
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


from app.students import StudentManager
from app.face_capture import FaceCapture
from app.reports import Reports



# ======================================================
# SMART ATTEND AI
# ======================================================

class SmartAttendAI:

    def __init__(self, root):

        self.root = root

        self.root.title("SMARTATTEND AI")

        self.root.geometry("1200x700")

        self.root.minsize(
            1050,
            650
        )

        self.root.configure(
            bg="#0f172a"
        )

        self.setup_style()

        self.create_sidebar()

        self.create_main_area()


    # ==================================================
    # DATABASE
    # ==================================================

    def get_dashboard_data(self):

        connection = sqlite3.connect(
            DB_PATH
        )

        cursor = connection.cursor()


        # Total students
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            """
        )

        total_students = cursor.fetchone()[0]


        # Today's date
        today = datetime.now().strftime(
            "%Y-%m-%d"
        )


        # Present today
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
            AND status = 'Present'
            """,
            (today,)
        )

        present_today = cursor.fetchone()[0]


        # Absent today
        absent_today = max(
            total_students - present_today,
            0
        )


        # Attendance percentage
        if total_students > 0:

            attendance_percentage = round(
                (present_today / total_students) * 100
            )

        else:

            attendance_percentage = 0


        # Recent attendance
        cursor.execute(
            """
            SELECT
                attendance.id,
                students.name,
                students.roll_no,
                attendance.date,
                attendance.time,
                attendance.status
            FROM attendance
            INNER JOIN students
            ON attendance.student_id = students.id
            ORDER BY attendance.id DESC
            LIMIT 50
            """
        )

        attendance_records = cursor.fetchall()


        connection.close()


        return (
            total_students,
            present_today,
            absent_today,
            attendance_percentage,
            attendance_records
        )


    # ==================================================
    # STYLE
    # ==================================================

    def setup_style(self):

        style = ttk.Style()

        style.theme_use("clam")


        style.configure(
            "Treeview",
            background="#1e293b",
            foreground="#e2e8f0",
            fieldbackground="#1e293b",
            rowheight=42,
            borderwidth=0,
            font=("Segoe UI", 10)
        )


        style.configure(
            "Treeview.Heading",
            background="#334155",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )


        style.map(
            "Treeview",
            background=[
                ("selected", "#2563eb")
            ],
            foreground=[
                ("selected", "white")
            ]
        )


    # ==================================================
    # SIDEBAR
    # ==================================================

    def create_sidebar(self):

        sidebar = tk.Frame(
            self.root,
            bg="#111827",
            width=245
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)


        tk.Label(
            sidebar,
            text="SMARTATTEND",
            bg="#111827",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(
            pady=(35, 2)
        )


        tk.Label(
            sidebar,
            text="AI ATTENDANCE SYSTEM",
            bg="#111827",
            fg="#64748b",
            font=("Segoe UI", 8, "bold")
        ).pack(
            pady=(0, 35)
        )


        self.create_menu_button(
            sidebar,
            "⌂   Dashboard",
            self.show_dashboard
        )


        self.create_menu_button(
            sidebar,
            "👨‍🎓  Students",
            self.open_students
        )


        self.create_menu_button(
            sidebar,
            "📷  Face Capture",
            self.face_capture
        )


        self.create_menu_button(
            sidebar,
            "🧠  Train Model",
            self.train_model
        )


        self.create_menu_button(
            sidebar,
            "✓   Attendance",
            self.attendance
        )


        self.create_menu_button(
            sidebar,
            "📊  Reports",
            self.reports
        )


        # Bottom status
        bottom = tk.Frame(
            sidebar,
            bg="#111827"
        )

        bottom.pack(
            side="bottom",
            fill="x",
            pady=25
        )


        tk.Label(
            bottom,
            text="●  SYSTEM ONLINE",
            bg="#111827",
            fg="#22c55e",
            font=("Segoe UI", 9, "bold")
        ).pack()


        tk.Label(
            bottom,
            text="SmartAttend AI  •  v1.0",
            bg="#111827",
            fg="#64748b",
            font=("Segoe UI", 8)
        ).pack(
            pady=(5, 0)
        )


    # ==================================================
    # MENU BUTTON
    # ==================================================

    def create_menu_button(
        self,
        parent,
        text,
        command
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            anchor="w",
            padx=25,
            bg="#111827",
            fg="#cbd5e1",
            activebackground="#1e293b",
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
            cursor="hand2"
        )

        button.pack(
            fill="x",
            pady=2,
            ipady=10
        )


    # ==================================================
    # MAIN AREA
    # ==================================================

    def create_main_area(self):

        self.main = tk.Frame(
            self.root,
            bg="#0f172a"
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.show_dashboard()


    # ==================================================
    # CLEAR MAIN
    # ==================================================

    def clear_main(self):

        for widget in self.main.winfo_children():

            widget.destroy()


    # ==================================================
    # DASHBOARD
    # ==================================================

    def show_dashboard(self):

        self.clear_main()


        (
            total_students,
            present_today,
            absent_today,
            attendance_percentage,
            attendance_records
        ) = self.get_dashboard_data()


        # HEADER
        header = tk.Frame(
            self.main,
            bg="#0f172a"
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(30, 10)
        )


        tk.Label(
            header,
            text="Dashboard",
            bg="#0f172a",
            fg="white",
            font=("Segoe UI", 27, "bold")
        ).pack(
            side="left"
        )


        tk.Label(
            header,
            text="Smart Attendance Management",
            bg="#0f172a",
            fg="#64748b",
            font=("Segoe UI", 10)
        ).pack(
            side="left",
            padx=18,
            pady=(12, 0)
        )


        # DASHBOARD CARDS
        cards = tk.Frame(
            self.main,
            bg="#0f172a"
        )

        cards.pack(
            fill="x",
            padx=30,
            pady=15
        )


        self.create_card(
            cards,
            "TOTAL STUDENTS",
            str(total_students),
            "#3b82f6"
        )


        self.create_card(
            cards,
            "PRESENT TODAY",
            str(present_today),
            "#22c55e"
        )


        self.create_card(
            cards,
            "ABSENT TODAY",
            str(absent_today),
            "#ef4444"
        )


        self.create_card(
            cards,
            "ATTENDANCE",
            f"{attendance_percentage}%",
            "#a855f7"
        )


        # RECENT ATTENDANCE
        section = tk.Frame(
            self.main,
            bg="#0f172a"
        )

        section.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )


        tk.Label(
            section,
            text="Recent Attendance",
            bg="#0f172a",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            pady=(0, 12)
        )


        table_frame = tk.Frame(
            section,
            bg="#1e293b"
        )

        table_frame.pack(
            fill="both",
            expand=True
        )


        # TABLE
        columns = (
            "sno",
            "name",
            "roll",
            "date",
            "time",
            "status"
        )


        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )


        headings = {
            "sno": "S.NO",
            "name": "STUDENT",
            "roll": "ROLL NO",
            "date": "DATE",
            "time": "TIME",
            "status": "STATUS"
        }


        widths = {
            "sno": 70,
            "name": 200,
            "roll": 140,
            "date": 130,
            "time": 120,
            "status": 120
        }


        for column in columns:

            table.heading(
                column,
                text=headings[column]
            )

            table.column(
                column,
                width=widths[column],
                anchor="center"
            )


        # INSERT RECORDS
        for index, record in enumerate(
            attendance_records,
            start=1
        ):

            table.insert(
                "",
                "end",
                values=(
                    index,
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5]
                )
            )


        table.pack(
            fill="both",
            expand=True
        )


        # REFRESH BUTTON
        refresh_button = tk.Button(
            section,
            text="↻  REFRESH DASHBOARD",
            command=self.show_dashboard,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )


        refresh_button.pack(
            anchor="e",
            pady=(10, 0),
            ipadx=12,
            ipady=5
        )


    # ==================================================
    # DASHBOARD CARD
    # ==================================================

    def create_card(
        self,
        parent,
        title,
        value,
        accent
    ):

        card = tk.Frame(
            parent,
            bg="#1e293b",
            height=120
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )


        tk.Frame(
            card,
            bg=accent,
            width=5
        ).pack(
            side="left",
            fill="y"
        )


        content = tk.Frame(
            card,
            bg="#1e293b"
        )

        content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )


        tk.Label(
            content,
            text=title,
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w"
        )


        tk.Label(
            content,
            text=value,
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 25, "bold")
        ).pack(
            anchor="w",
            pady=(5, 0)
        )


    # ==================================================
    # STUDENTS
    # ==================================================

    def open_students(self):

        StudentManager(
            self.root
        )


    # ==================================================
    # FACE CAPTURE
    # ==================================================

    def face_capture(self):

        FaceCapture(
            self.root
        )


    # ==================================================
    # TRAIN MODEL
    # ==================================================

    def train_model(self):

        if not os.path.exists(TRAIN_FILE):

            messagebox.showerror(
                "Training Error",
                "train_model.py file not found."
            )

            return


        try:

            result = subprocess.run(
                [sys.executable, TRAIN_FILE],
                capture_output=True,
                text=True
            )


            if result.returncode == 0:

                messagebox.showinfo(
                    "Training Completed",
                    "AI model trained successfully!\n\n"
                    "The trained model is ready for face recognition."
                )

            else:

                error_message = result.stderr.strip()

                if not error_message:
                    error_message = result.stdout.strip()

                messagebox.showerror(
                    "Training Error",
                    error_message
                )


        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )


    # ==================================================
    # LIVE ATTENDANCE
    # ==================================================

    def attendance(self):

        if not os.path.exists(ATTENDANCE_FILE):

            messagebox.showerror(
                "Attendance Error",
                "live_attendance.py file not found."
            )

            return


        model_path = os.path.join(
            BASE_DIR,
            "models",
            "trainer.yml"
        )


        if not os.path.exists(model_path):

            messagebox.showwarning(
                "Model Not Found",
                "Please train the AI model first."
            )

            return


        try:

            subprocess.Popen(
                [sys.executable, ATTENDANCE_FILE]
            )


        except Exception as error:

            messagebox.showerror(
                "Attendance Error",
                str(error)
            )


        # ==================================================
    # REPORTS
    # ==================================================
 
    def reports(self):

        Reports(self.root)


# ======================================================
# START APPLICATION
# ======================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = SmartAttendAI(
        root
    )

    root.mainloop()