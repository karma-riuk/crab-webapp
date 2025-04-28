import { jest } from '@jest/globals';
import express from 'express';
import request from 'supertest';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import datasetsRouter from '../datasets.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Mock the paths utility
jest.mock('../../utils/paths.js', () => ({
    getProjectPath: (path) => join(__dirname, '../../..', path)
}));

// Create Express app for testing
const app = express();
app.use('/datasets', datasetsRouter);

describe('Datasets Router', () => {
    // Mock environment variables
    const originalEnv = process.env;
    beforeEach(() => {
        jest.resetModules();
        process.env = { ...originalEnv };
        process.env.DATA_DIR = './test-data';
    });

    afterEach(() => {
        process.env = originalEnv;
    });

    describe('GET /download/:dataset', () => {
        it('should return 400 for invalid dataset name', async () => {
            const response = await request(app)
                .get('/datasets/download/invalid_dataset')
                .expect(400);

            expect(response.body).toEqual({
                error: 'Invalid dataset name'
            });
        });

        it('should download comment_generation without context', async () => {
            const response = await request(app)
                .get('/datasets/download/comment_generation')
                .expect(200);

            expect(response.headers['content-type']).toBe('application/zip');
            expect(response.headers['content-disposition']).toContain('comment_generation_no_context.zip');
        });

        it('should download comment_generation with context', async () => {
            const response = await request(app)
                .get('/datasets/download/comment_generation')
                .query({ withContext: true })
                .expect(200);

            expect(response.headers['content-type']).toBe('application/zip');
            expect(response.headers['content-disposition']).toContain('comment_generation_with_context.zip');
        });

        it('should download code_refinement without context', async () => {
            const response = await request(app)
                .get('/datasets/download/code_refinement')
                .expect(200);

            expect(response.headers['content-type']).toBe('application/zip');
            expect(response.headers['content-disposition']).toContain('code_refinement_no_context.zip');
        });

        it('should download code_refinement with context', async () => {
            const response = await request(app)
                .get('/datasets/download/code_refinement')
                .query({ withContext: true })
                .expect(200);

            expect(response.headers['content-type']).toBe('application/zip');
            expect(response.headers['content-disposition']).toContain('code_refinement_with_context.zip');
        });

        it('should handle JSON boolean for withContext parameter', async () => {
            const response = await request(app)
                .get('/datasets/download/comment_generation')
                .query({ withContext: 'true' })
                .expect(200);

            expect(response.headers['content-disposition']).toContain('comment_generation_with_context.zip');
        });
    });
}); 