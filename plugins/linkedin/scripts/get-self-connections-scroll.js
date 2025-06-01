// LinkedIn Connections Extractor - Scroll & Load More Approach
// Based on actual LinkedIn structure from sample.html
// Continuously scrolls and clicks "Show more results" to load ALL connections
// Usage: Paste this script in browser console on LinkedIn connections page

(function() {
    console.log('🚀 LinkedIn Connections Extractor - Scroll & Load More...');
    
    // Configuration
    const CONFIG = {
        SCROLL_DELAY: 1500,          // Wait time after scrolling
        LOAD_MORE_DELAY: 2000,       // Wait time after clicking "Show more"
        EXTRACTION_DELAY: 1000,      // Wait time between extractions
        MAX_SCROLL_ATTEMPTS: 50,     // Maximum scroll attempts to prevent infinite loops
        SCROLL_DISTANCE: 1000,       // Pixels to scroll each time
        MAX_NO_PROGRESS: 5           // Stop after this many attempts with no new connections
    };
    
    // Global state
    let allConnections = [];
    let isRunning = false;
    let stats = {
        totalExtracted: 0,
        duplicatesSkipped: 0,
        errorsEncountered: 0,
        scrollAttempts: 0,
        loadMoreClicks: 0,
        noProgressCount: 0
    };
    
    // CSS selectors based on actual sample.html structure
    const SELECTORS = {
        // Connection cards - exact from sample.html
        connectionContainer: 'ul',
        connectionItem: 'li.mn-connection-card.artdeco-list',
        
        // Connection details - exact classes from sample.html
        profileLink: 'a.mn-connection-card__link',
        nameElement: '.mn-connection-card__name',
        jobElement: '.mn-connection-card__occupation', 
        timeElement: '.time-badge',
        
        // Search input - exact from sample.html
        searchInput: '#mn-connections-search-input',
        searchInputAlt: '.mn-connections__search-input',
        
        // Load more button - exact from sample.html (Show more results)
        loadMoreButton: '.scaffold-finite-scroll__load-button',
        loadMoreButtonAlt: 'button.artdeco-button--full',
        loadMoreText: 'Show more results',
        
        // Total count
        totalCount: 'h1'
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
    
    // Get total connections count from header
    function getTotalConnectionsCount() {
        const headerElement = document.querySelector(SELECTORS.totalCount);
        if (headerElement) {
            const text = headerElement.textContent;
            const match = text.match(/([0-9,]+)\s+connections/i);
            if (match) {
                return parseInt(match[1].replace(/,/g, ''));
            }
        }
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
                extractedAt: new Date().toISOString()
            };
            
            // Extract profile link - from sample.html structure
            const profileLink = connectionElement.querySelector(SELECTORS.profileLink);
            if (profileLink) {
                data.profileUrl = profileLink.href;
                
                // Extract LinkedIn ID from URL
                const match = data.profileUrl.match(/linkedin\.com\/in\/([^\/\?%]+)/);
                if (match) {
                    data.linkedinId = decodeURIComponent(match[1]);
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
        let newConnections = 0;
        let totalVisible = connectionElements.length;
        
        connectionElements.forEach((element, index) => {
            const connectionData = extractConnectionData(element);
            
            if (connectionData && connectionData.name !== 'N/A') {
                if (!isDuplicateConnection(connectionData)) {
                    allConnections.push(connectionData);
                    newConnections++;
                    stats.totalExtracted++;
                } else {
                    stats.duplicatesSkipped++;
                }
            }
        });
        
        log(`Visible: ${totalVisible} | New: ${newConnections} | Total: ${allConnections.length} | Duplicates: ${stats.duplicatesSkipped}`);
        return newConnections;
    }
    
    // Scroll down to load more connections
    async function scrollDown() {
        log('📜 Scrolling down to load more connections...');
        
        // Get current scroll position
        const beforeScroll = window.pageYOffset;
        
        // Scroll down
        window.scrollBy({
            top: CONFIG.SCROLL_DISTANCE,
            behavior: 'smooth'
        });
        
        // Wait for scroll to complete and content to load
        await sleep(CONFIG.SCROLL_DELAY);
        
        // Check if we actually scrolled
        const afterScroll = window.pageYOffset;
        const scrolled = afterScroll > beforeScroll;
        
        stats.scrollAttempts++;
        return scrolled;
    }
    
    // Click "Show more results" button if available
    async function clickShowMore() {
        // Try to find the "Show more results" button using exact LinkedIn classes
        let showMoreButton = document.querySelector(SELECTORS.loadMoreButton);
        
        if (!showMoreButton) {
            // Try alternative selector for artdeco button with full width
            showMoreButton = document.querySelector(SELECTORS.loadMoreButtonAlt);
        }
        
        if (!showMoreButton) {
            // Final fallback: look for any button containing "Show more results" text
            const allButtons = Array.from(document.querySelectorAll('button'));
            showMoreButton = allButtons.find(btn => {
                const text = btn.textContent.toLowerCase().trim();
                return text.includes('show more results') || 
                       text.includes('show more') || 
                       text.includes('load more');
            });
        }
        
        if (showMoreButton && showMoreButton.offsetParent !== null && !showMoreButton.disabled) {
            log(`🔄 Found and clicking "Show more results" button...`);
            log(`Button classes: ${showMoreButton.className}`);
            log(`Button text: "${showMoreButton.textContent.trim()}"`);
            
            // Scroll button into view first
            showMoreButton.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            
            await sleep(500);
            
            // Try multiple click methods to ensure it works
            try {
                // Method 1: Regular click
                showMoreButton.click();
                stats.loadMoreClicks++;
                log(`✅ Successfully clicked "Show more results" button (method 1)`);
            } catch (error) {
                try {
                    // Method 2: Dispatch click event
                    showMoreButton.dispatchEvent(new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    }));
                    stats.loadMoreClicks++;
                    log(`✅ Successfully clicked "Show more results" button (method 2)`);
                } catch (error2) {
                    log(`❌ Failed to click "Show more results" button: ${error2.message}`, 'error');
                    return false;
                }
            }
            
            // Wait for new content to load
            await sleep(CONFIG.LOAD_MORE_DELAY);
            
            return true;
        }
        
        log('No "Show more results" button found or not clickable');
        return false;
    }
    
    // Main extraction process - Focus on Load More + Scroll Down
    async function extractAllConnections() {
        const totalConnections = getTotalConnectionsCount();
        log(`🎯 Target: ${totalConnections ? totalConnections.toLocaleString() : 'Unknown'} total connections`);
        
        let lastConnectionCount = 0;
        let noProgressCount = 0;
        let cycleCount = 0;
        
        // Initial extraction
        log('📊 Starting initial extraction...');
        extractVisibleConnections();
        lastConnectionCount = allConnections.length;
        
        while (isRunning && 
               cycleCount < CONFIG.MAX_SCROLL_ATTEMPTS && 
               noProgressCount < CONFIG.MAX_NO_PROGRESS) {
            
            cycleCount++;
            log(`🔄 Cycle ${cycleCount}: Load More + Scroll Down...`);
            
            // STEP 1: Try to click "Load More" first (this loads more connections)
            const loadMoreClicked = await clickShowMore();
            
            if (loadMoreClicked) {
                // Wait for new content to load after clicking Load More
                await sleep(CONFIG.LOAD_MORE_DELAY);
                
                // Extract new connections that appeared
                const newFromLoadMore = extractVisibleConnections();
                log(`📥 Load More brought ${newFromLoadMore} new connections`);
            }
            
            // STEP 2: Scroll down to trigger lazy loading and reveal Load More button
            const scrolled = await scrollDown();
            
            if (scrolled) {
                // Extract any connections that appeared from scrolling
                await sleep(CONFIG.EXTRACTION_DELAY);
                const newFromScroll = extractVisibleConnections();
                log(`📜 Scrolling revealed ${newFromScroll} new connections`);
            }
            
            // Check for progress after both actions
            const currentCount = allConnections.length;
            if (currentCount > lastConnectionCount) {
                // Made progress, reset no-progress counter
                noProgressCount = 0;
                lastConnectionCount = currentCount;
                
                // Log progress every 25 connections
                if (currentCount % 25 === 0) {
                    const percentage = totalConnections ? 
                        `(${Math.round((currentCount / totalConnections) * 100)}%)` : '';
                    log(`🎯 Progress: ${currentCount.toLocaleString()} connections extracted ${percentage}`, 'success');
                }
            } else {
                // No progress made
                noProgressCount++;
                log(`⏳ No new connections found (${noProgressCount}/${CONFIG.MAX_NO_PROGRESS})`);
            }
            
            // If we couldn't load more or scroll, we might be done
            if (!loadMoreClicked && !scrolled) {
                noProgressCount++;
                log('🛑 No Load More button and cannot scroll further');
                
                // Try one more scroll to bottom to be sure
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                await sleep(2000);
                
                // Final extraction attempt
                const finalExtraction = extractVisibleConnections();
                if (finalExtraction === 0) {
                    log('✅ Reached end - no more connections available');
                    break;
                }
            }
            
            // Brief pause before next cycle
            await sleep(1000);
        }
        
        log('🎉 Extraction completed!', 'success');
        printStats();
        offerDownload();
    }
    
    // Print extraction statistics
    function printStats() {
        const totalConnections = getTotalConnectionsCount();
        const coverage = totalConnections ? 
            `${Math.round((stats.totalExtracted / totalConnections) * 100)}%` : 'Unknown';
            
        console.log('\n📊 EXTRACTION STATISTICS:');
        console.log('=========================');
        console.log(`Total Connections Found: ${totalConnections ? totalConnections.toLocaleString() : 'Unknown'}`);
        console.log(`Total Connections Extracted: ${stats.totalExtracted.toLocaleString()}`);
        console.log(`Coverage: ${coverage}`);
        console.log(`Duplicates Skipped: ${stats.duplicatesSkipped}`);
        console.log(`Errors Encountered: ${stats.errorsEncountered}`);
        console.log(`Scroll Attempts: ${stats.scrollAttempts}`);
        console.log(`"Show More" Clicks: ${stats.loadMoreClicks}`);
        console.log('=========================\n');
    }
    
    // Generate CSV content
    function generateCSV() {
        if (allConnections.length === 0) {
            log('No connections to export', 'warning');
            return '';
        }
        
        const headers = ['name', 'jobTitle', 'profileUrl', 'linkedinId', 'connectionTime', 'extractedAt'];
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
        link.setAttribute('download', `linkedin_connections_scroll_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        log(`📋 CSV downloaded with ${allConnections.length} connections!`, 'success');
    }
    
    // Control functions
    window.startScrollExtraction = function() {
        if (isRunning) {
            log('Extraction already running!', 'warning');
            return;
        }
        
        // Validate page structure
        const connectionCards = document.querySelectorAll(SELECTORS.connectionItem);
        if (connectionCards.length === 0) {
            log('❌ No connection cards found. Make sure you are on the LinkedIn connections page.', 'error');
            return;
        }
        
        // Reset state
        isRunning = true;
        stats = { 
            totalExtracted: 0, 
            duplicatesSkipped: 0, 
            errorsEncountered: 0,
            scrollAttempts: 0,
            loadMoreClicks: 0,
            noProgressCount: 0
        };
        allConnections = [];
        
        log('🚀 Starting LinkedIn Connections Extraction (Scroll Mode)...');
        log(`Found ${connectionCards.length} connections currently visible`);
        
        // Scroll to top first
        window.scrollTo({ top: 0, behavior: 'smooth' });
        setTimeout(() => {
            extractAllConnections();
        }, 1000);
    };
    
    window.stopScrollExtraction = function() {
        isRunning = false;
        log('⏹️ Extraction stopped', 'warning');
        printStats();
        if (allConnections.length > 0) {
            offerDownload();
        }
    };
    
    window.downloadScrollConnections = function() {
        offerDownload();
    };
    
    window.getScrollConnectionsData = function() {
        return allConnections;
    };
    
    window.getScrollExtractionStats = function() {
        return stats;
    };
    
    window.testScrollExtraction = function() {
        log('🧪 Testing page structure for scroll extraction...');
        const connections = document.querySelectorAll(SELECTORS.connectionItem);
        const showMore = document.querySelector(SELECTORS.loadMoreButton);
        const totalCount = getTotalConnectionsCount();
        
        log(`Total Connections Header: ${totalCount ? totalCount.toLocaleString() : 'Not found'}`);
        log(`Connection Cards: ${connections.length} found`);
        log(`"Show More" Button: ${showMore ? '✅ Found' : '❌ Not found'}`);
        
        if (connections.length > 0) {
            log('🔍 Testing data extraction on first connection...');
            const testData = extractConnectionData(connections[0]);
            console.table([testData]);
        }
        
        // Test scroll capability
        const currentScroll = window.pageYOffset;
        const maxScroll = document.body.scrollHeight - window.innerHeight;
        log(`Scroll Position: ${currentScroll} / ${maxScroll} (${Math.round((currentScroll/maxScroll)*100)}%)`);
    };
    
    window.downloadScrollVisibleConnections = function() {
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
                connectionData.extractionMethod = 'visible_only';
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
        const headers = ['visibleIndex', 'name', 'jobTitle', 'profileUrl', 'linkedinId', 'connectionTime', 'extractedAt', 'extractionMethod'];
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
        link.setAttribute('download', `linkedin_scroll_visible_connections_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        log(`📁 Downloaded CSV with ${visibleConnections.length} visible connections!`, 'success');
        
        // Also return the data for programmatic use
        return visibleConnections;
    };
    
    window.getScrollVisibleConnections = function() {
        log('📊 Getting visible connections data...');
        
        const connectionElements = document.querySelectorAll(SELECTORS.connectionItem);
        const visibleConnections = [];
        
        connectionElements.forEach((element, index) => {
            const connectionData = extractConnectionData(element);
            
            if (connectionData && connectionData.name !== 'N/A') {
                connectionData.visibleIndex = index + 1;
                connectionData.extractionMethod = 'visible_only';
                visibleConnections.push(connectionData);
            }
        });
        
        log(`Found ${visibleConnections.length} visible connections`);
        console.table(visibleConnections.slice(0, 5)); // Show first 5 as preview
        
        return visibleConnections;
    };
    
    // Initialize
    log('✅ LinkedIn Connections Scroll Extractor loaded successfully!');
    log('📋 Commands:');
    log('  startScrollExtraction()      - Begin scroll & load more extraction');
    log('  stopScrollExtraction()       - Stop current extraction');
    log('  downloadScrollVisibleConnections() - Download visible connections (quick)');
    log('  getScrollVisibleConnections() - Get visible connections data (preview)');
    log('  testScrollExtraction()       - Test page structure');
    log('  downloadScrollConnections()  - Download full extraction results');
    log('  getScrollConnectionsData()   - Get full extraction raw data');
    log('  getScrollExtractionStats()   - View statistics');
    log('');
    log('🔥 FEATURES:');
    log('  • Scroll down and click "Show more results" automatically');
    log('  • Extract ALL connections without search limitations');
    log('  • Quick download of currently visible connections');
    log('  • Real-time progress tracking and statistics');
    log('\n🚀 Ready! Type startScrollExtraction() to begin or downloadScrollVisibleConnections() for quick export.');
    
})(); 