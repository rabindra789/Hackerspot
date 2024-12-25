from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

# Replace the following with your MongoDB connection string
MONGO_URI = "mongodb://localhost:27017"  # Local MongoDB
# MONGO_URI = "your_mongodb_atlas_connection_string"  # For MongoDB Atlas

client = MongoClient(MONGO_URI)
db = client['feedback_db']  # Replace with your database name
feedback_collection = db['feedback']  # Replace with your collection name

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        if not data or 'user_name' not in data or 'message' not in data:
            return jsonify({"error": "Invalid input"}), 400
        
        feedback = {
            "user_name": data['user_name'],
            "message": data['message'],
            "timestamp": data.get('timestamp', None)  # Optional timestamp
        }
        
        feedback_collection.insert_one(feedback)
        return jsonify({"message": "Feedback submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback', methods=['GET'])
def get_feedback():
    try:
        feedback_list = feedback_collection.find()
        return dumps(feedback_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)