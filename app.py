from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the trained model
model = tf.keras.models.load_model("hurricane_damage_model.keras")

# Class labels
classes = ["damage", "no_damage"]


# Image preprocessing
def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((64, 64))
    img = np.array(img, dtype=np.float32)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img


@app.route("/", methods=["GET", "POST"])
def home():

    prediction = None
    confidence = None
    image = None

    if request.method == "POST":

        file = request.files["image"]

        if file and file.filename != "":

            # Safe filename
            filename = secure_filename(file.filename)

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # Save uploaded image
            file.save(filepath)

            image = filename

            # Predict
            img = preprocess_image(filepath)

            pred = model.predict(img, verbose=0)

            probability = float(pred[0][0])

            if probability >= 0.5:
                prediction = classes[1]
                confidence = probability * 100
            else:
                prediction = classes[0]
                confidence = (1 - probability) * 100

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        image=image
    )


if __name__ == "__main__":
    app.run(debug=True)