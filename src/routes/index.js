const express = require('express');
const router = express.Router();

// Routes
router.get('/', (req, res) => {
  res.json({ message: 'Welcome to the Express backend!' });
});

// Example route
router.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from the backend!' });
});

module.exports = router; 