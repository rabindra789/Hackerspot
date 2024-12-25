from flask import Flask, request, jsonify
from transformers import pipeline

# Initialize the Flask application
app = Flask(__name__)

# Load the GPT model (you can change the model name as needed)
nlp = pipeline("text-generation", model="gpt2")  # You can use "gpt2", "gpt-3.5-turbo", etc.

# Define the API endpoint
@app.route('/api/ask', methods=['POST'])
def generate():
    data = request.json
    user_input = data.get('query', '')
    
    if user_input:
        # Generate a response from the model
        response = nlp(user_input, max_length=50, num_return_sequences=1)
        answer = response[0]['generated_text']
        return jsonify({"response": answer.strip()})
    
    return jsonify({"error": "No query provided"}), 400

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
