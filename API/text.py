from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import tempfile
import os

app = Flask(__name__)

def create_response(success, message=None, data=None):
    """Create a standardized JSON response."""
    response = {"success": success}
    if message:
        response["message"] = message
    if data:
        response["data"] = data
    return jsonify(response)

@app.route('/text', methods=['POST'])
def text_to_speech():
    if request.content_type != 'application/json':
        return create_response(False, "Unsupported Media Type. Please send JSON data."), 415
    
    data = request.get_json()
    
    if 'text' not in data:
        return create_response(False, "No text provided"), 400

    text = data['text']
    
    try:
        # Generate speech
        tts = gTTS(text=text, lang='en')
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            temp_file_path = temp_file.name
        
        # Return the file
        response = send_file(temp_file_path, as_attachment=True, download_name='output.mp3')
        response.call_on_close(lambda: os.remove(temp_file_path))  # Remove the file after sending
        return response
    
    except Exception as e:
        return create_response(False, f"Error generating speech: {e}"), 500

if __name__ == '__main__':
    app.run(debug=True)