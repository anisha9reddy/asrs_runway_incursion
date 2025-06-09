// Test script to check file path construction
const testOptions = [
    '6',
    '21',
    '6_2018_to_2025',
    '6_2001_to_2025'
];

for (const option of testOptions) {
    let path;
    
    if (option.includes('_')) {
        const [numTopics, ...timePeriodParts] = option.split('_');
        const timePeriod = timePeriodParts.join('_');
        path = `nlp_visuals/berttopic/bertopic_visualization_${numTopics}_topic_${timePeriod}.html`;
    } else {
        path = `nlp_visuals/berttopic/bertopic_visualization_${option}_topic_2012_to_2017.html`;
    }
    
    console.log(`Option: ${option} -> Path: ${path}`);
} 