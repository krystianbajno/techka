// LinkedIn Connections Extractor - Brute Force Alphabet Approach (FIXED)
// Based on actual LinkedIn structure from sample.html
// Usage: Paste this script in browser console on LinkedIn connections page

(function() {
    console.log('🚀 LinkedIn Connections Extractor - Fixed for Current Structure...');
    
    // Configuration
    const CONFIG = {
        TARGET_PER_LETTER: 100,
        DRILL_DOWN_THRESHOLD: 95,    // If we get this many or more, drill down to 2-letter combos
        SEARCH_DELAY: 3000,
        LOAD_MORE_DELAY: 2000,
        MAX_RETRIES: 3,
        EXTRACTION_DELAY: 1000
    };
    
    // Global state
    let allConnections = [];
    let currentSearchTerm = '';
    let isRunning = false;
    let stats = {
        totalExtracted: 0,
        lettersProcessed: 0,
        twoLetterCombosProcessed: 0,
        duplicatesSkipped: 0,
        errorsEncountered: 0,
        drillDownsPerformed: 0
    };
    
    // CSS selectors based on sample.html structure
    const SELECTORS = {
        // Search input - exact from sample.html
        searchInput: '#mn-connections-search-input',
        searchInputAlt: '.mn-connections__search-input',
        
        // Connection cards - from sample.html structure
        connectionContainer: 'ul',
        connectionItem: 'li.mn-connection-card.artdeco-list',
        
        // Connection details - exact classes from sample.html
        profileLink: 'a.mn-connection-card__link',
        nameElement: '.mn-connection-card__name',
        jobElement: '.mn-connection-card__occupation', 
        timeElement: '.time-badge',
        
        // Load more button - exact from sample.html
        loadMoreButton: '.scaffold-finite-scroll__load-button',
        loadMoreButtonAlt: 'button:contains("Show more results")',
        
        // Total count
        totalCount: 'h1:contains("Connections")'
    };
    
    // Utility functions
    function log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️';
        console.log(`[${timestamp}] ${prefix} ${message}`);
    }
    
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Find search input with exact selectors from sample
    function findSearchInput() {
        let input = document.querySelector(SELECTORS.searchInput);
        if (input) {
            log(`✓ Found search input: #mn-connections-search-input`);
            return input;
        }
        
        input = document.querySelector(SELECTORS.searchInputAlt);
        if (input) {
            log(`✓ Found search input: .mn-connections__search-input`);
            return input;
        }
        
        // Fallback - any search input
        input = document.querySelector('input[placeholder*="Search by name"]');
        if (input) {
            log(`✓ Found search input by placeholder`);
            return input;
        }
        
        log('❌ Search input not found', 'error');
        return null;
    }
    
    // Extract connection data from DOM element using sample.html structure
    function extractConnectionData(connectionElement) {
        try {
            const data = {
                name: 'N/A',
                jobTitle: 'N/A',
                profileUrl: 'N/A',
                linkedinId: 'N/A',
                connectionTime: 'N/A',
                extractedAt: new Date().toISOString(),
                searchLetter: currentSearchTerm
            };
            
            // Extract profile link and name - from sample.html structure
            const profileLink = connectionElement.querySelector(SELECTORS.profileLink);
            if (profileLink) {
                data.profileUrl = profileLink.href;
                
                // Extract LinkedIn ID from URL
                const match = data.profileUrl.match(/linkedin\.com\/in\/([^\/\?]+)/);
                if (match) {
                    data.linkedinId = match[1];
                }
            }
            
            // Extract name - exact selector from sample.html
            const nameElement = connectionElement.querySelector(SELECTORS.nameElement);
            if (nameElement) {
                data.name = nameElement.textContent.trim();
            }
            
            // Extract job title - exact selector from sample.html  
            const jobElement = connectionElement.querySelector(SELECTORS.jobElement);
            if (jobElement) {
                data.jobTitle = jobElement.textContent.trim();
            }
            
            // Extract connection time - from sample.html
            const timeElement = connectionElement.querySelector(SELECTORS.timeElement);
            if (timeElement) {
                data.connectionTime = timeElement.textContent.trim();
            }
            
            return data;
        } catch (error) {
            log(`Error extracting connection data: ${error.message}`, 'error');
            stats.errorsEncountered++;
            return null;
        }
    }
    
    // Check if connection already exists (avoid duplicates)
    function isDuplicateConnection(newConnection) {
        return allConnections.some(existing => 
            (existing.linkedinId === newConnection.linkedinId && newConnection.linkedinId !== 'N/A') ||
            (existing.profileUrl === newConnection.profileUrl && newConnection.profileUrl !== 'N/A') ||
            (existing.name === newConnection.name && newConnection.name !== 'N/A')
        );
    }
    
    // Extract all visible connections on current page
    function extractVisibleConnections() {
        const connectionElements = document.querySelectorAll(SELECTORS.connectionItem);
        log(`Found ${connectionElements.length} connection elements`);
        
        let newConnections = 0;
        
        connectionElements.forEach((element, index) => {
            const connectionData = extractConnectionData(element);
            
            if (connectionData && connectionData.name !== 'N/A') {
                if (!isDuplicateConnection(connectionData)) {
                    allConnections.push(connectionData);
                    newConnections++;
                    stats.totalExtracted++;
                    
                    // Log every 10th connection for progress
                    if (newConnections % 10 === 0) {
                        log(`Progress: ${newConnections} connections for letter ${currentSearchTerm.toUpperCase()}`);
                    }
                } else {
                    stats.duplicatesSkipped++;
                }
            }
        });
        
        log(`✓ Extracted ${newConnections} new connections. Total: ${allConnections.length}`);
        return newConnections;
    }
    
    // Perform search for specific term (letter or two-letter combo)
    async function searchForTerm(term) {
        const searchInput = findSearchInput();
        if (!searchInput) {
            log('Cannot search - search input not found', 'error');
            return false;
        }
        
        currentSearchTerm = term;
        log(`🔍 Searching for: ${term.toUpperCase()}`);
        
        try {
            // Clear existing search
            searchInput.value = '';
            searchInput.focus();
            
            // Small delay before typing
            await sleep(500);
            
            // Type the term
            searchInput.value = term;
            
            // Trigger comprehensive events to ensure LinkedIn recognizes the input
            searchInput.dispatchEvent(new Event('focus', { bubbles: true }));
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            searchInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Simulate typing events
            searchInput.dispatchEvent(new KeyboardEvent('keydown', { 
                key: term.slice(-1), 
                bubbles: true, 
                cancelable: true 
            }));
            searchInput.dispatchEvent(new KeyboardEvent('keyup', { 
                key: term.slice(-1), 
                bubbles: true, 
                cancelable: true 
            }));
            
            // Wait for search results to load
            await sleep(CONFIG.SEARCH_DELAY);
            
            return true;
        } catch (error) {
            log(`Error searching for term ${term}: ${error.message}`, 'error');
            stats.errorsEncountered++;
            return false;
        }
    }
    
    // Click load more button if available
    async function clickLoadMore() {
        // Try primary selector first
        let loadMoreButton = document.querySelector(SELECTORS.loadMoreButton);
        
        if (!loadMoreButton) {
            // Try finding by text content
            const buttons = Array.from(document.querySelectorAll('button'));
            loadMoreButton = buttons.find(btn => 
                btn.textContent.toLowerCase().includes('show more') ||
                btn.textContent.toLowerCase().includes('load more')
            );
        }
        
        if (loadMoreButton && loadMoreButton.offsetParent !== null) {
            log('🔄 Clicking "Show more results" button...');
            
            // Scroll button into view
            loadMoreButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
            await sleep(500);
            
            // Click the button
            loadMoreButton.click();
            await sleep(CONFIG.LOAD_MORE_DELAY);
            
            return true;
        }
        
        log('No "Show more results" button found or not visible');
        return false;
    }
    
    // Process single letter with drill-down capability
    async function processLetter(letter) {
        if (!isRunning) return;
        
        // First, try the single letter search
        const connectionsForLetter = await processSearchTerm(letter, false);
        stats.lettersProcessed++;
        
        // Check if we should drill down to two-letter combinations
        if (connectionsForLetter >= CONFIG.DRILL_DOWN_THRESHOLD) {
            log(`🎯 Letter ${letter.toUpperCase()} yielded ${connectionsForLetter} connections (≥${CONFIG.DRILL_DOWN_THRESHOLD}). Drilling down to two-letter combinations...`, 'warning');
            
            // Process all two-letter combinations for this letter
            const additionalConnections = await processTwoLetterCombos(letter);
            
            log(`📊 Total for letter ${letter.toUpperCase()}: ${connectionsForLetter} (single) + ${additionalConnections} (combos) = ${connectionsForLetter + additionalConnections}`, 'success');
        } else {
            log(`📊 Letter ${letter.toUpperCase()}: ${connectionsForLetter} connections (no drill-down needed)`);
        }
    }
    
    // Process two-letter combinations for a given letter
    async function processTwoLetterCombos(letter) {
        if (!isRunning) return 0;
        
        const alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
        let totalCombosExtracted = 0;
        
        log(`🔽 Drilling down to two-letter combinations for letter ${letter.toUpperCase()}...`, 'warning');
        stats.drillDownsPerformed++;
        
        for (const secondLetter of alphabet) {
            if (!isRunning) break;
            
            const combo = letter + secondLetter;
            const connectionsForCombo = await processSearchTerm(combo, true);
            totalCombosExtracted += connectionsForCombo;
            stats.twoLetterCombosProcessed++;
            
            // Brief pause between combinations
            await sleep(800);
            
            // Log progress every 5 combinations
            if (stats.twoLetterCombosProcessed % 5 === 0) {
                log(`Processed ${stats.twoLetterCombosProcessed} two-letter combinations, total: ${totalCombosExtracted} connections`);
            }
        }
        
        log(`✅ Completed two-letter drill-down for ${letter.toUpperCase()}: ${totalCombosExtracted} additional connections`, 'success');
        return totalCombosExtracted;
    }
    
    // Process single search term (letter or two-letter combo) with load more cycles
    async function processSearchTerm(term, isTwoLetterCombo = false) {
        if (!isRunning) return 0;
        
        const searchSuccess = await searchForTerm(term);
        if (!searchSuccess) {
            log(`Failed to search for term ${term}`, 'error');
            return 0;
        }
        
        let connectionsForTerm = 0;
        let consecutiveNoResults = 0;
        const maxNoResults = 3;
        let loadMoreAttempts = 0;
        const maxLoadMoreAttempts = 10; // Prevent infinite loops
        
        // Initial extraction after search
        await sleep(CONFIG.EXTRACTION_DELAY);
        const initialCount = extractVisibleConnections();
        connectionsForTerm += initialCount;
        
        // Keep loading more until we hit target or no more results
        const targetForTerm = isTwoLetterCombo ? 50 : CONFIG.TARGET_PER_LETTER; // Lower target for two-letter combos
        
        while (connectionsForTerm < targetForTerm && 
               isRunning && 
               consecutiveNoResults < maxNoResults &&
               loadMoreAttempts < maxLoadMoreAttempts) {
            
            loadMoreAttempts++;
            const hasMore = await clickLoadMore();
            
            if (hasMore) {
                await sleep(CONFIG.EXTRACTION_DELAY);
                const newConnections = extractVisibleConnections();
                
                if (newConnections > 0) {
                    connectionsForTerm += newConnections;
                    consecutiveNoResults = 0;
                } else {
                    consecutiveNoResults++;
                    log(`No new connections found (attempt ${consecutiveNoResults}/${maxNoResults})`);
                }
            } else {
                log(`No more "Show more" button for term ${term.toUpperCase()}`);
                break;
            }
        }
        
        const termType = isTwoLetterCombo ? 'two-letter combo' : 'letter';
        log(`✅ Completed ${termType} ${term.toUpperCase()}: ${connectionsForTerm} connections`, 'success');
        
        return connectionsForTerm;
    }
    
    // Main alphabet processing function with enhanced drill-down capability
    async function processAlphabet() {
        const alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
        log(`🔤 Starting enhanced brute force alphabet extraction (${alphabet.length} letters with drill-down capability)`);
        log(`🎯 Drill-down threshold: ${CONFIG.DRILL_DOWN_THRESHOLD} connections`);
        
        for (const letter of alphabet) {
            if (!isRunning) {
                log('Extraction stopped by user', 'warning');
                break;
            }
            
            await processLetter(letter);
            
            // Brief pause between letters
            await sleep(1000);
        }
        
        // Clear search to show all connections
        const searchInput = findSearchInput();
        if (searchInput) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            searchInput.dispatchEvent(new Event('change', { bubbles: true }));
            await sleep(1000);
        }
        
        log('🎉 Enhanced alphabet extraction completed!', 'success');
        printStats();
        offerDownload();
    }
    
    // Print extraction statistics
    function printStats() {
        console.log('\n📊 ENHANCED EXTRACTION STATISTICS:');
        console.log('===================================');
        console.log(`Total Connections Extracted: ${stats.totalExtracted}`);
        console.log(`Letters Processed: ${stats.lettersProcessed}/26`);
        console.log(`Two-Letter Combos Processed: ${stats.twoLetterCombosProcessed}`);
        console.log(`Drill-Downs Performed: ${stats.drillDownsPerformed}`);
        console.log(`Duplicates Skipped: ${stats.duplicatesSkipped}`);
        console.log(`Errors Encountered: ${stats.errorsEncountered}`);
        if (stats.lettersProcessed > 0) {
            console.log(`Average per Letter: ${Math.round(stats.totalExtracted / stats.lettersProcessed)}`);
        }
        if (stats.twoLetterCombosProcessed > 0) {
            console.log(`Average per Two-Letter Combo: ${Math.round(stats.totalExtracted / (stats.lettersProcessed + stats.twoLetterCombosProcessed))}`);
        }
        console.log('===================================\n');
    }
    
    // Generate CSV content
    function generateCSV() {
        if (allConnections.length === 0) {
            log('No connections to export', 'warning');
            return '';
        }
        
        const headers = ['name', 'jobTitle', 'profileUrl', 'linkedinId', 'connectionTime', 'extractedAt', 'searchLetter'];
        const csvContent = [
            headers.join(','),
            ...allConnections.map(conn => 
                headers.map(header => `"${(conn[header] || '').toString().replace(/"/g, '""')}"`).join(',')
            )
        ].join('\n');
        
        return csvContent;
    }
    
    // Offer CSV download
    function offerDownload() {
        const csvContent = generateCSV();
        if (!csvContent) return;
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `linkedin_connections_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        log(`📋 CSV downloaded with ${allConnections.length} connections!`, 'success');
    }
    
    // Control functions
    window.startExtraction = function() {
        if (isRunning) {
            log('Extraction already running!', 'warning');
            return;
        }
        
        // Validate page structure
        const searchInput = findSearchInput();
        if (!searchInput) {
            log('❌ Cannot find search input. Make sure you are on the LinkedIn connections page.', 'error');
            return;
        }
        
        const connectionCards = document.querySelectorAll(SELECTORS.connectionItem);
        if (connectionCards.length === 0) {
            log('⚠️ No connection cards found. Make sure the page is fully loaded.', 'warning');
        }
        
        isRunning = true;
        stats = { 
            totalExtracted: 0, 
            lettersProcessed: 0, 
            twoLetterCombosProcessed: 0,
            duplicatesSkipped: 0, 
            errorsEncountered: 0,
            drillDownsPerformed: 0
        };
        allConnections = [];
        
        log('🚀 Starting Enhanced LinkedIn Connections Extraction with Drill-Down...');
        log(`🎯 Drill-down threshold: ${CONFIG.DRILL_DOWN_THRESHOLD} connections per letter`);
        log(`Found ${connectionCards.length} connections currently visible`);
        processAlphabet();
    };
    
    window.stopExtraction = function() {
        isRunning = false;
        log('⏹️ Extraction stopped', 'warning');
        printStats();
        if (allConnections.length > 0) {
            offerDownload();
        }
    };
    
    window.downloadConnections = function() {
        offerDownload();
    };
    
    window.getConnectionsData = function() {
        return allConnections;
    };
    
    window.getExtractionStats = function() {
        return stats;
    };
    
    window.testExtraction = function() {
        log('🧪 Testing current page structure...');
        const searchInput = findSearchInput();
        const connections = document.querySelectorAll(SELECTORS.connectionItem);
        const loadMore = document.querySelector(SELECTORS.loadMoreButton);
        
        log(`Search Input: ${searchInput ? '✅ Found' : '❌ Not found'}`);
        log(`Connection Cards: ${connections.length} found`);
        log(`Load More Button: ${loadMore ? '✅ Found' : '❌ Not found'}`);
        
        if (connections.length > 0) {
            log('🔍 Testing data extraction on first connection...');
            const testData = extractConnectionData(connections[0]);
            console.table([testData]);
        }
    };
    
    window.downloadVisibleConnections = function() {
        log('📋 Extracting and downloading visible connections...');
        
        // Extract all currently visible connections
        const connectionElements = document.querySelectorAll(SELECTORS.connectionItem);
        const visibleConnections = [];
        let successCount = 0;
        
        log(`Found ${connectionElements.length} visible connection cards`);
        
        connectionElements.forEach((element, index) => {
            const connectionData = extractConnectionData(element);
            
            if (connectionData && connectionData.name !== 'N/A') {
                // Add index for reference
                connectionData.visibleIndex = index + 1;
                connectionData.searchLetter = 'visible_only';
                visibleConnections.push(connectionData);
                successCount++;
            }
        });
        
        if (visibleConnections.length === 0) {
            log('❌ No connections found to download. Make sure you are on the LinkedIn connections page with visible connections.', 'error');
            return;
        }
        
        log(`✅ Successfully extracted ${successCount} visible connections`);
        
        // Generate CSV content for visible connections
        const headers = ['visibleIndex', 'name', 'jobTitle', 'profileUrl', 'linkedinId', 'connectionTime', 'extractedAt', 'searchLetter'];
        const csvContent = [
            headers.join(','),
            ...visibleConnections.map(conn => 
                headers.map(header => `"${(conn[header] || '').toString().replace(/"/g, '""')}"`).join(',')
            )
        ].join('\n');
        
        // Download the CSV
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `linkedin_visible_connections_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        log(`📁 Downloaded CSV with ${visibleConnections.length} visible connections!`, 'success');
        
        // Also return the data for programmatic use
        return visibleConnections;
    };
    
    window.getVisibleConnections = function() {
        log('📊 Getting visible connections data...');
        
        const connectionElements = document.querySelectorAll(SELECTORS.connectionItem);
        const visibleConnections = [];
        
        connectionElements.forEach((element, index) => {
            const connectionData = extractConnectionData(element);
            
            if (connectionData && connectionData.name !== 'N/A') {
                connectionData.visibleIndex = index + 1;
                connectionData.searchLetter = 'visible_only';
                visibleConnections.push(connectionData);
            }
        });
        
        log(`Found ${visibleConnections.length} visible connections`);
        console.table(visibleConnections.slice(0, 5)); // Show first 5 as preview
        
        return visibleConnections;
    };
    
    // Initialize
    log('✅ LinkedIn Connections Extractor (Enhanced with Drill-Down) loaded successfully!');
    log('📋 Commands:');
    log('  startExtraction()          - Begin enhanced alphabet extraction with drill-down');
    log('  stopExtraction()           - Stop current extraction');
    log('  downloadVisibleConnections() - Download currently visible connections (quick)');
    log('  getVisibleConnections()    - Get visible connections data (preview)');
    log('  testExtraction()           - Test page structure');
    log('  downloadConnections()      - Download full extraction results');
    log('  getConnectionsData()       - Get full extraction raw data');
    log('  getExtractionStats()       - View statistics');
    log('');
    log('🔥 ENHANCED FEATURES:');
    log(`  • Auto drill-down to two-letter combos when letter yields ≥${CONFIG.DRILL_DOWN_THRESHOLD} connections`);
    log('  • Searches: a, b, c... then aa, ab, ac... if needed');
    log('  • Quick download of visible connections without full extraction');
    log('  • Maximizes connection discovery per letter');
    log('\n🚀 Ready! Type startExtraction() to begin or downloadVisibleConnections() for quick export.');
    
})(); 