import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load models
eye_model = load_model("eye_state_mrl_model.h5")
yawn_model = load_model("yawn_detector_model.h5")

# Load Haar cascades
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier(
    'haarcascade_mcs_mouth.xml')  # Loaded manually

# Drowsiness tracking
eye_closed_frames = 0
drowsy_threshold = 30  # frames

# Webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        roi_color = frame[y:y+h, x:x+w]
        roi_gray = gray[y:y+h, x:x+w]

        # Eye detection
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes[:1]:  # Only one eye
            eye_roi = roi_gray[ey:ey+eh, ex:ex+ew]
            eye_input = cv2.resize(eye_roi, (48, 48)) / 255.0
            eye_input = eye_input.reshape(1, 48, 48, 1)

            eye_pred = eye_model.predict(eye_input)[0][0]
            eye_label = "Open" if eye_pred > 0.5 else "Closed"
            eye_color = (0, 255, 0) if eye_label == "Open" else (0, 0, 255)

            if eye_label == "Closed":
                eye_closed_frames += 1
            else:
                eye_closed_frames = 0

            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), eye_color, 2)
            cv2.putText(frame, f"Eye: {eye_label}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, eye_color, 2)
            break

        # Drowsy alert
        if eye_closed_frames > drowsy_threshold:
            cv2.putText(frame, "DROWSINESS ALERT!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        # Mouth detection for yawning
        mouths = mouth_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.7,
            minNeighbors=20,
            minSize=(25, 25)
        )

        for (mx, my, mw, mh) in mouths:
            if my > h / 2:  # Only look at lower half of the face
                mouth_roi = roi_color[my:my+mh, mx:mx+mw]
                try:
                    mouth_input = cv2.resize(mouth_roi, (58, 56)) / 255.0
                    mouth_input = mouth_input.reshape(1, 56, 58, 3)
                    yawn_pred = yawn_model.predict(mouth_input)[0][0]
                    yawn_label = "Yawning" if yawn_pred > 0.5 else "No Yawn"
                    yawn_color = (
                        0, 0, 255) if yawn_pred > 0.5 else (0, 255, 0)
                except:
                    yawn_label = "No Yawn"
                    yawn_color = (0, 255, 0)

                cv2.rectangle(roi_color, (mx, my),
                              (mx+mw, my+mh), yawn_color, 2)
                cv2.putText(frame, f"Mouth: {yawn_label}", (x, y + h + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, yawn_color, 2)

                if yawn_pred > 0.5:
                    cv2.putText(frame, "YAWNING ALERT!", (50, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                break

    # Show webcam frame
    cv2.imshow("Drowsiness + Yawn Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
