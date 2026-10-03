import cv2
import os
import sqlite3
from collections import Counter
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


def get_student_name(student_id):

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM students WHERE id = ?",
        (student_id,)
    )

    result = cursor.fetchone()
    connection.close()

    return result[0] if result else "Unknown"


def mark_attendance(student_id):

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM attendance
        WHERE student_id = ?
        AND date = ?
        """,
        (student_id, date)
    )

    if cursor.fetchone():
        connection.close()
        return False, "Already marked today"

    cursor.execute(
        """
        INSERT INTO attendance
        (student_id, date, time, status)
        VALUES (?, ?, ?, ?)
        """,
        (student_id, date, time, "Present")
    )

    connection.commit()
    connection.close()

    return True, "Attendance marked"


def live_attendance():

    if not os.path.exists(MODEL_PATH):
        print("Trained model not found.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=2,
        neighbors=16,
        grid_x=8,
        grid_y=8
    )

    recognizer.read(MODEL_PATH)

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera could not be opened.")
        return

    recent_ids = []
    confirmed_student = None
    message = "Scanning..."

    print("================================")
    print("SMARTATTEND AI")
    print("LIVE ATTENDANCE")
    print("Press Q to exit")
    print("================================")

    while True:

        success, frame = camera.read()

        if not success:
            break

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:

            face = gray[y:y + h, x:x + w]

            face = cv2.resize(
                face,
                (200, 200)
            )

            student_id, confidence = recognizer.predict(face)

            if confidence < 130:

                name = get_student_name(student_id)

                if name != "Unknown":

                    recent_ids.append(student_id)

                    if len(recent_ids) > 3:
                        recent_ids.pop(0)

                    # Confirm only after 3 consecutive matching frames
                    if (
                        len(recent_ids) == 3
                        and len(set(recent_ids)) == 1
                    ):

                        confirmed_student = student_id

                        success_mark, message = mark_attendance(
                            student_id
                        )

                    label = f"{name} | {confidence:.1f}"

                    box_color = (0, 255, 0)

                else:

                    label = "Unknown"
                    box_color = (0, 0, 255)
                    recent_ids.clear()

            else:

                label = f"Unknown | {confidence:.1f}"
                box_color = (0, 0, 255)
                recent_ids.clear()

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                box_color,
                2
            )

            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                box_color,
                2
            )

        cv2.rectangle(
            frame,
            (0, 0),
            (frame.shape[1], 55),
            (15, 23, 42),
            -1
        )

        cv2.putText(
            frame,
            message,
            (20, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "SmartAttend AI - Live Attendance",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    live_attendance()