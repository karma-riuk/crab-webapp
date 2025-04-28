import { Router } from 'express';
const router = Router();

// Routes
router.get('/', (req, res) => {
    res.json({ message: 'Welcome to the Express backend!' });
});

// Example route
router.get('/api/hello', (req, res) => {
    res.json({ message: 'Hello from the backend!' });
});

export default router; 
