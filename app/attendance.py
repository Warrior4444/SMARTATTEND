import sqlite3
from datetime import datetime
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "smartattend.db"
)


def mark_attendance(student_id):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Check whether attendance is already marked today
    cursor.execute(
        """
        SELECT id
        FROM attendance
        WHERE student_id = ?
        AND date = ?
        """,
        (student_id, date)
    )

    existing = cursor.fetchone()

    if existing:

        connection.close()

        return False, "Attendance already marked today."

    # Mark attendance
    cursor.execute(
        """
        INSERT INTO attendance
        (student_id, date, time, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            student_id,
            date,
            time,
            "Present"
        )
    )

    connection.commit()
    connection.close()

    return True, "Attendance marked successfully."


if __name__ == "__main__":

    # Test with student ID 1
    success, message = mark_attendance(1)

    print(message)