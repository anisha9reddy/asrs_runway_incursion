import express from 'express';
import { exec, spawn } from 'child_process';
import path from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = 3000;
const pythonApiUrl = 'http://localhost:5000';
let pythonApiProcess = null;

// Serve static files
app.use(express.static('.'));
app.use(express.json());

// Check if data file exists
const dataFilePath = path.join(__dirname, 'Jan1990_Jan2025.csv');
if (!fs.existsSync(dataFilePath)) {
    console.error(`ERROR: Data file not found: ${dataFilePath}`);
    console.error('Please ensure the CSV data file is in the correct location');
}

// Start the Python API server
const startPythonApi = () => {
    return new Promise((resolve, reject) => {
        console.log('Starting Python API server...');
        
        // Check for Flask installation
        exec('python -c "import flask"', (error) => {
            if (error) {
                console.error('ERROR: Flask is not installed. Please run: pip install flask');
                console.error('You can also try: pip install -r requirements.txt');
                reject(new Error('Flask not installed'));
                return;
            }
            
            // Launch the Python API process
            pythonApiProcess = spawn('python', ['api.py']);
            
            pythonApiProcess.stdout.on('data', (data) => {
                console.log(`Python API: ${data.toString().trim()}`);
            });
            
            pythonApiProcess.stderr.on('data', (data) => {
                console.error(`Python API error: ${data.toString().trim()}`);
            });
            
            pythonApiProcess.on('error', (err) => {
                console.error('Failed to start Python API process:', err);
                reject(err);
            });
            
            pythonApiProcess.on('close', (code) => {
                if (code !== 0) {
                    console.error(`Python API process exited with code ${code}`);
                    reject(new Error(`Process exited with code ${code}`));
                }
            });
            
            // Wait for API to start
            setTimeout(() => {
                console.log('Python API server should be ready now');
                resolve(pythonApiProcess);
            }, 3000); // Give it more time to start up
        });
    });
};

// Direct execution of Python script for testing
const testDataPreprocessing = async (startMonth, startYear, endMonth, endYear) => {
    return new Promise((resolve, reject) => {
        console.log('Testing data preprocessing directly...');
        
        const pythonProcess = spawn('python', [
            'data_preprocessing.py',
            '--start-month', startMonth,
            '--start-year', startYear,
            '--end-month', endMonth,
            '--end-year', endYear
        ]);
        
        let stdout = '';
        let stderr = '';
        
        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            stdout += output + '\n';
            console.log(`Python output: ${output}`);
        });
        
        pythonProcess.stderr.on('data', (data) => {
            const output = data.toString().trim();
            stderr += output + '\n';
            console.error(`Python error: ${output}`);
        });
        
        pythonProcess.on('close', (code) => {
            if (code === 0) {
                resolve({ stdout, stderr });
            } else {
                reject(new Error(`Python process exited with code ${code}\nStdout: ${stdout}\nStderr: ${stderr}`));
            }
        });
    });
};

// API endpoint to generate visualizations
app.post('/api/generate-visualizations', async (req, res) => {
    const { startMonth, startYear, endMonth, endYear } = req.body;
    
    // Validate date range
    if (!startMonth || !startYear || !endMonth || !endYear) {
        return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    // Log the request
    console.log(`Generating visualizations for date range: ${startMonth}/${startYear} - ${endMonth}/${endYear}`);
    
    try {
        // Try using the API first
        try {
            console.log('Attempting to use Python API...');
            const response = await fetch(`${pythonApiUrl}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    startMonth,
                    startYear,
                    endMonth,
                    endYear
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Python API error:', errorData);
                throw new Error(`API returned status ${response.status}: ${JSON.stringify(errorData)}`);
            }
            
            const data = await response.json();
            console.log('Visualization generation successful:', data);
            return res.json(data);
        } catch (apiError) {
            console.error('API approach failed, trying direct script execution:', apiError);
            
            // Fall back to direct script execution
            try {
                const result = await testDataPreprocessing(startMonth, startYear, endMonth, endYear);
                
                // Check if files were generated
                const humanFactorsFile = `human_factors_${startMonth}${startYear}-${endMonth}${endYear}.png`;
                const contributingFactorsFile = `contributing_factors_${startMonth}${startYear}-${endMonth}${endYear}.png`;
                
                if (fs.existsSync(humanFactorsFile) && fs.existsSync(contributingFactorsFile)) {
                    return res.json({
                        humanFactorsImage: humanFactorsFile,
                        contributingFactorsImage: contributingFactorsFile
                    });
                } else {
                    throw new Error(`Files not generated. Output: ${result.stdout}`);
                }
            } catch (scriptError) {
                console.error('Direct script execution failed:', scriptError);
                throw scriptError;
            }
        }
    } catch (error) {
        console.error('Error generating visualizations:', error);
        return res.status(500).json({ 
            error: 'Failed to generate visualizations. Please try again.',
            details: error.message
        });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', pythonApiRunning: pythonApiProcess !== null && !pythonApiProcess.killed });
});

// Start the server
const startServer = async () => {
    try {
        // Start the Python API server
        await startPythonApi();
        
        // Start the Express server
        app.listen(port, () => {
            console.log(`Server running at http://localhost:${port}`);
            console.log('You can access the health check at http://localhost:3000/api/health');
        });
    } catch (error) {
        console.error('Failed to start servers:', error);
        console.error('Starting Express server anyway to show error information...');
        
        app.listen(port, () => {
            console.log(`Server running at http://localhost:${port} (without Python API)`);
            console.log('You can still access the health check at http://localhost:3000/api/health');
        });
    }
};

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('Shutting down servers...');
    if (pythonApiProcess) {
        pythonApiProcess.kill();
    }
    process.exit(0);
});

startServer(); 