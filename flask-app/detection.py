# # ==================================================================================================================
# import cv2
# import threading
# import time
# import numpy as np
# from datetime import datetime
# from tensorflow.keras.models import load_model
# from pymongo import MongoClient
# import os


# class DetectionWorker:
#     # "mongodb://localhost:27017", db_name="smart_classroom"):
#     def __init__(self, camera_index=0, mongo_uri="mongodb+srv://samithdarshana:1234@cluster0.wupnzmn.mongodb.net/?appName=Cluster0", db_name="Smart-Classroom-App"):
#         # === Load Models ===
#         # self.eye_model = load_model(
#         #     "models/eye_state_cnn_224.h5")
#         self.eye_model = load_model(
#             "models/Eye-State-Detection-DenseNet121.h5")
#         self.yawn_model = load_model("models/yawn_detector_model.h5")
#         self.emotion_model = load_model("models/emotion_detector_model.h5")
#         self.behavior_model = load_model(
#             "models/student_behavior_model_2.0.h5")

#         # === Model Labels ===
#         self.emotion_labels = ['Angry', 'Disgust',
#                                'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

#         self.behavior_labels = ["attentive", "distracted"]

#         # === Cascades ===
#         self.face_cascade = cv2.CascadeClassifier(
#             cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#         self.eye_cascade = cv2.CascadeClassifier(
#             cv2.data.haarcascades + "haarcascade_eye.xml")
#         self.mouth_cascade = cv2.CascadeClassifier(
#             "cascades/haarcascade_mcs_mouth.xml")

#         # === Dynamic Thresholds ===
#         self.EYE_CLOSED_THRESHOLD = 1.0  # seconds eyes must stay closed
#         self.YAWN_CONF_THRESHOLD = 0.5   # probability threshold for yawn model
#         self.EYE_CONF_THRESHOLD = 0.5    # probability threshold for eye model

#         # === State ===
#         self.camera_index = camera_index
#         self.cap = None
#         self.lock = threading.Lock()
#         self.running = False
#         self.thread = None
#         self.latest = {"eye_state": None, "yawning": None, "emotion": None}
#         self.last_eye_closed_time = None
#         self.last_alert_time = None

#         # === Session Data ===
#         self.session_data = {}

#         # === MongoDB ===
#         self.client = MongoClient(mongo_uri)
#         self.db = self.client[db_name]
#         self.alerts = self.db["alerts"]
#         self.reports = self.db["session_reports"]

#         # === Snapshot Folder ===
#         self.snapshot_dir = "snapshots"
#         os.makedirs(self.snapshot_dir, exist_ok=True)

#     def _save_drowsiness_event(self):
#         """Save every drowsiness alert to MongoDB immediately."""
#         event = {
#             "student_name": self.session_data.get("student_name"),
#             "timestamp": datetime.now(),
#             "event_type": "drowsiness_alert",
#             "status": "unread"
#         }
#         self.db["alerts"].insert_one(event)
#         print("⚠️ Drowsiness Alert Saved:", event)

#     def _has_unread_alert(self, student_name):
#         """Return True if the student already has an unread alert."""
#         return self.alerts.count_documents({
#             "student_name": student_name,
#             "status": "unread"
#         }) > 0

#     # === Main Detection Loop ===

#     def _run(self):
#         self.cap = cv2.VideoCapture(self.camera_index)
#         if not self.cap.isOpened():
#             print("❌ Could not open webcam.")
#             self.running = False
#             return

#         self.session_data = {
#             "start_time": time.time(),
#             "end_time": None,
#             "eye_closures": 0,
#             "yawns": 0,
#             "drowsiness_alerts": 0,
#             "distraction_count": 0,
#             "student_name": self.session_data.get("student_name")
#         }

#         print(
#             f"🎥 Detection started for {self.session_data.get('student_name')}")
#         print(f"⚙ Thresholds: EYE_CLOSED_THRESHOLD={self.EYE_CLOSED_THRESHOLD}s, "
#               f"EYE_CONF={self.EYE_CONF_THRESHOLD}, YAWN_CONF={self.YAWN_CONF_THRESHOLD}")

