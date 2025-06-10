import express from 'express';
import { exec, spawn } from 'child_process';
import path from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = process.env.PORT || 3000;
const pythonApiUrl = process.env.PYTHON_API_URL || 'http://localhost:5000';
console.log(`🔗 Python API URL: ${pythonApiUrl}`);
let pythonApiProcess = null;

// Serve static files
app.use(express.static('.'));
app.use(express.json());

// Check if data file exists
const dataFilePath = path.join(__dirname, 'Jan1990_Jan2025.csv');
console.log(`Checking for data file at: ${dataFilePath}`);
console.log(`Current working directory: ${process.cwd()}`);
console.log(`__dirname: ${__dirname}`);

if (!fs.existsSync(dataFilePath)) {
    console.error(`ERROR: Data file not found: ${dataFilePath}`);
    console.error('Please ensure the CSV data file is in the correct location');
    // List files to debug
    try {
        const files = fs.readdirSync(__dirname);
        console.log('Files in current directory:', files.filter(f => f.includes('.csv')));
    } catch (e) {
        console.error('Could not list directory files:', e);
    }
} else {
    console.log('✅ Data file found successfully');
}

// Start the Python API server
const startPythonApi = () => {
    return new Promise((resolve, reject) => {
        console.log('Starting Python API server...');
        
        // Check for Python dependencies
        exec('python -c "import flask, pandas, numpy, matplotlib"', (error, stdout, stderr) => {
            let pythonCmd = 'python';
            
            if (error) {
                console.error('Python dependencies check failed, trying python3...');
                console.error('Error:', stderr);
                
                // Try python3
                exec('python3 -c "import flask, pandas, numpy, matplotlib"', (error2) => {
                    if (error2) {
                        console.error('ERROR: Python dependencies not available');
                        reject(new Error('Python dependencies not installed'));
                        return;
                    }
                    pythonCmd = 'python3';
                    startPythonProcess(pythonCmd);
                });
                return;
            }
            
            console.log('✅ Python dependencies found');
            startPythonProcess(pythonCmd);
        });
        
        const startPythonProcess = (pythonCmd) => {
            // Launch the Python API process
            pythonApiProcess = spawn(pythonCmd, ['api.py']);
            
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
            }, 3000);
        };
    });
};

// Direct execution of Python script for testing
const testDataPreprocessing = async (startMonth, startYear, endMonth, endYear, stateFilters, darkMode) => {
    return new Promise((resolve, reject) => {
        console.log('Testing data preprocessing directly...');
        
        const args = [
            'data_preprocessing.py',
            '--start-month', startMonth,
            '--start-year', startYear,
            '--end-month', endMonth,
            '--end-year', endYear
        ];
        
        // Add state filters if provided
        if (stateFilters) {
            args.push('--state-filter', JSON.stringify(stateFilters));
        }
        
        // Add dark mode flag if enabled
        if (darkMode) {
            args.push('--dark-mode');
        }
        
        // Try python first, then python3
        let pythonCmd = 'python';
        const pythonProcess = spawn(pythonCmd, args);
        
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
    const { startMonth, startYear, endMonth, endYear, stateFilters, darkMode } = req.body;
    
    // Validate date range
    if (!startMonth || !startYear || !endMonth || !endYear) {
        return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    // Log the request
    console.log(`Generating visualizations for date range: ${startMonth}/${startYear} - ${endMonth}/${endYear}`);
    if (stateFilters) {
        const selectedStates = Object.keys(stateFilters).filter(state => stateFilters[state]);
        console.log(`State filtering enabled with ${selectedStates.length} states selected`);
    }
    
    try {
        // Prepare file suffix for state filtering
        let stateSuffix = "";
        if (stateFilters && Object.keys(stateFilters).length > 0) {
            const selectedStates = Object.keys(stateFilters).filter(state => stateFilters[state]);
            if (selectedStates.length < Object.keys(stateFilters).length) {
                stateSuffix = `_states_${selectedStates.length}`;
            }
        }
        
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
                    endYear,
                    stateFilters,
                    darkMode
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
                const result = await testDataPreprocessing(startMonth, startYear, endMonth, endYear, stateFilters, darkMode);
                
                // Check if files were generated
                const humanFactorsFile = `human_factors_${startMonth}${startYear}-${endMonth}${endYear}${stateSuffix}.png`;
                const contributingFactorsFile = `contributing_factors_${startMonth}${startYear}-${endMonth}${endYear}${stateSuffix}.png`;
                
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

// Enhanced health check endpoint with Python API connectivity test
app.get('/api/health', async (req, res) => {
    const health = {
        status: 'ok', 
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV || 'development',
        pythonApiRunning: pythonApiProcess !== null && !pythonApiProcess.killed,
        pythonApiUrl: pythonApiUrl
    };
    
    // In production, test Python API connectivity
    if (process.env.NODE_ENV === 'production') {
        try {
            console.log('Testing Python API connectivity...');
            const response = await fetch(`${pythonApiUrl}/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                const pythonHealth = await response.json();
                health.pythonApiStatus = 'connected';
                health.pythonApiDetails = pythonHealth;
                console.log('✅ Python API is responding');
            } else {
                health.pythonApiStatus = 'error';
                health.pythonApiError = `HTTP ${response.status}`;
                console.log(`⚠️ Python API returned status ${response.status}`);
            }
        } catch (error) {
            health.pythonApiStatus = 'unreachable';
            health.pythonApiError = error.message;
            console.log(`❌ Python API unreachable: ${error.message}`);
        }
    } else {
        health.pythonApiStatus = 'local';
    }
    
    res.json(health);
});

// Root health check for deployment platforms
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start the server
const startServer = async () => {
    // In production, don't start Python API locally - use external service
    if (process.env.NODE_ENV === 'production') {
        console.log('🌐 Production mode: Using external Python API service');
        console.log(`🔗 Python API URL: ${pythonApiUrl}`);
        
        app.listen(port, () => {
            console.log(`✅ Frontend server running at http://localhost:${port}`);
            console.log(`🔗 Connecting to Python API at: ${pythonApiUrl}`);
        });
    } else {
        // Development mode - start local Python API
        try {
            console.log('🐍 Development mode: Starting local Python API...');
            await startPythonApi();
            
            app.listen(port, () => {
                console.log(`✅ Development server running at http://localhost:${port}`);
                console.log('🔗 Local Python API should be running');
            });
        } catch (error) {
            console.error('Failed to start local Python API:', error);
            console.error('Starting Express server anyway...');
            
            app.listen(port, () => {
                console.log(`⚠️  Server running at http://localhost:${port} (without Python API)`);
                console.log('You can still access the health check at /api/health');
            });
        }
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