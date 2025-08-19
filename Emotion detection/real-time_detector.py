import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the trained model
model = load_model('emotion_detector_model.h5')

# FER-2013 emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear',
                  'Happy', 'Sad', 'Surprise', 'Neutral']

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def preprocess_face(face_img):
    face = cv2.resize(face_img, (48, 48))
    face = face.astype('float32') / 255.0
    face = np.expand_dims(face, axis=-1)   # (48,48,1)
    face = np.expand_dims(face, axis=0)    # (1,48,48,1)
    return face


# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale (model expects grayscale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]  # crop face region
        face_input = preprocess_face(roi_gray)

        # Predict emotion
        predictions = model.predict(face_input, verbose=0)
        emotion_idx = np.argmax(predictions)
        emotion = emotion_labels[emotion_idx]

        # Draw rectangle & emotion text
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, emotion, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Show result
    cv2.imshow('Real-Time Emotion Detection', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release
cap.release()
cv2.destroyAllWindows()