#         try:
#             while self.running:
#                 ret, frame = self.cap.read()
#                 if not ret:
#                     time.sleep(0.1)
#                     continue

#                 gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#                 faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

#                 eye_state, yawning_state, emotion_state = "unknown", "unknown", "unknown"

#                 for (x, y, w, h) in faces[:1]:
#                     roi_gray = gray[y:y+h, x:x+w]
#                     roi_color = frame[y:y+h, x:x+w]

#                     # === Emotion Detection ===
#                     try:
#                         face_input = self._preprocess_face(roi_gray)
#                         emotion_pred = self.emotion_model.predict(
#                             face_input, verbose=0)
#                         emotion_state = self.emotion_labels[np.argmax(
#                             emotion_pred)]
#                     except:
#                         emotion_state = "unknown"

#                     # === Eye Detection (DenseNet121) ===
#                     eyes = self.eye_cascade.detectMultiScale(roi_gray)
#                     for (ex, ey, ew, eh) in eyes[:1]:
#                         eye_img = roi_gray[ey:ey+eh, ex:ex+ew]
#                         eye_input = self._preprocess_eye(eye_img)
#                         pred = self.eye_model.predict(
#                             eye_input, verbose=0)[0][0]
#                         eye_state = "open" if pred > self.EYE_CONF_THRESHOLD else "closed"

#                         color = (0, 255, 0) if eye_state == "open" else (
#                             0, 0, 255)
#                         cv2.rectangle(roi_color, (ex, ey),
#                                       (ex+ew, ey+eh), color, 2)

#                         if eye_state == "closed":
#                             if self.last_eye_closed_time is None:
#                                 self.last_eye_closed_time = time.time()
#                             elif time.time() - self.last_eye_closed_time >= self.EYE_CLOSED_THRESHOLD:

#                                 now = time.time()
#                                 student = self.session_data.get("student_name")

#                                 # --- Check if student already has an unread alert ---
#                                 if not self._has_unread_alert(student):

#                                     # --- Check 1-minute cooldown ---
#                                     if self.last_alert_time is None or (now - self.last_alert_time) >= 60:

#                                         # Save event
#                                         event = {
#                                             "student_name": student,
#                                             "timestamp": datetime.now(),
#                                             "event_type": "drowsiness_alert",
#                                             "status": "unread"
#                                         }
#                                         self.alerts.insert_one(event)
#                                         print("🔔 Drowsiness alert saved:", event)

#                                         self.session_data["drowsiness_alerts"] += 1
#                                         self.last_alert_time = now
#                                     else:
#                                         print(
#                                             "⏳ Cooldown active — alert not saved.")

#                                 else:
#                                     print(
#                                         "⚠ Unread alert exists — new alert skipped.")

#                                 self.last_eye_closed_time = None
#                         else:
#                             self.last_eye_closed_time = None

#                     # === Yawn Detection ===
#                     mouths = self.mouth_cascade.detectMultiScale(
#                         roi_gray, 1.7, 11)
#                     for (mx, my, mw, mh) in mouths:
#                         if my > h / 2:
#                             mouth_img = roi_gray[my:my+mh, mx:mx+mw]
#                             mouth_input = self._preprocess_mouth(mouth_img)
#                             pred = self.yawn_model.predict(
#                                 mouth_input, verbose=0)[0][0]
#                             yawning_state = "yes" if pred > self.YAWN_CONF_THRESHOLD else "no"
#                             if yawning_state == "yes":
#                                 self.session_data["yawns"] += 1
#                             break

#                     # === Student Behavior Detection (Attentive vs Distracted) ===
#                     behavior_state = "unknown"
#                     behavior_conf = 0.0

