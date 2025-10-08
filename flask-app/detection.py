

# import threading
# import cv2
# import numpy as np
# import time
# from datetime import datetime
# from tensorflow.keras.models import load_model
# from pymongo import MongoClient


# class DetectionWorker:
#     def __init__(self, camera_index=0, mongo_uri="mongodb://localhost:27017", db_name="smart_classroom"):
#         # === Models ===
#         self.eye_model = load_model("models/eye_state_mrl_model.h5")
#         self.yawn_model = load_model("models/yawn_detector_model.h5")
#         self.emotion_model = load_model("models/emotion_detector_model.h5")

#         # === Emotion labels (FER-2013) ===
#         self.emotion_labels = ['Angry', 'Disgust', 'Fear',
#                                'Happy', 'Sad', 'Surprise', 'Neutral']

#         # === Cascades ===
#         self.face_cascade = cv2.CascadeClassifier(
#             cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#         self.eye_cascade = cv2.CascadeClassifier(
#             cv2.data.haarcascades + "haarcascade_eye.xml")
#         self.mouth_cascade = cv2.CascadeClassifier(
#             "cascades/haarcascade_mcs_mouth.xml")

#         # === State ===
#         self.cap = cv2.VideoCapture(camera_index)
#         self.lock = threading.Lock()
#         self.running = False
#         self.thread = None
#         self.latest = {"eye_state": None, "yawning": None, "emotion": None}
#         self.last_eye_closed_time = None
#         self.EYE_CLOSED_THRESHOLD = 3  # seconds

#         # === Session data ===
#         self.session_data = {
#             "student_name": None,
#             "start_time": None,
#             "end_time": None,
#             "eye_closures": 0,
#             "yawns": 0,
#             "drowsiness_alerts": 0
#         }

#         # === MongoDB ===
#         self.client = MongoClient(mongo_uri)
#         self.db = self.client[db_name]
#         self.reports = self.db["session_reports"]

#     # === Preprocessing helpers ===
#     def preprocess_eye(self, eye_img):
#         eye_img = cv2.resize(eye_img, (48, 48))
#         eye_img = eye_img.astype("float32") / 255.0
#         eye_img = np.expand_dims(eye_img, axis=-1)
#         eye_img = np.expand_dims(eye_img, axis=0)
#         return eye_img

#     def preprocess_mouth(self, mouth_img):
#         mouth_img = cv2.cvtColor(mouth_img, cv2.COLOR_GRAY2RGB)
#         mouth_img = cv2.resize(mouth_img, (58, 56))
#         mouth_img = mouth_img.astype("float32") / 255.0
#         mouth_img = np.expand_dims(mouth_img, axis=0)
#         return mouth_img

#     def preprocess_face(self, face_img):
#         face_img = cv2.resize(face_img, (48, 48))
#         face_img = face_img.astype("float32") / 255.0
#         face_img = np.expand_dims(face_img, axis=-1)
#         face_img = np.expand_dims(face_img, axis=0)
#         return face_img

#     # === Detection loop ===
#     def _run(self):
#         self.session_data["start_time"] = time.time()
#         self.session_data["eye_closures"] = 0
#         self.session_data["yawns"] = 0
#         self.session_data["drowsiness_alerts"] = 0

#         while self.running:
#             ret, frame = self.cap.read()
#             if not ret:
#                 time.sleep(0.1)
#                 continue

#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

#             eye_state, yawning_state, emotion_state = "unknown", "unknown", "unknown"

#             for (x, y, w, h) in faces:
#                 roi_gray = gray[y:y+h, x:x+w]
#                 roi_color = frame[y:y+h, x:x+w]

#                 # === Emotion Detection ===
#                 try:
#                     face_input = self.preprocess_face(roi_gray)
#                     emotion_pred = self.emotion_model.predict(
#                         face_input, verbose=0)
#                     emotion_idx = np.argmax(emotion_pred)
#                     emotion_state = self.emotion_labels[emotion_idx]
#                 except:
#                     emotion_state = "unknown"

