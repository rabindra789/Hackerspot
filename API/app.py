import requests
from flask import Flask, request, jsonify
from transformers import pipeline
from PIL import Image
import pytesseract
import ffmpeg
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import cv2
import numpy as np
from bson.json_util import dumps
import io
import time
from ultralytics import YOLO

# Initialize Flask app
app = Flask(__name__)

# Backend URL (change this to your actual backend URL)
BACKEND_URL = "http://your-backend-url.com/submit-feedback"  # Replace with your backend endpoint

# Load GPT model
print("Loading GPT model...")
try:
    nlp = pipeline("text-generation", model="gpt2")
    print("GPT model loaded successfully.")
except Exception as e:
    print(f"Error loading GPT model: {e}")
    nlp = None

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load YOLOv11 model
print("Loading YOLOv11 model...")
try:
    model = YOLO("yolo11m.pt")  # Ensure the model file is in the correct path
    print("YOLOv11 model loaded successfully.")
except Exception as e:
    print(f"Error loading YOLOv11 model: {e}")
    model = None

# Route: Text Generation (ask.py functionality)
@app.route('/api/ask', methods=['POST'])
def generate_text():
    if not nlp:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    try:
        response = nlp(query, max_length=50, num_return_sequences=1)
        return jsonify({"response": response[0]['generated_text']}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: OCR (OCR.py functionality)
@app.route('/api/ocr', methods=['POST'])
def extract_text():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image)
        return jsonify({'extracted_text': text}), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred while processing the image: {str(e)}'}), 500

# Route: Speech-to-Text (speech.py functionality)
@app.route('/api/speech', methods=['POST'])
def convert_speech_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files['file']
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    wav_path = audio_path.replace('.mp3', '.wav')
    file.save(audio_path)

    try:
        ffmpeg.input(audio_path).output(wav_path).run()
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        return jsonify({"text": text}), 200
    except sr.UnknownValueError:
        return jsonify({"error": "Speech not understood"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(audio_path)
        os.remove(wav_path)

# Route: Text-to-Speech (new functionality)
@app.route('/api/speak', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '').strip()

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        tts = gTTS(text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        return jsonify({"audio_file": temp_file.name}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: Object Detection
@app.route('/api/detect', methods=['POST'])
def detect():
    if not model:
        return jsonify({'error': 'YOLO model not loaded'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    img_data = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'Invalid image format'}), 400

    start_time = time.time()

    try:
        results = model.predict(img, conf=0.3)

        detections = []
        for result in results:
            boxes = result.boxes.data
            for box in boxes:
                x1, y1, x2, y2, conf, class_id = box.tolist()
                detections.append({
                    'box': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': float(conf),
                    'class_id': int(class_id),
                    'class_name': model.names[int(class_id)]
                })

        processing_time = time.time() - start_time

        response = {
            'total_detections': len(detections),
            'detections': detections,
            'processing_time': processing_time
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Submit Feedback (POST)
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        if not data or 'user_name' not in data or 'message' not in data:
            return jsonify({"error": "Invalid input"}), 400

        feedback = {
            "user_name": data['user_name'],
            "message": data['message'],
            "timestamp": data.get('timestamp', None)
        }

        response = requests.post(BACKEND_URL, json=feedback)
        if response.status_code == 200:
            return jsonify({"message": "Feedback sent successfully!"}), 200
        else:
            return jsonify({"error": "Failed to send feedback to backend"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: Get Feedback (GET)
@app.route('/feedback', methods=['GET'])
def get_feedback():
    try:
        feedback_list = feedback_collection.find()
        return dumps(feedback_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