#                     try:
#                         behavior_input = self._preprocess_behavior(frame)
#                         behavior_pred = self.behavior_model.predict(
#                             behavior_input, verbose=0)
#                         behavior_idx = np.argmax(behavior_pred)
#                         behavior_state = self.behavior_labels[behavior_idx]
#                         behavior_conf = float(behavior_pred[0][behavior_idx])

#                         # Optional: Count distractions
#                         if behavior_state == "distracted" and behavior_conf > 0.75:
#                             self.session_data["distraction_count"] = self.session_data.get(
#                                 "distraction_count", 0) + 1

#                         # Display on frame
#                         color = (0, 255, 0) if behavior_state == "attentive" else (
#                             0, 0, 255)
#                         cv2.putText(frame, f"Focus: {behavior_state.capitalize()} ({behavior_conf*100:.1f}%)",
#                                     (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

#                     except Exception as e:
#                         print(f"Behavior model error: {e}")
#                         behavior_state = "error"
#                         behavior_conf = 0.0
#                         cv2.putText(frame, "Focus: error", (x, y + h + 30),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#                     # # === Student Behavior (Attentive vs Distracted) ===
#                     # try:
#                     #     behavior_input = self._preprocess_behavior(
#                     #         frame)  # full frame
#                     #     behavior_pred = self.behavior_model.predict(
#                     #         behavior_input, verbose=0)
#                     #     behavior_idx = np.argmax(behavior_pred)
#                     #     behavior_state = self.behavior_labels[behavior_idx]
#                     #     behavior_conf = behavior_pred[0][behavior_idx]

#                     #     # Optional: Count distracted time or trigger alerts
#                     #     if behavior_state == "distracted" and behavior_conf > 0.7:
#                     #         self.session_data["distraction_count"] = self.session_data.get(
#                     #             "distraction_count", 0) + 1

#                     # except Exception as e:
#                     #     behavior_state = "unknown"
#                     #     behavior_conf = 0.0
#                     #     print("Behavior model error:", e)

#                     # === Overlay Info ===
#                     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
#                     cv2.putText(frame, f"Emotion: {emotion_state}", (x, y - 50),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
#                     cv2.putText(frame, f"Eye: {eye_state}", (x, y - 25),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.7,
#                                 (0, 255, 0) if eye_state == "open" else (0, 0, 255), 2)
#                     cv2.putText(frame, f"Yawn: {yawning_state}", (x, y - 5),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.7,
#                                 (0, 255, 255) if yawning_state == "yes" else (255, 255, 255), 2)

#                     cv2.putText(frame, f"Behavior: {behavior_state.capitalize()} ({behavior_conf*100:.1f}%)",
#                                 (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
#                                 (0, 255, 0) if behavior_state == "attentive" else (0, 0, 255), 2)

#                     if self.session_data["drowsiness_alerts"] > 0:
#                         cv2.putText(frame, "⚠ DROWSINESS ALERT!", (50, 50),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
#                     break  # only first face

#                 with self.lock:
#                     self.latest = {
#                         "timestamp": datetime.now().isoformat(),
#                         "eye_state": eye_state,
#                         "yawning": yawning_state,
#                         "emotion": emotion_state,
#                         "behavior": behavior_state,          # ← Add this
#                         "behavior_confidence": float(behavior_conf)
#                     }

#                 cv2.imshow("Smart Classroom Detection", frame)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     self.running = False

#         finally:
#             if self.cap:
#                 self.cap.release()
#                 self.cap = None
#             cv2.destroyAllWindows()
#             self.session_data["end_time"] = time.time()
#             self._save_report_to_mongo()
#             print(
#                 f"🛑 Detection stopped for {self.session_data.get('student_name')}")

#     # === Preprocessing helpers ===
#     def _preprocess_eye(self, eye_img):
#         """Preprocess eye for DenseNet121 (224x224 RGB)."""
#         eye_img = cv2.cvtColor(eye_img, cv2.COLOR_GRAY2RGB)
#         eye_img = cv2.resize(eye_img, (224, 224))
#         eye_img = eye_img.astype("float32") / 255.0
#         eye_img = np.expand_dims(eye_img, axis=0)
#         return eye_img

