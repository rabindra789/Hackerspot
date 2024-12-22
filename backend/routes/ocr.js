const express = require('express');
const axios = require('axios');
const router = express.Router();

// OCR Route
router.post('/', async (req, res) => {
  try {
    const image = req.body.image;
    const response = await axios.post('http://localhost:5002/api/ocr', { image });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error performing OCR' });
  }
});

module.exports = router;
