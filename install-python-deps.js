const { exec } = require('child_process');
const fs = require('fs');

console.log('📦 Installing Python dependencies...');

// Check if requirements.txt exists
if (!fs.existsSync('requirements.txt')) {
    console.error('❌ requirements.txt not found');
    process.exit(1);
}

// Try different Python commands
const pythonCommands = ['pip3 install -r requirements.txt', 'pip install -r requirements.txt', 'python3 -m pip install -r requirements.txt'];

async function installPythonDeps() {
    for (const cmd of pythonCommands) {
        try {
            console.log(`🔄 Trying: ${cmd}`);
            await new Promise((resolve, reject) => {
                exec(cmd, (error, stdout, stderr) => {
                    if (error) {
                        console.log(`❌ Failed: ${error.message}`);
                        reject(error);
                        return;
                    }
                    console.log('✅ Python dependencies installed successfully!');
                    console.log(stdout);
                    resolve();
                });
            });
            break; // Success, exit the loop
        } catch (error) {
            console.log(`❌ Command failed: ${cmd}`);
            continue; // Try next command
        }
    }
}

installPythonDeps().catch(() => {
    console.log('⚠️ All Python installation attempts failed. The app will run but Python features may not work.');
    process.exit(0); // Don't fail the build
}); 