import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Get the project root directory (2 levels up from src/utils)
export const PROJECT_ROOT = join(__dirname, '../..');

// Helper function to create paths relative to project root
export const getProjectPath = (relativePath) => join(PROJECT_ROOT, relativePath); 