from flask import Flask, request, jsonify
import ffmpeg
import speech_recognition as sr
import os

app = Flask(__name__)

@app.route('/speech', methods=['POST'])
def convert_mp3_to_text():
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # Check if the file is an MP3
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith('.mp3'):
        return jsonify({"error": "File is not an MP3"}), 400

    # Save the uploaded MP3 file
    mp3_file_path = os.path.join('uploads', file.filename)
    file.save(mp3_file_path)

    # Convert MP3 to WAV using FFMPEG
    wav_file_path = mp3_file_path.replace('.mp3', '.wav')
    ffmpeg.input(mp3_file_path).output(wav_file_path).run()

    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Convert WAV to text
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand audio"}), 400
        except sr.RequestError as e:
            return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500

    # Clean up files
    os.remove(mp3_file_path)
    os.remove(wav_file_path)

    return jsonify({"text": text}), 200

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    app.run(debug=True)