from flask import Flask, request, jsonify
from gtts import gTTS
import speech_recognition as sr
import os
import tempfile
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_response(success, message=None, data=None):
    """Create a standardized JSON response."""
    response = {"success": success}
    if message:
        response["message"] = message
    if data:
        response["data"] = data
    return jsonify(response)

# Text-to-Speech endpoint
@app.route('/text', methods=['POST'])
def text_to_speech():
    logging.info("Received request for text-to-speech")
    
    # Log raw data and Content-Type
    logging.info(f"Raw data: {request.data}")
    logging.info(f"Received Content-Type: {request.content_type}")
    
    # Check Content-Type
    if request.content_type != 'application/json':
        return create_response(False, "Unsupported Media Type. Please send JSON data."), 415

    data = request.get_json()

    if 'text' not in data:
        return create_response(False, "No text provided"), 400

    text = data['text']
    output_file = "output.mp3"

    # Generate speech
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_file)
        return create_response(True, "Audio content written to file", {"output_file": output_file}), 200
    except Exception as e:
        logging.error(f"Error generating speech: {e}")
        return create_response(False, "Error generating speech"), 500

# Speech-to-Text endpoint
@app.route('/speech', methods=['POST'])
def speech_to_text():
    logging.info("Received request for speech-to-text")
    
    if 'file' not in request.files:
        return create_response(False, "No file part"), 400

    file = request.files['file']

    if file.filename == '':
        return create_response(False, "No selected file"), 400

    if not allowed_file(file.filename):
        return create_response(False, "Unsupported file type. Please upload a WAV or MP3 file."), 400

    # Use a temporary file
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_audio_file:
        file.save(temp_audio_file.name)

        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Convert audio to text
        try:
            with sr.AudioFile(temp_audio_file.name) as source:
                audio_data = recognizer.record(source)  # Capture the entire audio file
                text = recognizer.recognize_google(audio_data)
                return create_response(True, "Transcription successful", {"transcription": text}), 200
        except sr.UnknownValueError:
            return create_response(False, "Could not understand audio"), 400
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service; {e}")
            return create_response(False, f"Could not request results from Google Speech Recognition service; {e}"), 500

if __name__ == '__main__':
    app.run(debug=True)