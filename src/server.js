const express = require('express');
const cors = require('cors');
require('dotenv').config();

const routes = require('./routes');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Use routes
app.use('/', routes);

// Start server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
}); 