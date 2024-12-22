const express = require('express');
const axios = require('axios');
const router = express.Router();

// Object Detection Route
router.post('/', async (req, res) => {
  try {
    const image = req.body.image;
    const response = await axios.post('http://localhost:5001/api/detect', { image });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error detecting objects' });
  }
});

module.exports = router;
