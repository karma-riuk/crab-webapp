import { Router } from 'express';
import datasetRoutes from './datasets.js';
import answerRoutes from './answers.js';

const router = Router();

// Routes
router.get('/', (_req, res) => {
    res.json({ message: 'Welcome to the Express backend!' });
});

// Example route
router.get('/api/hello', (_req, res) => {
    res.json({ message: 'Hello from the backend!' });
});

// Dataset routes
router.use('/datasets', datasetRoutes);

// Answer submission routes
router.use('/answers', answerRoutes);

export default router; 
