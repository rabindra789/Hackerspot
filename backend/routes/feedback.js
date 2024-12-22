const express = require('express');
const Feedback = require('../models/Feedback');
const router = express.Router();

// Submit Feedback Route
router.post('/', async (req, res) => {
  try {
    const { userId, feedbackText, rating } = req.body;
    const newFeedback = new Feedback({ userId, feedbackText, rating });
    await newFeedback.save();
    res.status(200).json({ message: 'Feedback submitted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Error submitting feedback' });
  }
});

module.exports = router;