#                 # === Eye Detection ===
#                 eyes = self.eye_cascade.detectMultiScale(roi_gray)
#                 for (ex, ey, ew, eh) in eyes[:1]:
#                     eye_img = roi_gray[ey:ey+eh, ex:ex+ew]
#                     eye_input = self.preprocess_eye(eye_img)
#                     pred = self.eye_model.predict(eye_input, verbose=0)[0][0]
#                     eye_state = "open" if pred > 0.5 else "closed"

#                     if eye_state == "closed":
#                         if self.last_eye_closed_time is None:
#                             self.last_eye_closed_time = time.time()
#                         elif time.time() - self.last_eye_closed_time >= self.EYE_CLOSED_THRESHOLD:
#                             self.session_data["drowsiness_alerts"] += 1
#                             self.last_eye_closed_time = None
#                             cv2.putText(frame, "⚠ DROWSINESS ALERT!", (50, 50),
#                                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
#                         self.session_data["eye_closures"] += 1
#                     else:
#                         self.last_eye_closed_time = None

#                     color = (0, 255, 0) if eye_state == "open" else (0, 0, 255)
#                     cv2.rectangle(roi_color, (ex, ey),
#                                   (ex+ew, ey+eh), color, 2)
#                     cv2.putText(frame, f"Eye: {eye_state}", (x, y - 10),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#                 # === Mouth Detection (Yawning) ===
#                 mouths = self.mouth_cascade.detectMultiScale(roi_gray, 1.7, 11)
#                 for (mx, my, mw, mh) in mouths:
#                     if my > h / 2:  # lower half of face
#                         mouth_img = roi_gray[my:my+mh, mx:mx+mw]
#                         mouth_input = self.preprocess_mouth(mouth_img)
#                         pred = self.yawn_model.predict(
#                             mouth_input, verbose=0)[0][0]
#                         yawning_state = "yes" if pred > 0.5 else "no"

#                         if yawning_state == "yes":
#                             self.session_data["yawns"] += 1
#                             cv2.putText(frame, "⚠ YAWNING ALERT!", (50, 90),
#                                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

#                         color = (0, 0, 255) if yawning_state == "yes" else (
#                             0, 255, 0)
#                         cv2.rectangle(roi_color, (mx, my),
#                                       (mx+mw, my+mh), color, 2)
#                         cv2.putText(frame, f"Yawning: {yawning_state}", (x, y+h+30),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
#                         break

#                 # === Draw emotion ===
#                 cv2.putText(frame, f"Emotion: {emotion_state}", (x, y+h+60),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

#                 cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

#                 break  # process only first detected face

#             # === Update latest results ===
#             with self.lock:
#                 self.latest = {
#                     "timestamp": datetime.now().isoformat(),
#                     "eye_state": eye_state,
#                     "yawning": yawning_state,
#                     "emotion": emotion_state
#                 }

#             cv2.imshow("Smart Classroom Detection", frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 self.running = False

#         self.cap.release()
#         cv2.destroyAllWindows()
#         self.session_data["end_time"] = time.time()
#         self._save_report_to_mongo()

#     # === MongoDB save ===
#     def _save_report_to_mongo(self):
#         if self.session_data["start_time"] is None:
#             return
#         duration = (self.session_data["end_time"] or time.time(
#         )) - self.session_data["start_time"]
#         report = {
#             "student_name": self.session_data["student_name"],
#             "start_time": datetime.fromtimestamp(self.session_data["start_time"]),
#             "end_time": datetime.fromtimestamp(self.session_data["end_time"]),
#             "session_duration_sec": round(duration, 2),
#             "eye_closures": self.session_data["eye_closures"],
#             "yawns": self.session_data["yawns"],
#             "drowsiness_alerts": self.session_data["drowsiness_alerts"],
#             "created_at": datetime.now()
#         }
#         self.reports.insert_one(report)
#         print("✅ Report saved to MongoDB:", report)