#     def _preprocess_mouth(self, mouth_img):
#         mouth_img = cv2.cvtColor(mouth_img, cv2.COLOR_GRAY2RGB)
#         mouth_img = cv2.resize(mouth_img, (58, 56))
#         mouth_img = mouth_img.astype("float32") / 255.0
#         mouth_img = np.expand_dims(mouth_img, axis=0)
#         return mouth_img

#     def _preprocess_face(self, face_img):
#         face_img = cv2.resize(face_img, (48, 48))
#         face_img = face_img.astype("float32") / 255.0
#         face_img = np.expand_dims(face_img, axis=(0, -1))
#         return face_img

#     def _preprocess_behavior(self, frame):
#         img = cv2.resize(frame, (224, 224))
#         img = img.astype("float32") / 255.0
#         img = np.expand_dims(img, axis=0)
#         return img

#     def _save_snapshot(self, frame, label):
#         """Save snapshot when drowsiness or yawning detected."""
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         path = os.path.join(self.snapshot_dir, f"{label}_{timestamp}.jpg")
#         cv2.imwrite(path, frame)
#         print(f"📸 Snapshot saved: {path}")

#     # === Save Report to MongoDB ===
#     def _save_report_to_mongo(self):
#         if not self.session_data.get("start_time"):
#             return
#         duration = (self.session_data["end_time"] or time.time(
#         )) - self.session_data["start_time"]
#         report = {
#             "student_name": self.session_data.get("student_name"),
#             "start_time": datetime.fromtimestamp(self.session_data["start_time"]),
#             "end_time": datetime.fromtimestamp(self.session_data["end_time"]),
#             "session_duration_sec": round(duration, 2),
#             "eye_closures": self.session_data.get("eye_closures", 0),
#             "yawns": self.session_data.get("yawns", 0),
#             "drowsiness_alerts": self.session_data.get("drowsiness_alerts", 0),
#             "distraction_count": self.session_data.get("distraction_count", 0),
#             "created_at": datetime.now()
#         }
#         self.reports.insert_one(report)
#         print("✅ Report saved to MongoDB:", report)

#     # === Public Methods ===
#     def start(self, student_name):
#         if self.running:
#             print("⚠ Detection already running.")
#             return
#         self.session_data = {"student_name": student_name}
#         self.running = True
#         self.thread = threading.Thread(target=self._run, daemon=True)
#         self.thread.start()

#     def stop(self):
#         if not self.running:
#             print("⚠ Detection not running.")
#             return
#         self.running = False
#         if self.thread:
#             self.thread.join(timeout=2)

#     def get_latest(self):
#         with self.lock:
#             return dict(self.latest)

#     def get_session_report(self):
#         if not self.session_data.get("start_time"):
#             return {"error": "No session data available"}
#         duration = (self.session_data.get("end_time")
#                     or time.time()) - self.session_data["start_time"]
#         return {
#             "student_name": self.session_data.get("student_name"),
#             "session_duration_sec": round(duration, 2),
#             "eye_closures": self.session_data.get("eye_closures", 0),
#             "yawns": self.session_data.get("yawns", 0),
#             "drowsiness_alerts": self.session_data.get("drowsiness_alerts", 0),
#             "distraction_count": self.session_data.get("distraction_count", 0)
#         }

#     # def update_thresholds(self, eye_closed=None, eye_conf=None, yawn_conf=None):
#     #     """Update detection sensitivity dynamically."""
#     #     if eye_closed is not None:
#     #         self.EYE_CLOSED_THRESHOLD = float(eye_closed)
#     #     if eye_conf is not None:
#     #         self.EYE_CONF_THRESHOLD = float(eye_conf)
#     #     if yawn_conf is not None:
#     #         self.YAWN_CONF_THRESHOLD = float(yawn_conf)

