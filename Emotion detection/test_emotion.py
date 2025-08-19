import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Load the model
model = load_model('emotion_detector_model.h5')

# FER-2013 emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear',
                  'Happy', 'Sad', 'Surprise', 'Neutral']


def predict_emotion(img_path):
    # Read image
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(gray, (48, 48))
    face = face.astype('float32') / 255.0
    face = np.expand_dims(face, axis=-1)  # (48,48,1)
    face = np.expand_dims(face, axis=0)   # (1,48,48,1)

    predictions = model.predict(face, verbose=0)
    emotion_idx = np.argmax(predictions)
    emotion = emotion_labels[emotion_idx]
    return emotion, img


# Folder containing test images
test_folder = 'test-images/'

for filename in os.listdir(test_folder):
    if filename.lower().endswith(('png', 'jpg', 'jpeg')):
        img_path = os.path.join(test_folder, filename)
        emotion, img = predict_emotion(img_path)

        # Convert BGR (OpenCV) to RGB (Matplotlib)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Show image with predicted label
        plt.imshow(img_rgb)
        plt.title(f"Predicted Emotion: {emotion}")
        plt.axis('off')
        plt.show()
