const express = require('express');
const Feedback = require('../models/Feedback.model'); // Import the Feedback model
const router = express.Router();

// Submit Feedback Route
router.post('/', async (req, res) => {
  try {
    const { userId, feedbackText, rating } = req.body;

    // Validate the request body to ensure all required fields are present
    if (!userId || !feedbackText || !rating) {
      return res.status(400).json({ error: 'All fields are required (userId, feedbackText, rating)' });
    }

    // Create a new feedback document
    const newFeedback = new Feedback({
      userId,
      feedbackText,
      rating
    });

    // Save the feedback to MongoDB
    await newFeedback.save();

    // Respond with a success message
    res.status(200).json({ message: 'Feedback submitted successfully' });
  } catch (error) {
    // Handle any errors that occur during the process
    res.status(500).json({ error: 'Error submitting feedback', details: error.message });
  }
});

module.exports = router;
