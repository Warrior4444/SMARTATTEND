import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "smartattend.db"
)


def get_connection():
    return sqlite3.connect(DB_PATH)


class StudentManager:

    def __init__(self, parent):

        self.parent = parent

        self.window = tk.Toplevel(parent)
        self.window.title("Student Management | SMARTATTEND AI")
        self.window.geometry("1100x700")
        self.window.minsize(1000, 650)
        self.window.configure(bg="#0f172a")

        self.create_style()
        self.create_ui()
        self.load_students()

    # ==================================================
    # STYLE
    # ==================================================

    def create_style(self):

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
            font=("Segoe UI", 9, "bold"),
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
    # MAIN UI
    # ==================================================

    def create_ui(self):

        # ---------------- HEADER ----------------

        header = tk.Frame(
            self.window,
            bg="#111827",
            height=90
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(
            header,
            bg="#111827"
        )

        title_frame.pack(
            side="left",
            padx=30,
            pady=18
        )

        tk.Label(
            title_frame,
            text="Student Management",
            bg="#111827",
            fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Manage student profiles and face registration",
            bg="#111827",
            fg="#64748b",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            header,
            text="SMARTATTEND AI",
            bg="#111827",
            fg="#3b82f6",
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="right",
            padx=30
        )

        # ---------------- FORM ----------------

        form = tk.Frame(
            self.window,
            bg="#1e293b"
        )

        form.pack(
            fill="x",
            padx=30,
            pady=20
        )

        self.name_var = tk.StringVar()
        self.roll_var = tk.StringVar()
        self.dept_var = tk.StringVar()
        self.year_var = tk.StringVar()

        # Row 1

        tk.Label(
            form,
            text="STUDENT NAME",
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(15, 5)
        )

        tk.Label(
            form,
            text="ROLL NUMBER",
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold")
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=20,
            pady=(15, 5)
        )

        # Row 2

        name_entry = tk.Entry(
            form,
            textvariable=self.name_var,
            bg="#0f172a",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Segoe UI", 11)
        )

        name_entry.grid(
            row=1,
            column=0,
            padx=20,
            ipady=8,
            sticky="ew"
        )

        roll_entry = tk.Entry(
            form,
            textvariable=self.roll_var,
            bg="#0f172a",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Segoe UI", 11)
        )

        roll_entry.grid(
            row=1,
            column=1,
            padx=20,
            ipady=8,
            sticky="ew"
        )

        # Row 3

        tk.Label(
            form,
            text="BRANCH / DEPARTMENT",
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold")
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=20,
            pady=(15, 5)
        )

        tk.Label(
            form,
            text="YEAR",
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold")
        ).grid(
            row=2,
            column=1,
            sticky="w",
            padx=20,
            pady=(15, 5)
        )

        self.dept_box = ttk.Combobox(
            form,
            textvariable=self.dept_var,
            values=(
                "ECE",
                "CSE",
                "EEE",
                "MECH",
                "CIVIL",
                "AI & DS",
                "AI & ML",
                "IT"
            ),
            state="readonly",
            font=("Segoe UI", 10)
        )

        self.dept_box.grid(
            row=3,
            column=0,
            padx=20,
            ipady=7,
            sticky="ew"
        )

        self.year_box = ttk.Combobox(
            form,
            textvariable=self.year_var,
            values=(
                "1st Year",
                "2nd Year",
                "3rd Year",
                "4th Year"
            ),
            state="readonly",
            font=("Segoe UI", 10)
        )

        self.year_box.grid(
            row=3,
            column=1,
            padx=20,
            ipady=7,
            sticky="ew"
        )

        # Add button

        tk.Button(
            form,
            text="+  ADD STUDENT",
            command=self.add_student,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        ).grid(
            row=1,
            column=2,
            rowspan=3,
            padx=20,
            ipadx=25,
            ipady=12
        )

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # ---------------- SEARCH BAR ----------------

        search_frame = tk.Frame(
            self.window,
            bg="#0f172a"
        )

        search_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 12)
        )

        tk.Label(
            search_frame,
            text="STUDENTS",
            bg="#0f172a",
            fg="white",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")

        self.search_var = tk.StringVar()

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg="#1e293b",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Segoe UI", 10),
            width=25
        )

        search_entry.pack(
            side="right",
            ipady=7,
            padx=(8, 0)
        )

        tk.Button(
            search_frame,
            text="SEARCH",
            command=self.search_students,
            bg="#334155",
            fg="white",
            activebackground="#475569",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        ).pack(
            side="right",
            ipadx=10,
            ipady=5
        )

        # ---------------- TABLE ----------------

        table_frame = tk.Frame(
            self.window,
            bg="#1e293b"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 25)
        )

        columns = (
            "id",
            "name",
            "roll",
            "department",
            "year",
            "face"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "name": "STUDENT NAME",
            "roll": "ROLL NUMBER",
            "department": "BRANCH",
            "year": "YEAR",
            "face": "FACE STATUS"
        }

        widths = {
            "id": 60,
            "name": 230,
            "roll": 170,
            "department": 150,
            "year": 130,
            "face": 170
        }

        for column in columns:

            self.table.heading(
                column,
                text=headings[column]
            )

            self.table.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # ==================================================
    # ADD STUDENT
    # ==================================================

    def add_student(self):

        name = self.name_var.get().strip()
        roll = self.roll_var.get().strip()
        department = self.dept_var.get().strip()
        year = self.year_var.get().strip()

        if not name or not roll or not department or not year:

            messagebox.showwarning(
                "Missing Information",
                "Please fill all student details."
            )

            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO students
                (name, roll_no, department, year)
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    roll,
                    department,
                    year
                )
            )

            connection.commit()
            connection.close()

            messagebox.showinfo(
                "Student Added",
                f"{name} has been added successfully."
            )

            self.name_var.set("")
            self.roll_var.set("")
            self.dept_var.set("")
            self.year_var.set("")

            self.load_students()

        except sqlite3.IntegrityError:

            messagebox.showerror(
                "Duplicate Roll Number",
                "This roll number already exists."
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error)
            )

    # ==================================================
    # LOAD STUDENTS
    # ==================================================

    def load_students(self):

        self.display_students("")

    # ==================================================
    # SEARCH
    # ==================================================

    def search_students(self):

        search_text = (
            self.search_var
            .get()
            .strip()
        )

        self.display_students(search_text)

    # ==================================================
    # DISPLAY
    # ==================================================

    def display_students(self, search_text):

        for item in self.table.get_children():

            self.table.delete(item)

        connection = get_connection()
        cursor = connection.cursor()

        if search_text:

            cursor.execute(
                """
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
                """,
                (
                    "%" + search_text + "%",
                    "%" + search_text + "%",
                    "%" + search_text + "%"
                )
            )

        else:

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    roll_no,
                    department,
                    year,
                    face_registered
                FROM students
                ORDER BY id DESC
                """
            )

        students = cursor.fetchall()

        connection.close()

        for student in students:

            face_status = (
                "●  REGISTERED"
                if student[5]
                else "○  NOT REGISTERED"
            )

            self.table.insert(
                "",
                "end",
                values=(
                    student[0],
                    student[1],
                    student[2],
                    student[3],
                    student[4],
                    face_status
                )
            )


if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()

    StudentManager(root)

    root.mainloop()