#     #     print(f"🔄 Thresholds updated: EYE_CLOSED={self.EYE_CLOSED_THRESHOLD}s, "
#     #           f"EYE_CONF={self.EYE_CONF_THRESHOLD}, YAWN_CONF={self.YAWN_CONF_THRESHOLD}")

#     def update_thresholds(self, thresholds=None, eye_closed=None, eye_conf=None, yawn_conf=None):

#         # --- If a dict (from set_mode) is passed ---
#         if isinstance(thresholds, dict):
#             # Extract thresholds if present in dict
#             eye_closed = thresholds.get("eye_closed", eye_closed)
#             eye_conf = thresholds.get("eye_conf", eye_conf)
#             yawn_conf = thresholds.get("yawn_conf", yawn_conf)

#     # --- Apply updates ---
#         if eye_closed is not None:
#             self.EYE_CLOSED_THRESHOLD = float(eye_closed)
#         if eye_conf is not None:
#             self.EYE_CONF_THRESHOLD = float(eye_conf)
#         if yawn_conf is not None:
#             self.YAWN_CONF_THRESHOLD = float(yawn_conf)

#         print(f"🔄 Thresholds updated: "
#               f"EYE_CLOSED={self.EYE_CLOSED_THRESHOLD}s, "
#               f"EYE_CONF={self.EYE_CONF_THRESHOLD}, "
#               f"YAWN_CONF={self.YAWN_CONF_THRESHOLD}")


# # === Example usage ===
# if __name__ == "__main__":
#     worker = DetectionWorker()
#     worker.start("User 1")

#     try:
#         time.sleep(5)
#         # Example: dynamically adjust detection sensitivity
#         worker.update_thresholds(eye_closed=0.8, eye_conf=0.6, yawn_conf=0.55)
#         while worker.running:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         worker.stop()

# ==================================================================================================================
# detection.py - FINAL VERSION WITH COLORED EYE & MOUTH BOXES (Green = Good, Red = Bad)
# ==================================================================================================================


# ==================================================================================================================
# detection.py – FINAL WORKING VERSION (Green = Good, Red = Alert)
# ==================================================================================================================

import cv2
import threading
import time
import numpy as np
from datetime import datetime
from tensorflow.keras.models import load_model
from pymongo import MongoClient
import os


