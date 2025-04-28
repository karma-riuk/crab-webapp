import { Router } from 'express';
const router = Router();

// Routes
router.get('/', (_req, res) => {
    res.json({ message: 'Welcome to the Express backend!' });
});

// Example route
router.get('/api/hello', (_req, res) => {
    res.json({ message: 'Hello from the backend!' });
});

export default router; 
