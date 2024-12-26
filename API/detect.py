import cv2
import numpy as np
from flask import Flask, request, jsonify
from ultralytics import YOLO
import time

app = Flask(__name__)

# Load the YOLOv11 model
model = YOLO("yolo11m.pt")  # Ensure the model file is in the correct path

@app.route('/detect', methods=['POST'])
def detect():
    # Check if the file part is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Read the image from the uploaded file
    img_data = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    
    # Validate the image format
    if img is None:
        return jsonify({'error': 'Invalid image format'}), 400

    start_time = time.time()  # Start time for performance measurement

    # Run inference with a confidence threshold
    results = model.predict(img, conf=0.3)  # Adjust confidence threshold as needed

    detections = []
    for result in results:
        boxes = result.boxes.data  # Get bounding boxes
        for box in boxes:
            x1, y1, x2, y2, conf, class_id = box.tolist()  # Extract box coordinates and class info
            detections.append({
                'box': [int(x1), int(y1), int(x2), int(y2)],  # Bounding box coordinates
                'confidence': float(conf),  # Confidence score
                'class_id': int(class_id),  # Class ID
                'class_name': model.names[int(class_id)]  # Class name
            })

    end_time = time.time()  # End time for performance measurement
    processing_time = end_time - start_time

    # Prepare the response
    response = {
        'total_detections': len(detections),  # Total number of detections
        'detections': detections,
        'processing_time': processing_time  # Time taken for processing
    }

    return jsonify(response)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
