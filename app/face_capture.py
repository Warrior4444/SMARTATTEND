import cv2
import os
import time
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "smartattend.db"
)

FACES_DIR = os.path.join(
    BASE_DIR,
    "data",
    "faces"
)

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


class FaceCapture:

    def __init__(self, parent):

        self.parent = parent

        os.makedirs(FACES_DIR, exist_ok=True)

        self.window = tk.Toplevel(parent)
        self.window.title("Face Registration - SmartAttend AI")
        self.window.geometry("850x600")
        self.window.configure(bg="#0f172a")
        self.window.resizable(False, False)

        self.face_detector = cv2.CascadeClassifier(
            CASCADE_PATH
        )

        self.create_ui()
        self.load_students()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def create_ui(self):

        header = tk.Frame(
            self.window,
            bg="#111827",
            height=80
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Face Registration",
            bg="#111827",
            fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(
            side="left",
            padx=30,
            pady=20
        )

        content = tk.Frame(
            self.window,
            bg="#0f172a"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        tk.Label(
            content,
            text="Select Student",
            bg="#0f172a",
            fg="#cbd5e1",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.student_var = tk.StringVar()

        self.student_box = ttk.Combobox(
            content,
            textvariable=self.student_var,
            state="readonly",
            width=45,
            font=("Segoe UI", 11)
        )

        self.student_box.pack(
            anchor="w",
            pady=(8, 25),
            ipady=6
        )

        self.status_label = tk.Label(
            content,
            text="Ready to capture",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 11)
        )

        self.status_label.pack(
            pady=10
        )

        self.progress_label = tk.Label(
            content,
            text="Samples: 0 / 10",
            bg="#0f172a",
            fg="#60a5fa",
            font=("Segoe UI", 13, "bold")
        )

        self.progress_label.pack(
            pady=10
        )

        tk.Button(
            content,
            text="START FACE CAPTURE",
            command=self.start_capture,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        ).pack(
            pady=20,
            ipadx=30,
            ipady=12
        )

        tk.Label(
            content,
            text=(
                "Look directly at the camera • Good lighting recommended\n"
                "Keep your face clearly visible during registration"
            ),
            bg="#0f172a",
            fg="#64748b",
            font=("Segoe UI", 9),
            justify="center"
        ).pack(
            pady=10
        )

    # --------------------------------------------------
    # DATABASE
    # --------------------------------------------------

    def get_students(self):

        connection = sqlite3.connect(DB_PATH)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, roll_no
            FROM students
            ORDER BY name
            """
        )

        students = cursor.fetchall()

        connection.close()

        return students

    def load_students(self):

        students = self.get_students()

        self.student_data = {}

        values = []

        for student_id, name, roll_no in students:

            display = f"{name}  |  {roll_no}"

            values.append(display)

            self.student_data[display] = (
                student_id,
                name,
                roll_no
            )

        self.student_box["values"] = values

        if values:
            self.student_box.current(0)

    # --------------------------------------------------
    # FACE CAPTURE
    # --------------------------------------------------

    def start_capture(self):

        selected = self.student_var.get()

        if not selected:

            messagebox.showwarning(
                "Select Student",
                "Please select a student first."
            )

            return

        student_id, name, roll_no = self.student_data[selected]

        student_folder = os.path.join(
            FACES_DIR,
            str(student_id)
        )

        os.makedirs(
            student_folder,
            exist_ok=True
        )

        # Remove old samples
        for file in os.listdir(student_folder):

            file_path = os.path.join(
                student_folder,
                file
            )

            if os.path.isfile(file_path):

                try:
                    os.remove(file_path)
                except:
                    pass

        self.status_label.config(
            text=f"Starting camera for {name}...",
            fg="#60a5fa"
        )

        self.window.update()

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            messagebox.showerror(
                "Camera Error",
                "Unable to open camera."
            )

            return

        sample_count = 0

        last_capture = 0

        self.status_label.config(
            text="Look directly at the camera",
            fg="#22c55e"
        )

        while True:

            success, frame = camera.read()

            if not success:
                break

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=6,
                minSize=(100, 100)
            )

            # Draw all detected faces
            for (x, y, w, h) in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            # Capture only when exactly one face exists
            if len(faces) == 1:

                x, y, w, h = faces[0]

                face = gray[
                    y:y + h,
                    x:x + w
                ]

                # Quality check
                if w >= 120 and h >= 120:

                    current_time = time.time()

                    if current_time - last_capture >= 1.0:

                        sample_count += 1

                        filename = os.path.join(
                            student_folder,
                            f"{sample_count:03d}.jpg"
                        )

                        face = cv2.resize(
                            face,
                            (200, 200)
                        )

                        cv2.imwrite(
                            filename,
                            face
                        )

                        last_capture = current_time

                        self.progress_label.config(
                            text=f"Samples: {sample_count} / 30"
                        )

                        self.window.update()

                        cv2.putText(
                            frame,
                            f"CAPTURED {sample_count}/30",
                            (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2
                        )

            cv2.putText(
                frame,
                "Press Q to stop",
                (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "SmartAttend AI - Face Registration",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if sample_count >= 10:
                break

        camera.release()

        cv2.destroyAllWindows()

        # Update database
        if sample_count >= 10:

            connection = sqlite3.connect(DB_PATH)

            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE students
                SET face_registered = 1
                WHERE id = ?
                """,
                (student_id,)
            )

            connection.commit()
            connection.close()

            self.status_label.config(
                text="Face registration completed successfully",
                fg="#22c55e"
            )

            messagebox.showinfo(
                "Registration Complete",
                f"{name}\n\n"
                f"Face samples captured: {sample_count}\n\n"
                "Student is ready for model training."
            )

        else:

            self.status_label.config(
                text="Registration incomplete",
                fg="#ef4444"
            )

            messagebox.showwarning(
                "Registration Incomplete",
                f"Only {sample_count} samples captured.\n\n"
                "Please capture the face again."
            )


if __name__ == "__main__":

    root = tk.Tk()

    root.withdraw()

    FaceCapture(root)

    root.mainloop()