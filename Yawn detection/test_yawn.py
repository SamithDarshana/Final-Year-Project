import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Load the trained RGB model
model = load_model('yawn_detector_model.h5')


def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found at path: {image_path}")
    img = cv2.resize(img, (58, 56))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255.0
    img = img.reshape(1, 56, 58, 3)  # RGB input
    return img


def predict_yawn(image_path):
    img = load_image(image_path)
    pred = model.predict(img)[0][0]
    label = "Yawn" if pred >= 0.5 else "No Yawn"
    print(f"{image_path} => {label} ({pred:.2f})")

    # Display
    img_disp = cv2.imread(image_path)
    img_disp = cv2.cvtColor(img_disp, cv2.COLOR_BGR2RGB)
    plt.imshow(img_disp)
    plt.axis('off')
    plt.title(label)
    plt.show()


# Test
image_path = 'sample-2.jpg'
predict_yawn(image_path)
