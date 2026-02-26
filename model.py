import tensorflow as tf
import numpy as np
from PIL import Image
import os

class_labels = [
    'Enfeksiyonel', 
    'Ekzama', 
    'Akne', 
    'Pigment', 
    'Benign', 
    'Malign'
]

IMG_SIZE = (299, 299)
MODEL_PATH_KERAS = "D:/dermainsight-main/app/skindisease.keras"

try:
    model = tf.keras.models.load_model(MODEL_PATH_KERAS)
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    raise

LOW_SPREAD_INTENSITY_THRESHOLD = 50  # % intensity

def preprocess_image(img_path):
    try:
        img = Image.open(img_path).convert("RGB")
        img = img.resize(IMG_SIZE)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

def predict_skin_disease(img_path):
    if not os.path.exists(img_path):
        return "Error", "Image file does not exist."

    img_array = preprocess_image(img_path)
    if img_array is None:
        return "Error", "Image preprocessing failed."

    try:
        prediction = model.predict(img_array)
        predicted_index = np.argmax(prediction)
        spread_intensity = float(np.max(prediction)) * 100

        predicted_class = class_labels[predicted_index]
        print(f"🔍 Raw Prediction Scores: {prediction}")

        if spread_intensity < LOW_SPREAD_INTENSITY_THRESHOLD:
            return predicted_class, round(spread_intensity, 2)

        return predicted_class, round(spread_intensity, 2)

    except Exception as e:
        return "Error", str(e)

# 🔍 Test the function
img_path = "D:/dermainsight-main/app/upload"  # Replace with your image path
result, spread_intensity = predict_skin_disease(img_path)
print(f"\n📌 Prediction: {result} (Spread Intensity: {spread_intensity}%)")
