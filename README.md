# ASRS Runway Incursion Data Visualization

This web application displays visualizations of runway incursion data from the Aviation Safety Reporting System (ASRS) database. Users can select a date range and view generated visuals showing human factors and contributing factors to runway incursions.

## Features

- Date range selection (month and year)
- Visualization of human factors contributing to runway incursions
- Visualization of contributing factors and situations
- Responsive design for desktop and mobile devices

## Prerequisites

- Node.js (v14 or newer)
- npm (comes with Node.js)
- Python 3.6 or newer (for data processing)
- Required Python packages (see Installation section)

## Installation

1. Clone this repository or download the source code

2. Install Node.js dependencies:
   ```
   npm install
   ```

3. Install Python dependencies:
   ```
   pip install pandas numpy matplotlib
   ```

## Usage

1. Start the server:
   ```
   npm start
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:3000
   ```

3. Select a date range using the dropdown menus and click "Generate Visualizations"

## Data Processing

The application uses Python scripts to process the ASRS runway incursion data:

- `data_preprocessing.py` - Main script for data loading and processing
- `preprocessing_helpers.py` - Helper functions for data preprocessing
- `visual_helpers.py` - Functions for generating visualizations

The raw data is stored in `Jan1990_Jan2025.csv`.

## Development

For development with automatic server restart:
```
npm run dev
```

## File Structure

```
├── index.html                   # Main HTML file
├── styles.css                   # CSS styling
├── script.js                    # Client-side JavaScript
├── server.js                    # Express server
├── data_preprocessing.py        # Python data processing script
├── preprocessing_helpers.py     # Python helper functions
├── visual_helpers.py            # Visualization functions
├── Jan1990_Jan2025.csv          # Raw data file
├── human_factors_2017-2025.png  # Sample visualization
├── contributing_factors_2017-2025.png  # Sample visualization
├── package.json                 # Node.js package configuration
└── README.md                    # This file
```

## Customization

To modify the visualizations or add new ones:

1. Edit the Python scripts to include additional data processing
2. Update the JavaScript and HTML to display the new visualizations
3. Modify the CSS to adjust the styling as needed 