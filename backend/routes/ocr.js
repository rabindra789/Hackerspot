const express = require('express');
const router = express.Router();
const axios = require('axios');
const multer = require('multer');

// Configure multer for file uploads
const upload = multer({ dest: 'uploads/' });

router.post('/', upload.single('image'), async (req, res) => {
  try {
    const filePath = req.file.path;

    const formData = new FormData();
    formData.append('image', fs.createReadStream(filePath));

    const response = await axios.post('http://localhost:5000/api/ocr', formData, {
      headers: formData.getHeaders(),
    });

    // Send Flask response back to client
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error processing OCR', details: error.message });
  }
});

module.exports = router;
