const express = require('express');
const axios = require('axios');
const multer = require('multer');
const router = express.Router();
const upload = multer({ dest: 'uploads/' });

// Speech-to-Text Route
router.post('/', upload.single('audio'), async (req, res) => {
  try {
    const audioFile = req.file;
    const formData = new FormData();
    formData.append('audio', audioFile.path);

    const response = await axios.post('http://localhost:5003/api/speech-to-text', formData, {
      headers: formData.getHeaders(),
    });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error converting speech to text' });
  }
});

module.exports = router;
