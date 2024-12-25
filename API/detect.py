import cv2
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Loading YOLO
def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    out_layers_indices = net.getUnconnectedOutLayers()
    if len(out_layers_indices) == 0:
        raise ValueError("No unconnected output layers found.")
    output_layers = [layer_names[i - 1] for i in out_layers_indices.flatten()]
    return net, output_layers

# Loading class names
def load_class_names():
    with open("coco.names", "r") as f:
        class_names = [line.strip() for line in f.readlines()]
    return class_names

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

# Initialize YOLO and class names for detection
net, output_layers = load_yolo()
class_names = load_class_names()

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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
