
# Title - 

## Overview
The **Title** is a real-time, context-aware solution designed to assist users by integrating AI functionalities such as:
- Object detection
- Text recognition (OCR)
- Speech-to-text and text-to-speech
- Face recognition
- User feedback collection for continuous improvement

This project combines modern AI tools with a user-friendly API and PWA dashboard.

---

## Features
- **Real-time Object Detection**: Identify and describe objects from a live feed.
- **OCR**: Extract and interpret text from images or camera feeds.
- **Speech Interaction**:
  - Convert speech to text for user queries.
  - Provide spoken responses using TTS.
- **User Feedback**: Collect and manage user input to improve performance.
- **Dashboard**: Manage saved results and session logs.

---

## Tech Stack
- **Backend**: Node.js, Express, MongoDB
- **AI Models**: Python (YOLOv5, Tesseract, Whisper)
- **Authentication**: Google OAuth 2.0
- **Deployment**: Docker

---

## API Endpoints
| Endpoint         | Method | Description                                |
|-------------------|--------|--------------------------------------------|
| `/api/detect`     | POST   | Detect objects in an image or live feed    |
| `/api/ocr`        | POST   | Extract text from an image                |
| `/api/ask`        | POST   | Process a user query and provide answers   |
| `/api/speech`     | POST   | Convert speech to text                    |
| `/api/speak`      | POST   | Convert text to speech                    |
| `/api/feedback`   | POST   | Submit user feedback                      |

---

## Getting Started
### Prerequisites
- Node.js (v16+)
- MongoDB
- Docker (optional)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/rabindra789/Hackerspot
   cd ai-assistant
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   - Create a `.env` file with the following:
     ```env
     GOOGLE_CLIENT_ID=your-client-id
     GOOGLE_CLIENT_SECRET=your-client-secret
     MONGO_URI=your-mongo-uri
     ```
4. Start the server:
   ```bash
   npm start
   ```

5. (Optional) Start Docker for deployment:
   ```bash
   docker-compose up --build
   ```

---

## Usage
1. Log in using Google OAuth.
2. Access APIs via the provided endpoints.
3. Manage results on the dashboard.

---

## Author
1. [Rohan Bhoi](https://github.com/RohanBhoi-7064)
2. [Swayam Kumar Sahu](https://github.com/swayam-1404)
3. [Rabindra Kumar Meher](https://github.com/rabindra789)
   
---

## Contribution
Contributions are welcome! Please fork the repository and submit a pull request.

---

## License
[MIT License](LICENSE)
