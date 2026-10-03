import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "smartattend.db"
)


class Reports:

    def __init__(self, parent):

        self.parent = parent

        self.window = tk.Toplevel(parent)

        self.window.title(
            "Attendance Reports - SmartAttend AI"
        )

        self.window.geometry(
            "1150x720"
        )

        self.window.minsize(
            1000,
            650
        )

        self.window.configure(
            bg="#0f172a"
        )

        self.create_ui()

        self.load_reports()


    # ==================================================
    # UI
    # ==================================================

    def create_ui(self):

        # HEADER

        header = tk.Frame(
            self.window,
            bg="#111827",
            height=80
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)


        tk.Label(
            header,
            text="Attendance Reports",
            bg="#111827",
            fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(
            side="left",
            padx=30,
            pady=20
        )


        tk.Label(
            header,
            text="SMARTATTEND AI",
            bg="#111827",
            fg="#64748b",
            font=("Segoe UI", 9, "bold")
        ).pack(
            side="right",
            padx=30
        )


        # ==================================================
        # SUMMARY CARDS
        # ==================================================

        cards = tk.Frame(
            self.window,
            bg="#0f172a"
        )

        cards.pack(
            fill="x",
            padx=30,
            pady=(20, 10)
        )


        self.total_card = self.create_card(
            cards,
            "TOTAL RECORDS",
            "0",
            "#3b82f6"
        )


        self.present_card = self.create_card(
            cards,
            "PRESENT",
            "0",
            "#22c55e"
        )


        self.absent_card = self.create_card(
            cards,
            "ABSENT",
            "0",
            "#ef4444"
        )


        self.percentage_card = self.create_card(
            cards,
            "ATTENDANCE",
            "0%",
            "#a855f7"
        )


        # ==================================================
        # SEARCH / CONTROLS
        # ==================================================

        controls = tk.Frame(
            self.window,
            bg="#1e293b"
        )

        controls.pack(
            fill="x",
            padx=30,
            pady=15
        )


        # SEARCH

        tk.Label(
            controls,
            text="Search Student:",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="left",
            padx=(15, 8)
        )


        self.search_var = tk.StringVar()


        search_entry = tk.Entry(
            controls,
            textvariable=self.search_var,
            bg="#0f172a",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Segoe UI", 10),
            width=20
        )

        search_entry.pack(
            side="left",
            ipady=7,
            padx=5
        )


        tk.Button(
            controls,
            text="SEARCH",
            command=self.search_reports,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        ).pack(
            side="left",
            padx=6,
            ipadx=8,
            ipady=5
        )


        # DATE

        tk.Label(
            controls,
            text="Date:",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Segoe UI", 10, "bold")
        ).pack(
            side="left",
            padx=(12, 5)
        )


        self.date_var = tk.StringVar()


        date_entry = tk.Entry(
            controls,
            textvariable=self.date_var,
            bg="#0f172a",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Segoe UI", 10),
            width=12
        )

        date_entry.pack(
            side="left",
            ipady=7,
            padx=5
        )


        tk.Button(
            controls,
            text="DATE FILTER",
            command=self.filter_by_date,
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        ).pack(
            side="left",
            padx=5,
            ipadx=7,
            ipady=5
        )


        # SHOW ALL

        tk.Button(
            controls,
            text="SHOW ALL",
            command=self.load_reports,
            bg="#475569",
            fg="white",
            activebackground="#334155",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        ).pack(
            side="left",
            padx=5,
            ipadx=8,
            ipady=5
        )


        # EXPORT

        tk.Button(
            controls,
            text="EXPORT CSV",
            command=self.export_csv,
            bg="#16a34a",
            fg="white",
            activebackground="#15803d",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        ).pack(
            side="right",
            padx=15,
            ipadx=10,
            ipady=5
        )


        # ==================================================
        # TABLE
        # ==================================================

        table_frame = tk.Frame(
            self.window,
            bg="#1e293b"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 30)
        )


        columns = (
            "sno",
            "name",
            "roll",
            "department",
            "date",
            "time",
            "status"
        )


        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )


        headings = {
            "sno": "S.NO",
            "name": "STUDENT",
            "roll": "ROLL NO",
            "department": "DEPARTMENT",
            "date": "DATE",
            "time": "TIME",
            "status": "STATUS"
        }


        widths = {
            "sno": 60,
            "name": 180,
            "roll": 130,
            "department": 130,
            "date": 120,
            "time": 110,
            "status": 100
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
    # SUMMARY CARD
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
            height=100
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
            padx=15,
            pady=10
        )


        tk.Label(
            content,
            text=title,
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w"
        )


        value_label = tk.Label(
            content,
            text=value,
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 22, "bold")
        )


        value_label.pack(
            anchor="w",
            pady=(4, 0)
        )


        return value_label


    # ==================================================
    # LOAD REPORTS
    # ==================================================

    def load_reports(self):

        self.search_var.set("")

        self.date_var.set("")

        self.fetch_reports()


    # ==================================================
    # SEARCH
    # ==================================================

    def search_reports(self):

        search_text = (
            self.search_var
            .get()
            .strip()
        )


        self.fetch_reports(
            search_text
        )


    # ==================================================
    # DATE FILTER
    # ==================================================

    def filter_by_date(self):

        date_text = (
            self.date_var
            .get()
            .strip()
        )


        if not date_text:

            messagebox.showwarning(
                "Date Required",
                "Please enter a date.\n\n"
                "Format: YYYY-MM-DD\n"
                "Example: 2026-10-02"
            )

            return


        connection = sqlite3.connect(
            DB_PATH
        )

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
                students.name,
                students.roll_no,
                students.department,
                attendance.date,
                attendance.time,
                attendance.status
            FROM attendance
            INNER JOIN students
            ON attendance.student_id = students.id
            WHERE attendance.date = ?
            ORDER BY attendance.id DESC
            """,
            (date_text,)
        )


        records = cursor.fetchall()

        connection.close()


        self.update_table(
            records
        )


    # ==================================================
    # FETCH DATABASE DATA
    # ==================================================

    def fetch_reports(
        self,
        search_text=""
    ):

        connection = sqlite3.connect(
            DB_PATH
        )

        cursor = connection.cursor()


        if search_text:

            cursor.execute(
                """
                SELECT
                    students.name,
                    students.roll_no,
                    students.department,
                    attendance.date,
                    attendance.time,
                    attendance.status
                FROM attendance
                INNER JOIN students
                ON attendance.student_id = students.id
                WHERE students.name LIKE ?
                OR students.roll_no LIKE ?
                ORDER BY attendance.id DESC
                """,
                (
                    "%" + search_text + "%",
                    "%" + search_text + "%"
                )
            )


        else:

            cursor.execute(
                """
                SELECT
                    students.name,
                    students.roll_no,
                    students.department,
                    attendance.date,
                    attendance.time,
                    attendance.status
                FROM attendance
                INNER JOIN students
                ON attendance.student_id = students.id
                ORDER BY attendance.id DESC
                """
            )


        records = cursor.fetchall()

        connection.close()


        self.update_table(
            records
        )


    # ==================================================
    # UPDATE TABLE + SUMMARY
    # ==================================================

    def update_table(
        self,
        records
    ):

        # CLEAR TABLE

        for item in self.table.get_children():

            self.table.delete(
                item
            )


        # SUMMARY

        total_records = len(
            records
        )


        present_count = sum(
            1
            for record in records
            if record[5] == "Present"
        )


        absent_count = sum(
            1
            for record in records
            if record[5] == "Absent"
        )


        if total_records > 0:

            percentage = round(
                (
                    present_count
                    /
                    total_records
                ) * 100
            )

        else:

            percentage = 0


        self.total_card.config(
            text=str(
                total_records
            )
        )


        self.present_card.config(
            text=str(
                present_count
            )
        )


        self.absent_card.config(
            text=str(
                absent_count
            )
        )


        self.percentage_card.config(
            text=f"{percentage}%"
        )


        # INSERT TABLE DATA

        for index, record in enumerate(
            records,
            start=1
        ):

            self.table.insert(
                "",
                "end",
                values=(
                    index,
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5]
                )
            )


    # ==================================================
    # EXPORT CSV
    # ==================================================

    def export_csv(self):

        items = self.table.get_children()


        if not items:

            messagebox.showwarning(
                "No Data",
                "There is no attendance data to export."
            )

            return


        file_path = filedialog.asksaveasfilename(
            title="Save Attendance Report",
            defaultextension=".csv",
            filetypes=[
                (
                    "CSV Files",
                    "*.csv"
                )
            ]
        )


        if not file_path:

            return


        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(
                file
            )


            writer.writerow(
                [
                    "S.NO",
                    "STUDENT",
                    "ROLL NO",
                    "DEPARTMENT",
                    "DATE",
                    "TIME",
                    "STATUS"
                ]
            )


            for item in items:

                writer.writerow(
                    self.table.item(
                        item,
                        "values"
                    )
                )


        messagebox.showinfo(
            "Export Successful",
            "Attendance report exported successfully."
        )


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.withdraw()

    Reports(root)

    root.mainloop()