from tensorflow.keras.models import load_model
import cv2
import numpy as np

import warnings
warnings.filterwarnings("ignore")


# Load model
model = load_model('eye_state_mrl_model.h5')

# Load and preprocess image


def load_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (48, 48))
    img = img / 255.0
    img = img.reshape(1, 48, 48, 1)
    return img

# Predict


def predict_eye_state(image_path):
    img = load_image(image_path)
    pred = model.predict(img)[0][0]
    label = "Open 👁️" if pred > 0.5 else "Closed 😴"
    print(f"{image_path} => {label} ({pred:.2f})")


# Example usage
image_path = 'sample-2.jpg'  # Replace with your image path
predict_eye_state(image_path)
# predict_eye_state('mrlEyes_2018_01/test/closed/image2.png')
