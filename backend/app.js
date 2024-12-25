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
const fileUpload = require('express-fileupload');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
);
app.use(passport.initialize());
app.use(fileUpload());
// Routes
app.use('/api/auth' ,authRoutes);
app.use('/api/detect', detectRoutes);
app.use('/api/ocr', ocrRoutes);
app.use('/api/speech', speechRoutes);
app.use('/api/speak', speakRoutes);
app.use('/api/feedback', feedbackRoutes);


// Connect to MongoDB
connectDB();

// Start server
app.listen(process.env.PORT, () => {
  console.log(`Server running on port ${process.env.PORT}`);
});
