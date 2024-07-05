import cv2
import numpy as np

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    image = image / 255.0
    return image

if __name__ == "__main__":
    image = preprocess_image('sample_image.jpg')
    print(f"Processed Image Shape: {image.shape}")
