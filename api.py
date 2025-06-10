from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import time
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'asrs-python-api',
        'timestamp': time.time()
    })

# Root endpoint for debugging
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'ASRS Python API',
        'status': 'running',
        'endpoints': [
            '/api/health',
            '/api/generate',
            '/api/files/<filename>'
        ]
    })

# Alternative health check without /api prefix for compatibility
@app.route('/health', methods=['GET'])
def health_check_alt():
    return jsonify({
        'status': 'ok',
        'service': 'asrs-python-api',
        'timestamp': time.time()
    })

@app.route('/api/generate', methods=['POST'])
def generate_visualizations():
    # Get the date range from the request
    data = request.json
    start_month = data.get('startMonth')
    start_year = data.get('startYear')
    end_month = data.get('endMonth')
    end_year = data.get('endYear')
    state_filters = data.get('stateFilters')
    dark_mode = data.get('darkMode', False)
    
    # Validate the date range
    if not (start_month and start_year and end_month and end_year):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Prepare state filter suffix
    state_suffix = ""
    if state_filters and any(state_filters.values()):
        selected_states = [state for state in state_filters if state_filters[state]]
        if len(selected_states) < len(state_filters):
            state_suffix = f"_states_{len(selected_states)}"
    
    # Generate the file names with more specific naming that includes all date parameters
    human_factors_file = f'human_factors_{start_month}{start_year}-{end_month}{end_year}{state_suffix}.png'
    contributing_factors_file = f'contributing_factors_{start_month}{start_year}-{end_month}{end_year}{state_suffix}.png'
    
    # Run the data preprocessing script
    try:
        cmd = [
            'python', 'data_preprocessing.py',
            '--start-month', start_month,
            '--start-year', start_year,
            '--end-month', end_month,
            '--end-year', end_year
        ]
        
        # Add state filter if provided
        if state_filters:
            cmd.extend(['--state-filter', json.dumps(state_filters)])
        
        # Add dark mode flag if enabled
        if dark_mode:
            cmd.append('--dark-mode')
        
        print(f"Executing command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error running script: {stderr.decode('utf-8')}")
            return jsonify({'error': f'Script execution failed: {stderr.decode("utf-8")}'}), 500
        
        print(f"Script output: {stdout.decode('utf-8')}")
        
        # Check if the files were created
        human_exists = os.path.exists(human_factors_file)
        contributing_exists = os.path.exists(contributing_factors_file)
        
        print(f"Human factors file exists: {human_exists} ({human_factors_file})")
        print(f"Contributing factors file exists: {contributing_exists} ({contributing_factors_file})")
        
        if not (human_exists and contributing_exists):
            # List current directory files for debugging
            current_files = os.listdir('.')
            png_files = [f for f in current_files if f.endswith('.png')]
            print(f"Available PNG files: {png_files}")
            return jsonify({'error': 'Failed to generate visualization files'}), 500
        
        # Return the URLs to the generated files (served by this API)
        api_base_url = request.host_url.rstrip('/')
        return jsonify({
            'humanFactorsImage': f"{api_base_url}/api/files/{human_factors_file}",
            'contributingFactorsImage': f"{api_base_url}/api/files/{contributing_factors_file}"
        })
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({'error': f'Error executing script: {str(e)}'}), 500

@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    print(f"File request for: {filename}")
    
    # Validate the filename for security
    if '..' in filename or '/' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        # List available files for debugging
        png_files = [f for f in os.listdir('.') if f.endswith('.png')]
        print(f"Available PNG files: {png_files}")
        return jsonify({'error': 'File not found'}), 404
    
    print(f"Serving file: {filename}")
    # Return the file
    return send_file(filename, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug) 