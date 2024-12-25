from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

@app.route('/OCT', methods=['POST'])
def extract_text():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Read the image file
        image = Image.open(file.stream)
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        return jsonify({'extracted_text': text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)