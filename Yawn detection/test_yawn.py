import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Load the trained RGB model
model = load_model('yawn_detector_model.h5')

image_folder = 'test_images'

# Folder to save labeled output images
save_labeled_images = False
output_folder = 'output_labeled_images'
if save_labeled_images and not os.path.exists(output_folder):
    os.makedirs(output_folder)


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
    label = "Yawn" if pred > 0.5 else "No Yawn"
    confidence = f"{pred:.2f}"
    print(f"{image_path} => {label} ({confidence})")

    # Display
    img_disp = cv2.imread(image_path)
    img_disp = cv2.cvtColor(img_disp, cv2.COLOR_BGR2RGB)
    plt.imshow(img_disp)
    plt.title(f"{label} ({confidence})")
    plt.axis('off')
    plt.show()


# 🔍 Loop over all images in the folder
for file in os.listdir(image_folder):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        full_path = os.path.join(image_folder, file)
        predict_yawn(full_path)