class DetectionWorker:
    def __init__(self, camera_index=0,
                 mongo_uri="mongodb+srv://samithdarshana:1234@cluster0.wupnzmn.mongodb.net/?appName=Cluster0",
                 db_name="Smart-Classroom-App"):
        # === Load Models ===
        self.eye_model = load_model(
            "models/eye_state_cnn_224.h5")
        # self.eye_model = load_model(
        #     "models/Eye-State-Detection-DenseNet121.h5")
        # self.yawn_model = load_model("models/yawn_detector_model.h5")
        self.yawn_model = load_model("models/yawn_detector_densenet121.h5")
        self.emotion_model = load_model("models/emotion_detector_model.h5")
        self.behavior_model = load_model(
            "models/student_behavior_model_2.0.h5")

        # === Labels ===
        self.emotion_labels = ['Angry', 'Disgust',
                               'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        self.behavior_labels = ["attentive", "distracted"]

        # === Cascades ===
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml")
        self.mouth_cascade = cv2.CascadeClassifier(
            "cascades/haarcascade_mcs_mouth.xml")

        # === Thresholds ===
        self.EYE_CLOSED_THRESHOLD = 1.0
        self.YAWN_CONF_THRESHOLD = 0.5
        self.EYE_CONF_THRESHOLD = 0.5

        # === State ===
        self.camera_index = camera_index
        self.cap = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.latest = {}
        self.last_eye_closed_time = None
        self.last_alert_time = None

        # === Session & DB ===
        self.session_data = {}
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.alerts = self.db["alerts"]
        self.reports = self.db["session_reports"]

        self.snapshot_dir = "snapshots"
        os.makedirs(self.snapshot_dir, exist_ok=True)

    def _run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("Could not open webcam.")
            return

        self.session_data = {
            "start_time": time.time(),
            "end_time": None,
            "eye_closures": 0,
            "yawns": 0,
            "drowsiness_alerts": 0,
            "distraction_count": 0,
            "student_name": self.session_data.get("student_name", "Unknown")
        }

        print(f"Detection started for {self.session_data['student_name']}")

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                # Default states (prevents UnboundLocalError)
                eye_state = "unknown"
                yawning_state = "no"
                emotion_state = "unknown"
                behavior_state = "unknown"
                behavior_conf = 0.0

                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]

                    # === Emotion ===
                    try:
                        face_input = self._preprocess_face(roi_gray)
                        pred = self.emotion_model.predict(
                            face_input, verbose=0)
                        emotion_state = self.emotion_labels[np.argmax(pred)]
                    except:
                        emotion_state = "unknown"

                    # === Eyes - Green when open, Red when closed ===
                    eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.3, 5)
                    for (ex, ey, ew, eh) in eyes[:2]:
                        eye_img = roi_gray[ey:ey+eh, ex:ex+ew]
                        eye_input = self._preprocess_eye(eye_img)
                        prob = self.eye_model.predict(
                            eye_input, verbose=0)[0][0]
                        eye_state = "open" if prob > self.EYE_CONF_THRESHOLD else "closed"

                        color = (0, 255, 0) if eye_state == "open" else (
                            0, 0, 255)
                        cv2.rectangle(roi_color, (ex, ey),
                                      (ex+ew, ey+eh), color, 3)

                        # Drowsiness timing
                        if eye_state == "closed":
                            if self.last_eye_closed_time is None:
                                self.last_eye_closed_time = time.time()
                            elif time.time() - self.last_eye_closed_time >= self.EYE_CLOSED_THRESHOLD:
                                student = self.session_data["student_name"]
                                now = time.time()
                                if not self._has_unread_alert(student):
                                    if self.last_alert_time is None or (now - self.last_alert_time) >= 60:
                                        event = {
                                            "student_name": student,
                                            "timestamp": datetime.now(),
                                            "event_type": "drowsiness_alert",
                                            "status": "unread"
                                        }
                                        self.alerts.insert_one(event)
                                        print("DROWSINESS ALERT")
                                        self.session_data["drowsiness_alerts"] += 1
                                        self.last_alert_time = now
                                self.last_eye_closed_time = None
                        else:
                            self.last_eye_closed_time = None

                    # === Mouth/Yawn - Green when no yawn, Red when yawning ===
                    mouths = self.mouth_cascade.detectMultiScale(
                        roi_gray, 1.7, 11)
                    mouth_found = False
                    for (mx, my, mw, mh) in mouths:
                        if my > h // 2:  # lower half
                            mouth_img = roi_gray[my:my+mh, mx:mx+mw]
                            mouth_input = self._preprocess_mouth(mouth_img)
                            prob = self.yawn_model.predict(
                                mouth_input, verbose=0)[0][0]
                            yawning_state = "yes" if prob > self.YAWN_CONF_THRESHOLD else "no"

                            color = (0, 255, 0) if yawning_state == "no" else (
                                0, 0, 255)
                            cv2.rectangle(roi_color, (mx, my),
                                          (mx+mw, my+mh), color, 3)

                            if yawning_state == "yes":
                                self.session_data["yawns"] += 1
                            mouth_found = True
                            break
                    if not mouth_found:
                        yawning_state = "no"

                    # === Behavior (Focus) ===
                    try:
                        behavior_input = self._preprocess_behavior(frame)
                        pred = self.behavior_model.predict(
                            behavior_input, verbose=0)
                        idx = np.argmax(pred)
                        behavior_state = self.behavior_labels[idx]
                        behavior_conf = float(pred[0][idx])

                        if behavior_state == "distracted" and behavior_conf > 0.75:
                            self.session_data["distraction_count"] += 1

                        color = (0, 255, 0) if behavior_state == "attentive" else (
                            0, 0, 255)
                        cv2.putText(frame, f"Focus: {behavior_state.capitalize()} ({behavior_conf*100:.1f}%)",
                                    (x, y + h + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    except Exception as e:
                        print("Behavior model error:", e)

                    # === Face box & text overlays ===
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 3)
                    cv2.putText(frame, f"Emotion: {emotion_state}", (
                        x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(frame, f"Eye: {eye_state}", (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                (0, 255, 0) if eye_state == "open" else (0, 0, 255), 2)
                    cv2.putText(frame, f"Yawn: {yawning_state}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                (0, 255, 0) if yawning_state == "no" else (0, 0, 255), 2)

                    if self.session_data["drowsiness_alerts"] > 0:
                        cv2.putText(frame, "DROWSINESS ALERT!", (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 4)

                else:
                    cv2.putText(frame, "No Face Detected", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)

                # Update latest state
                with self.lock:
                    self.latest = {
                        "timestamp": datetime.now().isoformat(),
                        "eye_state": eye_state,
                        "yawning": yawning_state,
                        "emotion": emotion_state,
                        "behavior": behavior_state,
                        "behavior_confidence": round(behavior_conf, 3)
                    }

                cv2.imshow(
                    "Smart Classroom - Green = Good | Red = Alert", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.session_data["end_time"] = time.time()
            self._save_report_to_mongo()
            print("Detection stopped.")

    # === Preprocessing functions ===
    def _preprocess_eye(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        img = cv2.resize(img, (224, 224))
        return np.expand_dims(img.astype("float32") / 255.0, axis=0)

    def _preprocess_mouth(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        img = cv2.resize(img, (58, 56))
        return np.expand_dims(img.astype("float32") / 255.0, axis=0)

    def _preprocess_face(self, img):
        img = cv2.resize(img, (48, 48))
        img = img.astype("float32") / 255.0
        return np.expand_dims(img, axis=(0, -1))

    def _preprocess_behavior(self, frame):
        img = cv2.resize(frame, (224, 224))
        img = img.astype("float32") / 255.0
        return np.expand_dims(img, axis=0)

    # === DB helpers ===
    def _has_unread_alert(self, name):
        return self.alerts.count_documents({"student_name": name, "status": "unread"}) > 0

    def _save_report_to_mongo(self):
        if "start_time" not in self.session_data:
            return
        duration = self.session_data["end_time"] - \
            self.session_data["start_time"]
        report = {
            "student_name": self.session_data["student_name"],
            "start_time": datetime.fromtimestamp(self.session_data["start_time"]),
            "end_time": datetime.fromtimestamp(self.session_data["end_time"]),
            "session_duration_sec": round(duration, 2),
            "eye_closures": self.session_data.get("eye_closures", 0),
            "yawns": self.session_data.get("yawns", 0),
            "drowsiness_alerts": self.session_data.get("drowsiness_alerts", 0),
            "distraction_count": self.session_data.get("distraction_count", 0),
            "created_at": datetime.now()
        }
        self.reports.insert_one(report)
        print("Report saved to MongoDB")

    # === Public API ===
    def start(self, student_name):
        if self.running:
            return
        self.session_data["student_name"] = student_name
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=3)

    def get_latest(self):
        with self.lock:
            return dict(self.latest)

    def get_session_report(self):
        if "start_time" not in self.session_data:
            return {"error": "No session"}
        duration = (self.session_data.get("end_time")
                    or time.time()) - self.session_data["start_time"]
        return {
            "student_name": self.session_data["student_name"],
            "session_duration_sec": round(duration, 2),
            "yawns": self.session_data.get("yawns", 0),
            "drowsiness_alerts": self.session_data.get("drowsiness_alerts", 0),
            "distraction_count": self.session_data.get("distraction_count", 0)
        }


# === Test run ===
if __name__ == "__main__":
    worker = DetectionWorker()
    worker.start("Test Student")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        worker.stop()
