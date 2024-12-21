require('dotenv').config();
const express = require('express');
const passport = require('passport');
const cors = require('cors');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/auth.js');
const connectDB = require('./config/db.js');
const { isLoggedIn } = require('./middlewares/checkAuth.js');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(passport.initialize());

// Routes
app.use('/api/auth',isLoggedIn ,authRoutes);

// Connect to MongoDB
connectDB();

// Start server
app.listen(process.env.PORT, () => {
  console.log(`Server running on port ${process.env.PORT}`);
});
