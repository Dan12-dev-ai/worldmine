/**
 * DEDAN Mine - Main Entry Point for Vercel Build
 * This file redirects to the actual frontend entry point
 */

// Import the actual React app from the frontend directory
import App from '../frontend/src/App';

// Export the App component as default
export default App;

// Re-export everything from the actual index.js file
export * from '../frontend/src/index';
