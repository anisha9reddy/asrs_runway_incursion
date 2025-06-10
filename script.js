document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle functionality
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    const themeLabel = document.getElementById('theme-label');
    
    // Check for saved theme preference or use default (light)
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeIcon.textContent = '🌙';
        themeLabel.textContent = 'Switch to Light Mode';
    } else {
        themeIcon.textContent = '☀️';
    }
    
    // Toggle theme when button is clicked
    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        
        // Update icon and label
        if (document.body.classList.contains('dark-theme')) {
            themeIcon.textContent = '🌙';
            themeLabel.textContent = 'Switch to Light Mode';
            localStorage.setItem('theme', 'dark');
        } else {
            themeIcon.textContent = '☀️';
            themeLabel.textContent = 'Switch to Dark Mode';
            localStorage.setItem('theme', 'light');
        }
    });

    // Page navigation
    const filtersPage = document.getElementById('filters-page');
    const visualizationsPage = document.getElementById('visualizations-page');
    const berttopicPage = document.getElementById('berttopic-page');
    const ldaPage = document.getElementById('lda-page');
    
    // Navigation buttons
    const backToFiltersBtn = document.getElementById('back-to-filters');
    const nextToBerttopicBtn = document.getElementById('next-to-berttopic');
    const nextToLdaBtn = document.getElementById('next-to-lda');
    const backToVisualizationsBtn = document.getElementById('back-to-visualizations');
    const backToVisualizationsFromLdaBtn = document.getElementById('back-to-visualizations-from-lda');
    const berttopicToLdaBtn = document.getElementById('berttopic-to-lda');
    const ldaToBerttopicBtn = document.getElementById('lda-to-berttopic');
    
    // Filter summaries
    const filtersSummary = document.getElementById('current-filters-summary');
    const berttopicFiltersSummary = document.getElementById('berttopic-filters-summary');
    const ldaFiltersSummary = document.getElementById('lda-filters-summary');
    
    // Navigation functions
    function showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show the requested page
        document.getElementById(pageId).classList.add('active');
    }
    
    // Handle back button click from visualizations to filters
    backToFiltersBtn.addEventListener('click', () => {
        showPage('filters-page');
    });

    // Handle next button click to BERTopic page
    nextToBerttopicBtn.addEventListener('click', () => {
        // No longer copy filter summary to BERTopic page
        berttopicFiltersSummary.textContent = '';
        
        // Load the default BERTopic visualization
        loadBERTTopicVisualization();
        
        // Show BERTopic page
        showPage('berttopic-page');
    });
    
    // Handle next button click to LDA page from visualizations
    nextToLdaBtn.addEventListener('click', () => {
        // No longer copy filter summary to LDA page
        ldaFiltersSummary.textContent = '';
        
        // Load the default LDA visualization
        loadLDAVisualization();
        
        // Show LDA page
        showPage('lda-page');
    });
    
    // Handle back button click from BERTopic to Visualizations
    backToVisualizationsBtn.addEventListener('click', () => {
        showPage('visualizations-page');
    });
    
    // Handle back button click from LDA to Visualizations
    backToVisualizationsFromLdaBtn.addEventListener('click', () => {
        showPage('visualizations-page');
    });
    
    // Handle navigation from BERTopic to LDA
    berttopicToLdaBtn.addEventListener('click', () => {
        // No longer copy filter summary to LDA page
        ldaFiltersSummary.textContent = '';
        
        // Load the default LDA visualization
        loadLDAVisualization();
        
        // Show LDA page
        showPage('lda-page');
    });
    
    // Handle navigation from LDA to BERTopic
    ldaToBerttopicBtn.addEventListener('click', () => {
        // No longer copy filter summary to BERTopic page
        berttopicFiltersSummary.textContent = '';
        
        // Load the default BERTopic visualization
        loadBERTTopicVisualization();
        
        // Show BERTopic page
        showPage('berttopic-page');
    });

    // BERTopic visualization handling
    const berttopicSelect = document.getElementById('berttopic-select');
    const berttopicIframe = document.getElementById('berttopic-iframe');
    
    // Load BERTopic visualization based on selection
    function loadBERTTopicVisualization() {
        const selectedOption = berttopicSelect.value;
        let visualizationPath;
        
        // Create a mapping of option values to file paths for clarity and reliability
        const pathMap = {
            '6': 'nlp_visuals/berttopic/bertopic_visualization_6_topic_2012_to_2017.html',
            '21': 'nlp_visuals/berttopic/bertopic_visualization_21_topic_2012_to_2017.html',
            '6_2018_to_2025': 'nlp_visuals/berttopic/bertopic_visualization_6_topic_2018_to_2025.html',
            '6_2001_to_2025': 'nlp_visuals/berttopic/bertopic_visualization_6_topic_2001_to_2025.html'
        };
        
        // Use the mapping or construct path dynamically if not in the map
        visualizationPath = pathMap[selectedOption];
        
        if (!visualizationPath) {
            console.error(`Path not found for option: ${selectedOption}`);
            // Fallback to a default option
            visualizationPath = 'nlp_visuals/berttopic/bertopic_visualization_6_topic_2012_to_2017.html';
        }
        
        console.log("Loading BERTopic visualization:", visualizationPath);
        berttopicIframe.src = visualizationPath;
        
        // Add event listener to center content when iframe loads
        berttopicIframe.onload = function() {
            try {
                // Access the iframe content and center it
                centerIframeContent(berttopicIframe);
            } catch (err) {
                console.error("Could not center BERTopic content:", err);
            }
        };
        
        // Add error handling for the iframe
        berttopicIframe.onerror = function() {
            console.error(`Failed to load: ${visualizationPath}`);
            alert(`Error loading visualization. Please try another option.`);
        };
    }
    
    // Handle BERTopic model selection change
    berttopicSelect.addEventListener('change', loadBERTTopicVisualization);
    
    // LDA visualization handling
    const ldaSelect = document.getElementById('lda-select');
    const ldaIframe = document.getElementById('lda-iframe');
    
    // Load LDA visualization based on selection
    function loadLDAVisualization() {
        const timePeriod = ldaSelect.value;
        const visualizationPath = `nlp_visuals/lda/lda_visualization_${timePeriod}.html`;
        ldaIframe.src = visualizationPath;
        
        // Add event listener to center content when iframe loads
        ldaIframe.onload = function() {
            try {
                // Access the iframe content and center it
                centerIframeContent(ldaIframe);
            } catch (err) {
                console.error("Could not center LDA content:", err);
            }
        };
    }
    
    // Handle LDA model selection change
    ldaSelect.addEventListener('change', loadLDAVisualization);

    // Initialize year dropdowns
    const startYearSelect = document.getElementById('start-year');
    const endYearSelect = document.getElementById('end-year');
    const startMonthSelect = document.getElementById('start-month');
    const endMonthSelect = document.getElementById('end-month');
    const generateBtn = document.getElementById('generate-btn');
    const loadingIndicator = document.getElementById('loading');
    const enableStateFilter = document.getElementById('enable-state-filter');
    const statesContainer = document.getElementById('states-container');
    const stateSearch = document.getElementById('state-search');
    const stateSearchResults = document.getElementById('state-search-results');
    const selectedStatesChips = document.getElementById('selected-states-chips');
    const selectedCount = document.getElementById('selected-count');
    const selectAllStatesBtn = document.getElementById('select-all-states');
    const clearAllStatesBtn = document.getElementById('clear-all-states');
    
    // Available year range (based on the dataset Jan1990_Jan2025.csv)
    const startYear = 1990;
    const endYear = 2025;
    
    // List of US states with abbreviations
    const states = [
        { name: "Alabama", abbr: "AL" },
        { name: "Alaska", abbr: "AK" },
        { name: "Arizona", abbr: "AZ" },
        { name: "Arkansas", abbr: "AR" },
        { name: "California", abbr: "CA" },
        { name: "Colorado", abbr: "CO" },
        { name: "Connecticut", abbr: "CT" },
        { name: "Delaware", abbr: "DE" },
        { name: "Florida", abbr: "FL" },
        { name: "Georgia", abbr: "GA" },
        { name: "Hawaii", abbr: "HI" },
        { name: "Idaho", abbr: "ID" },
        { name: "Illinois", abbr: "IL" },
        { name: "Indiana", abbr: "IN" },
        { name: "Iowa", abbr: "IA" },
        { name: "Kansas", abbr: "KS" },
        { name: "Kentucky", abbr: "KY" },
        { name: "Louisiana", abbr: "LA" },
        { name: "Maine", abbr: "ME" },
        { name: "Maryland", abbr: "MD" },
        { name: "Massachusetts", abbr: "MA" },
        { name: "Michigan", abbr: "MI" },
        { name: "Minnesota", abbr: "MN" },
        { name: "Mississippi", abbr: "MS" },
        { name: "Missouri", abbr: "MO" },
        { name: "Montana", abbr: "MT" },
        { name: "Nebraska", abbr: "NE" },
        { name: "Nevada", abbr: "NV" },
        { name: "New Hampshire", abbr: "NH" },
        { name: "New Jersey", abbr: "NJ" },
        { name: "New Mexico", abbr: "NM" },
        { name: "New York", abbr: "NY" },
        { name: "North Carolina", abbr: "NC" },
        { name: "North Dakota", abbr: "ND" },
        { name: "Ohio", abbr: "OH" },
        { name: "Oklahoma", abbr: "OK" },
        { name: "Oregon", abbr: "OR" },
        { name: "Pennsylvania", abbr: "PA" },
        { name: "Rhode Island", abbr: "RI" },
        { name: "South Carolina", abbr: "SC" },
        { name: "South Dakota", abbr: "SD" },
        { name: "Tennessee", abbr: "TN" },
        { name: "Texas", abbr: "TX" },
        { name: "Utah", abbr: "UT" },
        { name: "Vermont", abbr: "VT" },
        { name: "Virginia", abbr: "VA" },
        { name: "Washington", abbr: "WA" },
        { name: "West Virginia", abbr: "WV" },
        { name: "Wisconsin", abbr: "WI" },
        { name: "Wyoming", abbr: "WY" },
        { name: "District of Columbia", abbr: "DC" }
    ];
    
    // Set to store selected state abbreviations - start with all states selected
    const selectedStates = new Set(states.map(state => state.abbr));
    
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
    
    // Initialize state selection UI
    updateSelectedStatesDisplay();
    
    // Toggle state filter section visibility
    enableStateFilter.addEventListener('change', () => {
        if (enableStateFilter.checked) {
            statesContainer.classList.add('active');
        } else {
            statesContainer.classList.remove('active');
        }
    });
    
    // Handle state search input
    stateSearch.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        
        // Clear previous results
        stateSearchResults.innerHTML = '';
        
        if (searchTerm.length < 1) return;
        
        // Filter states based on search term
        const filteredStates = states.filter(state => 
            state.name.toLowerCase().includes(searchTerm) || 
            state.abbr.toLowerCase().includes(searchTerm)
        );
        
        // Display search results
        filteredStates.forEach(state => {
            const stateElement = document.createElement('div');
            stateElement.className = `state-result ${selectedStates.has(state.abbr) ? 'selected' : ''}`;
            stateElement.textContent = `${state.name} (${state.abbr})`;
            stateElement.dataset.abbr = state.abbr;
            
            stateElement.addEventListener('click', () => {
                toggleStateSelection(state.abbr);
                updateSelectedStatesDisplay();
                
                // Toggle selected class
                stateElement.classList.toggle('selected', selectedStates.has(state.abbr));
            });
            
            stateSearchResults.appendChild(stateElement);
        });
    });
    
    // Handle Select All button
    selectAllStatesBtn.addEventListener('click', () => {
        states.forEach(state => selectedStates.add(state.abbr));
        updateSelectedStatesDisplay();
        updateSearchResultsSelection();
    });
    
    // Handle Clear All button
    clearAllStatesBtn.addEventListener('click', () => {
        selectedStates.clear();
        updateSelectedStatesDisplay();
        updateSearchResultsSelection();
    });
    
    // Toggle state selection
    function toggleStateSelection(abbr) {
        if (selectedStates.has(abbr)) {
            selectedStates.delete(abbr);
        } else {
            selectedStates.add(abbr);
        }
    }
    
    // Update the selected states display
    function updateSelectedStatesDisplay() {
        // Clear previous chips
        selectedStatesChips.innerHTML = '';
        
        // Update count
        selectedCount.textContent = selectedStates.size;
        
        // If all states are selected, just show a message
        if (selectedStates.size === states.length) {
            const allStateChip = document.createElement('div');
            allStateChip.className = 'state-chip all-states';
            allStateChip.textContent = 'All States Selected';
            selectedStatesChips.appendChild(allStateChip);
            return;
        }
        
        // Create chips for selected states
        const sortedSelectedStates = Array.from(selectedStates)
            .map(abbr => states.find(s => s.abbr === abbr))
            .sort((a, b) => a.name.localeCompare(b.name));
        
        sortedSelectedStates.forEach(state => {
            const stateChip = document.createElement('div');
            stateChip.className = 'state-chip';
            
            const stateText = document.createElement('span');
            stateText.textContent = `${state.name} (${state.abbr})`;
            
            const removeBtn = document.createElement('span');
            removeBtn.className = 'remove-state';
            removeBtn.textContent = '×';
            removeBtn.addEventListener('click', () => {
                toggleStateSelection(state.abbr);
                updateSelectedStatesDisplay();
                updateSearchResultsSelection();
            });
            
            stateChip.appendChild(stateText);
            stateChip.appendChild(removeBtn);
            selectedStatesChips.appendChild(stateChip);
        });
    }
    
    // Update selection state in search results
    function updateSearchResultsSelection() {
        document.querySelectorAll('.state-result').forEach(el => {
            const abbr = el.dataset.abbr;
            el.classList.toggle('selected', selectedStates.has(abbr));
        });
    }
    
    // Create filters summary text
    function createFiltersSummary(startMonth, startYear, endMonth, endYear, stateFilters) {
        const monthNames = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April', 
            '05': 'May', '06': 'June', '07': 'July', '08': 'August', 
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        };
        
        let summary = `Date Range: ${monthNames[startMonth]} ${startYear} to ${monthNames[endMonth]} ${endYear}`;
        
        if (stateFilters) {
            const selectedStateCount = Object.keys(stateFilters).filter(state => stateFilters[state]).length;
            if (selectedStateCount === states.length) {
                summary += ' | States: All States';
            } else if (selectedStateCount > 0) {
                summary += ` | States: ${selectedStateCount}`;
            }
        }
        
        return summary;
    }
    
    // Handle generate button click
    generateBtn.addEventListener('click', () => {
        // Prevent multiple simultaneous requests
        if (!loadingIndicator.classList.contains('hidden')) {
            console.log('Request already in progress...');
            return;
        }
        
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
        
        // Get state filters
        let stateFilters = null;
        if (enableStateFilter.checked) {
            stateFilters = {};
            states.forEach(state => {
                stateFilters[state.abbr] = selectedStates.has(state.abbr);
            });
        }
        
        // Clear any existing visualizations and show loading message
        const humanFactorsContainer = document.getElementById('human-factors-viz');
        const contributingFactorsContainer = document.getElementById('contributing-factors-viz');
        if (humanFactorsContainer) {
            humanFactorsContainer.innerHTML = '<div class="loading-message">🔄 Generating Human Factors visualization...</div>';
        }
        if (contributingFactorsContainer) {
            contributingFactorsContainer.innerHTML = '<div class="loading-message">🔄 Generating Contributing Factors visualization...</div>';
        }
        
        // Show loading indicator (ensure it's visible)
        loadingIndicator.classList.remove('hidden');
        console.log('🔄 Loading indicator shown');
        
        // Show visualizations page first with placeholders
        showPage('visualizations-page');
        
        // Update filters summary
        filtersSummary.textContent = createFiltersSummary(startMonth, startYear, endMonth, endYear, stateFilters);
        
        // Call the API to generate visualizations
        fetchVisualizations(startMonth, startYear, endMonth, endYear, stateFilters);
    });
    
    // Validate that end date is after start date
    function validateDateRange(startMonth, startYear, endMonth, endYear) {
        const startDate = new Date(`${startYear}-${startMonth}-01`);
        const endDate = new Date(`${endYear}-${endMonth}-01`);
        return endDate >= startDate;
    }
    
    // Function to check if API is healthy with retry logic
    async function waitForApiReady(maxRetries = 30, retryInterval = 2000) {
        console.log('🔍 Checking API health...');
        
        // Add initial delay to allow services to start
        console.log('⏳ Waiting 5 seconds for services to initialize...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const healthResponse = await fetch('/api/health', {
                    method: 'GET',
                    timeout: 5000
                });
                
                if (healthResponse.ok) {
                    const healthData = await healthResponse.json();
                    console.log(`✅ API health check passed (attempt ${attempt}/${maxRetries}):`, healthData);
                    
                    // In production, also check if Python API is connected
                    if (healthData.environment === 'production' && healthData.pythonApiStatus !== 'connected') {
                        console.log(`⏳ Python API not yet connected (${healthData.pythonApiStatus}), retrying...`);
                        throw new Error(`Python API status: ${healthData.pythonApiStatus}`);
                    }
                    
                    return true;
                }
            } catch (error) {
                console.log(`⏳ API not ready yet (attempt ${attempt}/${maxRetries}): ${error.message}`);
            }
            
            if (attempt < maxRetries) {
                console.log(`🔄 Retrying in ${retryInterval/1000} seconds...`);
                
                // Show user-friendly message - don't reveal technical details for first 2 minutes
                const humanFactorsContainer = document.getElementById('human-factors-viz');
                const contributingFactorsContainer = document.getElementById('contributing-factors-viz');
                
                if (attempt * retryInterval < 120000) { // First 2 minutes (120 seconds)
                    // Show simple generating message
                    if (humanFactorsContainer) {
                        humanFactorsContainer.innerHTML = `<div class="loading-message">🔄 Generating visualizations...</div>`;
                    }
                    if (contributingFactorsContainer) {
                        contributingFactorsContainer.innerHTML = `<div class="loading-message">🔄 Generating visualizations...</div>`;
                    }
                } else if (attempt * retryInterval < 300000) { // 2-5 minutes
                    // Show that it's taking longer than usual
                    if (humanFactorsContainer) {
                        humanFactorsContainer.innerHTML = `<div class="loading-message">🔄 This is taking longer than usual, please wait...</div>`;
                    }
                    if (contributingFactorsContainer) {
                        contributingFactorsContainer.innerHTML = `<div class="loading-message">🔄 This is taking longer than usual, please wait...</div>`;
                    }
                } else {
                    // After 5 minutes, show more technical details
                    if (humanFactorsContainer) {
                        humanFactorsContainer.innerHTML = `<div class="retry-message">⏳ Services are starting up, please wait... (${Math.floor(attempt * retryInterval / 1000)}s)</div>`;
                    }
                    if (contributingFactorsContainer) {
                        contributingFactorsContainer.innerHTML = `<div class="retry-message">⏳ Services are starting up, please wait... (${Math.floor(attempt * retryInterval / 1000)}s)</div>`;
                    }
                }
                
                await new Promise(resolve => setTimeout(resolve, retryInterval));
            }
        }
        
        console.error('❌ API failed to become ready after maximum retries');
        return false;
    }

    // Function to fetch visualizations with retry logic
    async function fetchVisualizationsWithRetry(startMonth, startYear, endMonth, endYear, stateFilters, maxRetries = 10, retryInterval = 3000) {
        console.log('🚀 Starting visualization generation with retry logic...');
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                // Check if dark mode is enabled
                const isDarkMode = document.body.classList.contains('dark-theme');
                
                console.log(`📡 Sending request to API (attempt ${attempt}/${maxRetries})...`);
                const response = await fetch('/api/generate-visualizations', {
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
                        darkMode: isDarkMode
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                    throw new Error(`API returned status ${response.status}: ${errorData.error || 'Unknown error'}`);
                }
                
                console.log('✅ API response received, processing...');
                const data = await response.json();
                return data;
                
            } catch (error) {
                console.error(`❌ Attempt ${attempt} failed:`, error.message);
                
                if (attempt < maxRetries) {
                    console.log(`🔄 Retrying in ${retryInterval/1000} seconds...`);
                    
                    // Show user-friendly messages based on timing
                    const humanFactorsContainer = document.getElementById('human-factors-viz');
                    const contributingFactorsContainer = document.getElementById('contributing-factors-viz');
                    const elapsedTime = attempt * retryInterval;
                    
                    if (elapsedTime < 180000) { // First 3 minutes
                        // Keep showing simple generating message
                        if (humanFactorsContainer) {
                            humanFactorsContainer.innerHTML = `<div class="loading-message">🔄 Generating visualizations...</div>`;
                        }
                        if (contributingFactorsContainer) {
                            contributingFactorsContainer.innerHTML = `<div class="loading-message">🔄 Generating visualizations...</div>`;
                        }
                    } else if (elapsedTime < 300000) { // 3-5 minutes
                        // Show it's taking longer
                        if (humanFactorsContainer) {
                            humanFactorsContainer.innerHTML = `<div class="loading-message">🔄 Still processing, this may take a few more minutes...</div>`;
                        }
                        if (contributingFactorsContainer) {
                            contributingFactorsContainer.innerHTML = `<div class="loading-message">🔄 Still processing, this may take a few more minutes...</div>`;
                        }
                    } else {
                        // After 5 minutes, show retry information
                        if (humanFactorsContainer) {
                            humanFactorsContainer.innerHTML = `<div class="retry-message">⚠️ Processing is taking longer than expected, retrying... (${attempt}/${maxRetries})</div>`;
                        }
                        if (contributingFactorsContainer) {
                            contributingFactorsContainer.innerHTML = `<div class="retry-message">⚠️ Processing is taking longer than expected, retrying... (${attempt}/${maxRetries})</div>`;
                        }
                    }
                    
                    await new Promise(resolve => setTimeout(resolve, retryInterval));
                } else {
                    throw new Error(`Failed after ${maxRetries} attempts: ${error.message}`);
                }
            }
        }
    }

    // Function to fetch visualizations from the API
    async function fetchVisualizations(startMonth, startYear, endMonth, endYear, stateFilters) {
        console.log('🚀 Starting visualization generation...');
        
        try {
            // First, wait for API to be ready
            const apiReady = await waitForApiReady();
            if (!apiReady) {
                throw new Error('TIMEOUT: Services are taking longer than expected to start. This may happen on the first use or during high traffic periods. Please try again in a few minutes.');
            }
            
            // Then attempt to fetch visualizations with retry logic
            const data = await fetchVisualizationsWithRetry(startMonth, startYear, endMonth, endYear, stateFilters);
            displayVisualizations(data, startMonth, startYear, endMonth, endYear, stateFilters);
            console.log('🎯 Visualizations displayed successfully');
            
        } catch (error) {
            console.error('❌ Error generating visualizations:', error);
            
            // Show more specific error messages
            let errorMessage = '';
            let isTimeout = error.message.includes('TIMEOUT') || error.message.includes('Failed after') || error.message.includes('not responding');
            
            if (isTimeout) {
                errorMessage = 'The visualization service is starting up or experiencing high demand. This is normal for the first use or during busy periods. Please wait a few minutes and try again.';
            } else {
                errorMessage = 'There was a temporary issue generating the visualizations. Please try again.';
            }
            
            alert(errorMessage);
            
            // Show error state in containers
            const humanFactorsContainer = document.getElementById('human-factors-viz');
            const contributingFactorsContainer = document.getElementById('contributing-factors-viz');
            if (humanFactorsContainer) {
                humanFactorsContainer.innerHTML = '<div class="error-message">⏳ Service temporarily unavailable. Please try again in a few minutes.</div>';
            }
            if (contributingFactorsContainer) {
                contributingFactorsContainer.innerHTML = '<div class="error-message">⏳ Service temporarily unavailable. Please try again in a few minutes.</div>';
            }
            
            // Show filters page again on error
            showPage('filters-page');
        } finally {
            console.log('🔄 Hiding loading indicator...');
            loadingIndicator.classList.add('hidden');
            console.log('✅ Loading indicator hidden');
        }
    }
    
    // Function to display the visualizations
    function displayVisualizations(data, startMonth, startYear, endMonth, endYear, stateFilters) {
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
        
        // Append to containers
        humanFactorsContainer.appendChild(humanFactorsImg);
        contributingFactorsContainer.appendChild(contributingFactorsImg);
        
        // Update the headings with only the date range (removed state filter info)
        let dateRangeText = createDateRangeTitle(startMonth, startYear, endMonth, endYear);
        
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

    // Helper function to center content in iframes
    function centerIframeContent(iframe) {
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            // Create a style element
            const style = iframeDoc.createElement('style');
            style.textContent = `
                /* Center content styles */
                .plotly, .js-plotly-plot, .plot-container, .svg-container, svg, #ldavis, .container {
                    margin: 0 auto !important;
                    display: block !important;
                    text-align: center !important;
                }
                body, html {
                    text-align: center !important;
                }
            `;
            
            // Add the style to the iframe document
            iframeDoc.head.appendChild(style);
            
            console.log("Applied centering styles to iframe content");
        } catch (err) {
            console.error("Error applying centering styles:", err);
        }
    }
}); 