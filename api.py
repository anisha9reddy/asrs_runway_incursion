from flask import Flask, request, jsonify, send_file
import os
import subprocess
import time
import json

app = Flask(__name__)

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
        if not (os.path.exists(human_factors_file) and os.path.exists(contributing_factors_file)):
            return jsonify({'error': 'Failed to generate visualization files'}), 500
        
        # Return the paths to the generated files
        return jsonify({
            'humanFactorsImage': human_factors_file,
            'contributingFactorsImage': contributing_factors_file
        })
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({'error': f'Error executing script: {str(e)}'}), 500

@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    # Validate the filename
    if not os.path.exists(filename):
        return jsonify({'error': 'File not found'}), 404
    
    # Return the file
    return send_file(filename, mimetype='image/png')

if __name__ == '__main__':
    app.run(port=5000, debug=True) 