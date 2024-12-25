const express = require('express');
const axios = require('axios');
const FormData = require('form-data');
const router = express.Router();

// Object Detection Route
router.post('/', async (req, res) => {
  try {
    // Check if the file is part of the request
    if (!req.files || !req.files.image) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    const imageFile = req.files.image;

    // Create FormData instance
    const form = new FormData();
    form.append('file', imageFile.data, { filename: imageFile.name });

    // Send the file to the Flask API
    const response = await axios.post('http://localhost:5001/api/detect', form, {
      headers: {
        ...form.getHeaders(),
      },
    });

    // Send the response from the Flask backend
    res.json(response.data);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error detecting objects' });
  }
});

module.exports = router;
