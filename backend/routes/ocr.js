const express = require('express');
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const router = express.Router();

router.post('/', async (req, res) => {
    try {
        if (!req.files || !req.files.image) {
            return res.status(400).json({ error: 'No image file provided' });
          }
      
          const imageFile = req.files.image;
      

        const form = new FormData();
            form.append('image', imageFile.data, { filename: imageFile.name });
        
        const response = await axios.post('http://localhost:5001/api/ocr', form, {
            headers: { ...form.getHeaders() },
            timeout: 10000, // Timeout after 10 seconds
        });

        res.json({ extractedText: response.data.extracted_text });
    } catch (error) {
        console.error('Error processing request:', error);
        res.status(500).json({ error: 'An error occurred while processing the file', errorMessage: error.message });
    }
});

module.exports = router;
