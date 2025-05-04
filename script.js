document.addEventListener('DOMContentLoaded', () => {
    // Initialize year dropdowns
    const startYearSelect = document.getElementById('start-year');
    const endYearSelect = document.getElementById('end-year');
    const startMonthSelect = document.getElementById('start-month');
    const endMonthSelect = document.getElementById('end-month');
    const generateBtn = document.getElementById('generate-btn');
    const loadingIndicator = document.getElementById('loading');
    
    // Available year range (based on the dataset Jan1990_Jan2025.csv)
    const startYear = 1990;
    const endYear = 2025;
    
    // Populate year dropdowns
    for (let year = startYear; year <= endYear; year++) {
        const startOption = document.createElement('option');
        startOption.value = year.toString();
        startOption.textContent = year.toString();
        startYearSelect.appendChild(startOption);
        
        const endOption = document.createElement('option');
        endOption.value = year.toString();
        endOption.textContent = year.toString();
        endYearSelect.appendChild(endOption);
    }
    
    // Set default selections (e.g., last 5 years)
    startYearSelect.value = '2020';
    startMonthSelect.value = '01';
    endYearSelect.value = '2025';
    endMonthSelect.value = '01';
    
    // Handle generate button click
    generateBtn.addEventListener('click', () => {
        // Get selected date range
        const startMonth = startMonthSelect.value;
        const startYear = startYearSelect.value;
        const endMonth = endMonthSelect.value;
        const endYear = endYearSelect.value;
        
        // Validate date range
        if (!validateDateRange(startMonth, startYear, endMonth, endYear)) {
            alert('Please select a valid date range (end date must be after start date)');
            return;
        }
        
        // Show loading indicator
        loadingIndicator.classList.remove('hidden');
        
        // Call the API to generate visualizations
        fetchVisualizations(startMonth, startYear, endMonth, endYear);
    });
    
    // Validate that end date is after start date
    function validateDateRange(startMonth, startYear, endMonth, endYear) {
        const startDate = new Date(`${startYear}-${startMonth}-01`);
        const endDate = new Date(`${endYear}-${endMonth}-01`);
        return endDate >= startDate;
    }
    
    // Function to fetch visualizations from the API
    async function fetchVisualizations(startMonth, startYear, endMonth, endYear) {
        try {
            const response = await fetch('/api/generate-visualizations', {
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
                throw new Error('Failed to generate visualizations');
            }
            
            const data = await response.json();
            displayVisualizations(data, startMonth, startYear, endMonth, endYear);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate visualizations. Please try again.');
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    // Function to display the visualizations
    function displayVisualizations(data, startMonth, startYear, endMonth, endYear) {
        const humanFactorsContainer = document.getElementById('human-factors-viz');
        const contributingFactorsContainer = document.getElementById('contributing-factors-viz');
        
        // Clear previous content
        humanFactorsContainer.innerHTML = '';
        contributingFactorsContainer.innerHTML = '';
        
        // Create image elements with the returned paths
        const humanFactorsImg = document.createElement('img');
        humanFactorsImg.src = data.humanFactorsImage;
        humanFactorsImg.alt = 'Human Factors';
        
        const contributingFactorsImg = document.createElement('img');
        contributingFactorsImg.src = data.contributingFactorsImage;
        contributingFactorsImg.alt = 'Contributing Factors';
        
        // Append to containers directly without titles
        humanFactorsContainer.appendChild(humanFactorsImg);
        contributingFactorsContainer.appendChild(contributingFactorsImg);
        
        // Update the headings with date range
        const dateRangeText = createDateRangeTitle(startMonth, startYear, endMonth, endYear);
        document.getElementById('human-factors-title').textContent = `Human Factors ${dateRangeText}`;
        document.getElementById('contributing-factors-title').textContent = `Contributing Factors / Situations ${dateRangeText}`;
    }
    
    // Create formatted date range title
    function createDateRangeTitle(startMonth, startYear, endMonth, endYear) {
        const monthNames = {
            '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'June',
            '07': 'July', '08': 'Aug', '09': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'
        };
        
        return `(${monthNames[startMonth]} ${startYear} - ${monthNames[endMonth]} ${endYear})`;
    }
    
    // Add responsive design considerations
    window.addEventListener('resize', () => {
        // Adjust visualization size based on window size if needed
    });
}); 