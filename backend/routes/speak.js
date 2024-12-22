const express = require('express');
const axios = require('axios');
const router = express.Router();

// Text-to-Speech Route
router.post('/', async (req, res) => {
  try {
    const text = req.body.text;
    const response = await axios.post('http://localhost:5004/api/speak', { text });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error converting text to speech' });
  }
});

module.exports = router;
