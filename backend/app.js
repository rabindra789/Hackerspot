require('dotenv').config();
const express = require('express');
const passport = require('passport');
const cors = require('cors');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/auth.js');
const connectDB = require('./config/db.js');
const { isLoggedIn } = require('./middlewares/checkAuth.js');
const detectRoutes = require('./routes/detect');
const ocrRoutes = require('./routes/ocr');
const speechRoutes = require('./routes/speech');
const speakRoutes = require('./routes/speak');
const feedbackRoutes = require('./routes/feedback');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(passport.initialize());

// Routes
app.use('/api/auth',isLoggedIn ,authRoutes);
app.use('/api/detect', isLoggedIn, detectRoutes);
app.use('/api/ocr', isLoggedIn, ocrRoutes);
app.use('/api/speech', isLoggedIn, speechRoutes);
app.use('/api/speak', isLoggedIn, speakRoutes);
app.use('/api/feedback', isLoggedIn, feedbackRoutes);


// Connect to MongoDB
connectDB();

// Start server
app.listen(process.env.PORT, () => {
  console.log(`Server running on port ${process.env.PORT}`);
});
