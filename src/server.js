import express, { json } from 'express';
import cors from 'cors';
require('dotenv').config();

import routes from './routes';

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(json());

// Use routes
app.use('/', routes);

// Start server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
}); 