#     # === Public methods ===
#     def start(self, student_name):
#         if self.running:
#             return
#         self.session_data["student_name"] = student_name
#         self.running = True
#         self.thread = threading.Thread(target=self._run, daemon=True)
#         self.thread.start()

#     def stop(self):
#         self.running = False
#         if self.thread:
#             self.thread.join(timeout=1)

#     def get_latest(self):
#         with self.lock:
#             return dict(self.latest)

#     def get_session_report(self):
#         if self.session_data["start_time"] is None:
#             return {"error": "No session data available"}
#         duration = (self.session_data["end_time"] or time.time(
#         )) - self.session_data["start_time"]
#         return {
#             "student_name": self.session_data["student_name"],
#             "session_duration_sec": round(duration, 2),
#             "eye_closures": self.session_data["eye_closures"],
#             "yawns": self.session_data["yawns"],
#             "drowsiness_alerts": self.session_data["drowsiness_alerts"]
#         }

import cv2
import threading
import time
import numpy as np
from datetime import datetime
from tensorflow.keras.models import load_model
from pymongo import MongoClient


class DetectionWorker:
    def __init__(self, camera_index=0, mongo_uri="mongodb://localhost:27017", db_name="smart_classroom"):
        # === Models ===
        self.eye_model = load_model("models/eye_state_mrl_model.h5")
        self.yawn_model = load_model("models/yawn_detector_model.h5")
        self.emotion_model = load_model("models/emotion_detector_model.h5")

        # === Emotion labels ===
        self.emotion_labels = ['Angry', 'Disgust',
                               'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

        # === Cascades ===
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml")
        self.mouth_cascade = cv2.CascadeClassifier(
            "cascades/haarcascade_mcs_mouth.xml")

        # === State ===
        self.camera_index = camera_index
        self.cap = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.latest = {"eye_state": None, "yawning": None, "emotion": None}
        self.last_eye_closed_time = None
        self.EYE_CLOSED_THRESHOLD = 3  # seconds

        # === Session data ===
        self.session_data = {}

        # === MongoDB ===
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.reports = self.db["session_reports"]

    # === Detection loop ===
    def _run(self):
        # Initialize new capture for each session
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("❌ Could not open webcam.")
            self.running = False
            return

        self.session_data["start_time"] = time.time()
        self.session_data["end_time"] = None
        self.session_data["eye_closures"] = 0
        self.session_data["yawns"] = 0
        self.session_data["drowsiness_alerts"] = 0

        print(
            f"🎥 Detection started for {self.session_data.get('student_name')}")

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                eye_state, yawning_state, emotion_state = "unknown", "unknown", "unknown"

                for (x, y, w, h) in faces[:1]:
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]

                    # === Emotion Detection ===
                    try:
                        face_input = self._preprocess_face(roi_gray)
                        emotion_pred = self.emotion_model.predict(
                            face_input, verbose=0)
                        emotion_state = self.emotion_labels[np.argmax(
                            emotion_pred)]
                    except:
                        emotion_state = "unknown"

                    # === Eye Detection ===
                    eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    for (ex, ey, ew, eh) in eyes[:1]:
                        eye_img = roi_gray[ey:ey+eh, ex:ex+ew]
                        eye_input = self._preprocess_eye(eye_img)
                        pred = self.eye_model.predict(
                            eye_input, verbose=0)[0][0]
                        eye_state = "open" if pred > 0.5 else "closed"

                        if eye_state == "closed":
                            if self.last_eye_closed_time is None:
                                self.last_eye_closed_time = time.time()
                            elif time.time() - self.last_eye_closed_time >= self.EYE_CLOSED_THRESHOLD:
                                self.session_data["drowsiness_alerts"] += 1
                                self.last_eye_closed_time = None
                            self.session_data["eye_closures"] += 1
                        else:
                            self.last_eye_closed_time = None

                    # === Mouth Detection (Yawning) ===
                    mouths = self.mouth_cascade.detectMultiScale(
                        roi_gray, 1.7, 11)
                    for (mx, my, mw, mh) in mouths:
                        if my > h / 2:
                            mouth_img = roi_gray[my:my+mh, mx:mx+mw]
                            mouth_input = self._preprocess_mouth(mouth_img)
                            pred = self.yawn_model.predict(
                                mouth_input, verbose=0)[0][0]
                            yawning_state = "yes" if pred > 0.5 else "no"
                            if yawning_state == "yes":
                                self.session_data["yawns"] += 1
                            break

                    break  # only process first face

                with self.lock:
                    self.latest = {
                        "timestamp": datetime.now().isoformat(),
                        "eye_state": eye_state,
                        "yawning": yawning_state,
                        "emotion": emotion_state
                    }

                cv2.imshow("Smart Classroom Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False

        finally:
            # Release resources safely
            if self.cap:
                self.cap.release()
                self.cap = None
            cv2.destroyAllWindows()
            self.session_data["end_time"] = time.time()
            self._save_report_to_mongo()
            print(
                f"🛑 Detection stopped for {self.session_data.get('student_name')}")

    # === Preprocessing helpers ===
    def _preprocess_eye(self, eye_img):
        eye_img = cv2.resize(eye_img, (48, 48))
        eye_img = eye_img.astype("float32") / 255.0
        eye_img = np.expand_dims(eye_img, axis=(0, -1))
        return eye_img

    def _preprocess_mouth(self, mouth_img):
        mouth_img = cv2.cvtColor(mouth_img, cv2.COLOR_GRAY2RGB)
        mouth_img = cv2.resize(mouth_img, (58, 56))
        mouth_img = mouth_img.astype("float32") / 255.0
        mouth_img = np.expand_dims(mouth_img, axis=0)
        return mouth_img

    def _preprocess_face(self, face_img):
        face_img = cv2.resize(face_img, (48, 48))
        face_img = face_img.astype("float32") / 255.0
        face_img = np.expand_dims(face_img, axis=(0, -1))
        return face_img

    # === MongoDB save ===
    def _save_report_to_mongo(self):
        if not self.session_data.get("start_time"):
            return
        duration = (self.session_data["end_time"] or time.time(
        )) - self.session_data["start_time"]
        report = {
            "student_name": self.session_data.get("student_name"),
            "start_time": datetime.fromtimestamp(self.session_data["start_time"]),
            "end_time": datetime.fromtimestamp(self.session_data["end_time"]),
            "session_duration_sec": round(duration, 2),
            "eye_closures": self.session_data.get("eye_closures", 0),
            "yawns": self.session_data.get("yawns", 0),
            "drowsiness_alerts": self.session_data.get("drowsiness_alerts", 0),
            "created_at": datetime.now()
        }
        self.reports.insert_one(report)
        print("✅ Report saved to MongoDB:", report)

    # === Public methods ===
    def start(self, student_name):
        if self.running:
            print("⚠ Detection already running.")
            return
        self.session_data = {"student_name": student_name}
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            print("⚠ Detection not running.")
            return
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def get_latest(self):
        with self.lock:
            return dict(self.latest)

    def get_session_report(self):
        if not self.session_data.get("start_time"):
            return {"error": "No session data available"}
        duration = (self.session_data.get("end_time")
                    or time.time()) - self.session_data["start_time"]
        return {
            "student_name": self.session_data.get("student_name"),
            "session_duration_sec": round(duration, 2),
            "eye_closures": self.session_data.get("eye_closures", 0),
            "yawns": self.session_data.get("yawns", 0),
            "drowsiness_alerts": self.session_data.get("drowsiness_alerts", 0)
        }
