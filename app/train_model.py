import cv2
import os
import sqlite3
import numpy as np


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

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

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "trainer.yml"
)


# =========================================================
# GET CURRENT STUDENT IDS FROM DATABASE
# =========================================================

def get_valid_student_ids():

    valid_ids = set()

    try:

        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM students"
        )

        rows = cursor.fetchall()

        conn.close()

        for row in rows:

            valid_ids.add(
                int(row[0])
            )

    except Exception as e:

        print(
            "DATABASE ERROR:",
            e
        )

    return valid_ids


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model():

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8
    )

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    faces = []
    labels = []

    if not os.path.exists(FACES_DIR):

        print(
            "Face data folder not found."
        )

        return False

    # -----------------------------------------------------
    # GET ONLY CURRENT STUDENTS
    # -----------------------------------------------------

    valid_ids = get_valid_student_ids()

    print(
        "Valid student IDs:",
        sorted(valid_ids)
    )

    if len(valid_ids) == 0:

        print(
            "No students found in database."
        )

        return False

    print(
        "Scanning face samples..."
    )

    # -----------------------------------------------------
    # SCAN FACE FOLDERS
    # -----------------------------------------------------

    for student_id in os.listdir(FACES_DIR):

        student_folder = os.path.join(
            FACES_DIR,
            student_id
        )

        if not os.path.isdir(
            student_folder
        ):
            continue

        try:

            label = int(student_id)

        except ValueError:

            continue

        # -------------------------------------------------
        # IMPORTANT:
        # IGNORE OLD / DELETED STUDENT FOLDERS
        # -------------------------------------------------

        if label not in valid_ids:

            print(
                f"Skipping old student folder: {label}"
            )

            continue

        image_files = [
            f
            for f in os.listdir(
                student_folder
            )
            if f.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png"
                )
            )
        ]

        print(
            f"Student {label}: "
            f"{len(image_files)} images"
        )

        # -------------------------------------------------
        # PROCESS IMAGES
        # -------------------------------------------------

        for image_name in image_files:

            image_path = os.path.join(
                student_folder,
                image_name
            )

            image = cv2.imread(
                image_path,
                cv2.IMREAD_GRAYSCALE
            )

            if image is None:

                continue

            # ---------------------------------------------
            # RESIZE LARGE IMAGE
            # ---------------------------------------------

            height, width = image.shape

            if width > 640:

                scale = 640 / width

                new_width = 640

                new_height = int(
                    height * scale
                )

                image = cv2.resize(
                    image,
                    (
                        new_width,
                        new_height
                    )
                )

            # ---------------------------------------------
            # DETECT FACE
            # ---------------------------------------------

            detected_faces = detector.detectMultiScale(
                image,
                scaleFactor=1.2,
                minNeighbors=4,
                minSize=(60, 60)
            )

            # ---------------------------------------------
            # NO FACE DETECTED
            # ---------------------------------------------

            if len(detected_faces) == 0:

                face = cv2.resize(
                    image,
                    (160, 160)
                )

                faces.append(
                    face
                )

                labels.append(
                    label
                )

            # ---------------------------------------------
            # FACE DETECTED
            # ---------------------------------------------

            else:

                x, y, w, h = max(
                    detected_faces,
                    key=lambda r:
                        r[2] * r[3]
                )

                face = image[
                    y:y + h,
                    x:x + w
                ]

                if face.size == 0:

                    continue

                face = cv2.resize(
                    face,
                    (160, 160)
                )

                faces.append(
                    face
                )

                labels.append(
                    label
                )

    # =====================================================
    # NO SAMPLES
    # =====================================================

    if len(faces) == 0:

        print(
            "No valid face samples found."
        )

        return False

    # =====================================================
    # TRAIN
    # =====================================================

    print(
        f"Training with {len(faces)} face samples..."
    )

    recognizer.train(
        faces,
        np.array(labels)
    )

    # =====================================================
    # SAVE MODEL
    # =====================================================

    recognizer.save(
        MODEL_PATH
    )

    print(
        "================================"
    )

    print(
        "MODEL TRAINING COMPLETED"
    )

    print(
        "================================"
    )

    print(
        f"Students used : "
        f"{len(set(labels))}"
    )

    print(
        f"Samples used  : "
        f"{len(faces)}"
    )

    print(
        f"Model saved   : "
        f"{MODEL_PATH}"
    )

    return True


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    train_model()