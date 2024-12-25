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

# Initialize Flask app
app = Flask(__name__)

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

# Load YOLO model and class names
def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    out_layers_indices = net.getUnconnectedOutLayers()
    if len(out_layers_indices) == 0:
        raise ValueError("No unconnected output layers found.")
    output_layers = [layer_names[i - 1] for i in out_layers_indices.flatten()]
    return net, output_layers

def load_class_names():
    with open("coco.names", "r") as f:
        class_names = [line.strip() for line in f.readlines()]
    return class_names

# Initialize YOLO
net, output_layers = load_yolo()
class_names = load_class_names()

# Object Detection Function to detect image
def detect_objects(image, confidence_threshold=0.5):
    height, width, _ = image.shape
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    boxes, confidences, class_ids = [], [], []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confidence_threshold:
                center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype('int')
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    return boxes, confidences, class_ids

# Route: Text Generation (ask.py functionality)
@app.route('/ask', methods=['POST'])
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
@app.route('/ocr', methods=['POST'])
def extract_text():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    try:
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image)
        return jsonify({'extracted_text': text.strip()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Speech-to-Text (speech.py functionality)
@app.route('/speech', methods=['POST'])
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
@app.route('/speak', methods=['POST'])
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
@app.route('/detect', methods=['POST'])
def detect():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Reading the image
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'Invalid image format'}), 400

    boxes, confidences, class_ids = detect_objects(img)

    # Preparing response
    results = []
    for i in range(len(boxes)):
        results.append({
            'box': [int(coord) for coord in boxes[i]],  # Converting to integer
            'confidence': float(confidences[i]),  # Ensure confidence is a float
            'class_id': int(class_ids[i]),  # Converting to int
            'class_name': class_names[class_ids[i]]  # Get the class name
        })

    return jsonify(results)

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
