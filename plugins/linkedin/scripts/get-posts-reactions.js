/**
 * LinkedIn Reactions Extractor (Browser DevTools)
 * Extracts user reactions from LinkedIn HTML page and saves as CSV
 * Run this in browser developer tools console
 */

class LinkedInReactionsExtractor {
    constructor() {
        this.reactions = [];
    }

    /**
     * Clean and normalize text content
     */
    cleanText(text) {
        if (!text) return "";
        
        // Remove extra whitespace and newlines
        text = text.replace(/\s+/g, ' ');
        // Decode HTML entities
        const textarea = document.createElement('textarea');
        textarea.innerHTML = text;
        text = textarea.value;
        // Strip leading/trailing whitespace
        return text.trim();
    }

    /**
     * Extract post information from the feed update container
     */
    extractPostInfo(feedUpdateElement) {
        const postInfo = {
            post_author: "",
            post_author_title: "",
            post_author_profile_url: "",
            post_content: "",
            post_url: "",
            post_timestamp: ""
        };

        try {
            // Extract post author name and profile URL
            const authorNameElement = feedUpdateElement.querySelector('.update-components-actor__title .hoverable-link-text');
            const authorLinkElement = feedUpdateElement.querySelector('.update-components-actor__meta-link');
            
            if (authorNameElement) {
                postInfo.post_author = this.cleanText(authorNameElement.textContent);
            }
            
            if (authorLinkElement && authorLinkElement.href) {
                postInfo.post_author_profile_url = authorLinkElement.href;
            }

            // Extract post author title/description
            const authorDescElement = feedUpdateElement.querySelector('.update-components-actor__description');
            if (authorDescElement) {
                postInfo.post_author_title = this.cleanText(authorDescElement.textContent);
            }

            // Extract post timestamp
            const timestampElement = feedUpdateElement.querySelector('.update-components-actor__sub-description');
            if (timestampElement) {
                const timestampText = timestampElement.textContent;
                // Extract time part (before the visibility info)
                const timeMatch = timestampText.match(/^([^•]+)/);
                if (timeMatch) {
                    postInfo.post_timestamp = this.cleanText(timeMatch[1]);
                }
            }

            // Extract post content
            const postContentElement = feedUpdateElement.querySelector('.update-components-text');
            if (postContentElement) {
                let text = "";
                const walker = document.createTreeWalker(
                    postContentElement,
                    NodeFilter.SHOW_ALL
                );
                
                let node;
                while (node = walker.nextNode()) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        text += node.textContent;
                    } else if (node.nodeName === 'BR') {
                        text += '\n';
                    }
                }
                postInfo.post_content = this.cleanText(text);
            }

            // Try to extract post URL from permalink - multiple methods
            // The data-urn is on the feedUpdateElement itself
            const urn = feedUpdateElement.getAttribute('data-urn');
            if (urn) {
                // Extract activity ID from URN like "urn:li:activity:7327743543861469184"
                const activityMatch = urn.match(/activity:(\d+)/);
                if (activityMatch) {
                    const activityId = activityMatch[1];
                    postInfo.post_url = `https://www.linkedin.com/feed/update/urn:li:activity:${activityId}/`;
                }
            }

            // Alternative method: look for any element with data-urn within the feed update
            if (!postInfo.post_url) {
                const permalinkElement = feedUpdateElement.querySelector('[data-urn]');
                if (permalinkElement) {
                    const urn = permalinkElement.getAttribute('data-urn');
                    if (urn) {
                        const activityMatch = urn.match(/activity:(\d+)/);
                        if (activityMatch) {
                            const activityId = activityMatch[1];
                            postInfo.post_url = `https://www.linkedin.com/feed/update/urn:li:activity:${activityId}/`;
                        }
                    }
                }
            }

            // Third method: look for permalink in header or other elements
            if (!postInfo.post_url) {
                const timeElements = feedUpdateElement.querySelectorAll('time');
                timeElements.forEach(timeEl => {
                    const parent = timeEl.closest('a');
                    if (parent && parent.href && parent.href.includes('feed/update')) {
                        postInfo.post_url = parent.href;
                    }
                });
            }

        } catch (error) {
            console.warn("Error extracting post info:", error);
        }

        return postInfo;
    }

    /**
     * Extract reaction information from the reaction header
     */
    extractReactionInfo(feedUpdateElement) {
        const reactionInfo = {
            reactor_name: "",
            reactor_profile_url: "",
            reaction_type: "",
            reaction_text: ""
        };

        try {
            // Extract reaction header text which contains the reaction information
            const headerTextElement = feedUpdateElement.querySelector('.update-components-header__text-view');
            if (headerTextElement) {
                const fullText = this.cleanText(headerTextElement.textContent);
                reactionInfo.reaction_text = fullText;

                // Extract reaction type from the text (e.g., "loves this", "liked this", "celebrates this")
                if (fullText.includes('loves this')) {
                    reactionInfo.reaction_type = 'love';
                } else if (fullText.includes('liked this')) {
                    reactionInfo.reaction_type = 'like';
                } else if (fullText.includes('celebrates this')) {
                    reactionInfo.reaction_type = 'celebrate';
                } else if (fullText.includes('supports this')) {
                    reactionInfo.reaction_type = 'support';
                } else if (fullText.includes('finds this insightful')) {
                    reactionInfo.reaction_type = 'insightful';
                } else if (fullText.includes('finds this funny')) {
                    reactionInfo.reaction_type = 'funny';
                } else {
                    // Try to extract from the end of the text
                    const words = fullText.split(' ');
                    const lastWords = words.slice(-2).join(' ');
                    reactionInfo.reaction_type = lastWords;
                }

                // Extract reactor name (should be at the beginning)
                const nameLink = headerTextElement.querySelector('a');
                if (nameLink) {
                    reactionInfo.reactor_name = this.cleanText(nameLink.textContent);
                    reactionInfo.reactor_profile_url = nameLink.href || "";
                }
            }

            // Also check the header image link for reactor info
            const headerImageLink = feedUpdateElement.querySelector('.update-components-header__image a');
            if (headerImageLink && !reactionInfo.reactor_name) {
                // Extract from aria-label or href
                const ariaLabel = headerImageLink.getAttribute('aria-label');
                if (ariaLabel) {
                    const nameMatch = ariaLabel.match(/View (.+?)'s/);
                    if (nameMatch) {
                        reactionInfo.reactor_name = nameMatch[1];
                    }
                }
                reactionInfo.reactor_profile_url = headerImageLink.href || "";
            }

        } catch (error) {
            console.warn("Error extracting reaction info:", error);
        }

        return reactionInfo;
    }

    /**
     * Extract all reactions from the current page
     */
    extractReactions() {
        console.log("🔄 Extracting reactions from current page...");
        const reactions = [];
        
        // Find all feed update containers
        const feedUpdates = document.querySelectorAll('.feed-shared-update-v2');
        
        console.log(`📊 Found ${feedUpdates.length} feed updates`);
        
        feedUpdates.forEach((feedUpdate, feedIdx) => {
            try {
                // Extract post information for this feed update
                const postInfo = this.extractPostInfo(feedUpdate);
                
                // Extract reaction information
                const reactionInfo = this.extractReactionInfo(feedUpdate);
                
                // Only process if we have reaction information
                if (reactionInfo.reactor_name || reactionInfo.reaction_type) {
                    const reactionData = {
                        reaction_id: reactions.length + 1,
                        feed_update_id: feedIdx + 1,
                        post_author: postInfo.post_author,
                        post_author_title: postInfo.post_author_title,
                        post_author_profile_url: postInfo.post_author_profile_url,
                        post_content: postInfo.post_content.substring(0, 500) + (postInfo.post_content.length > 500 ? '...' : ''),
                        post_timestamp: postInfo.post_timestamp,
                        post_url: postInfo.post_url,
                        reactor_name: reactionInfo.reactor_name,
                        reactor_profile_url: reactionInfo.reactor_profile_url,
                        reaction_type: reactionInfo.reaction_type,
                        reaction_text: reactionInfo.reaction_text,
                        extracted_timestamp: new Date().toISOString()
                    };
                    
                    reactions.push(reactionData);
                    console.log(`✓ Extracted reaction ${reactions.length}: ${reactionData.reactor_name} ${reactionData.reaction_type} post by ${reactionData.post_author}`);
                }
                
            } catch (error) {
                console.warn(`⚠️  Error processing feed update ${feedIdx + 1}:`, error);
            }
        });
        
        console.log(`✅ Successfully extracted ${reactions.length} reactions`);
        this.reactions = reactions;
        return reactions;
    }

    /**
     * Convert data to CSV format
     */
    convertToCSV() {
        if (this.reactions.length === 0) {
            console.warn("⚠️  No reactions to convert. Run extractReactions() first.");
            return "";
        }
        
        const headers = [
            'reaction_id', 'feed_update_id', 'post_author', 'post_author_title', 'post_author_profile_url', 'post_content',
            'post_timestamp', 'post_url', 'reactor_name', 'reactor_profile_url',
            'reaction_type', 'reaction_text', 'extracted_timestamp'
        ];
        
        // Helper function to escape CSV values
        const escapeCSV = (value) => {
            if (value === null || value === undefined) return '';
            const str = String(value);
            if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
                return `"${str.replace(/"/g, '""')}"`;
            }
            return str;
        };
        
        // Create CSV content
        let csvContent = headers.join(',') + '\n';
        
        this.reactions.forEach(reaction => {
            const row = headers.map(header => escapeCSV(reaction[header])).join(',');
            csvContent += row + '\n';
        });
        
        return csvContent;
    }

    /**
     * Download CSV file
     */
    downloadCSV(filename = 'linkedin_reactions.csv') {
        const csvContent = this.convertToCSV();
        if (!csvContent) return;
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            console.log(`📁 CSV file downloaded as: ${filename}`);
        } else {
            console.error('❌ Download not supported in this browser');
        }
    }

    /**
     * Copy CSV to clipboard
     */
    async copyToClipboard() {
        const csvContent = this.convertToCSV();
        if (!csvContent) return;
        
        try {
            await navigator.clipboard.writeText(csvContent);
            console.log('📋 CSV content copied to clipboard!');
        } catch (error) {
            console.error('❌ Failed to copy to clipboard:', error);
            // Fallback: show the content in console
            console.log('📄 CSV Content:');
            console.log(csvContent);
        }
    }

    /**
     * Print a summary of extracted reactions
     */
    printSummary() {
        if (this.reactions.length === 0) {
            console.log("No reactions extracted.");
            return;
        }
        
        const totalReactions = this.reactions.length;
        const uniquePosters = new Set(this.reactions.map(r => r.post_author)).size;
        const uniqueReactors = new Set(this.reactions.map(r => r.reactor_name)).size;
        const reactionTypes = {};
        
        // Count reaction types
        this.reactions.forEach(reaction => {
            const type = reaction.reaction_type || 'unknown';
            reactionTypes[type] = (reactionTypes[type] || 0) + 1;
        });
        
        console.log('\n❤️ REACTIONS EXTRACTION SUMMARY');
        console.log('='.repeat(60));
        console.log(`Total reactions extracted: ${totalReactions}`);
        console.log(`Unique post authors: ${uniquePosters}`);
        console.log(`Unique reactors: ${uniqueReactors}`);
        console.log('='.repeat(60));
        
        console.log('\n📊 REACTION TYPES:');
        console.log('-'.repeat(40));
        Object.entries(reactionTypes)
            .sort(([,a], [,b]) => b - a)
            .forEach(([type, count]) => {
                console.log(`${type}: ${count}`);
            });
        
        console.log('\n📝 SAMPLE REACTIONS:');
        console.log('-'.repeat(60));
        
        this.reactions.slice(0, 3).forEach((reaction, i) => {
            console.log(`${i + 1}. ${reaction.reactor_name} ${reaction.reaction_type} post by ${reaction.post_author}`);
            console.log(`   Post: "${reaction.post_content.substring(0, 80)}..."`);
            console.log(`   Time: ${reaction.post_timestamp}`);
            console.log(`   Full reaction: "${reaction.reaction_text}"\n`);
        });
    }

    /**
     * Get reactions as array of objects
     */
    getReactions() {
        return this.reactions;
    }

    /**
     * Filter reactions by type
     */
    getReactionsByType(type) {
        return this.reactions.filter(r => r.reaction_type === type);
    }

    /**
     * Get reactions by specific user
     */
    getReactionsByUser(userName) {
        return this.reactions.filter(r => 
            r.reactor_name.toLowerCase().includes(userName.toLowerCase())
        );
    }

    /**
     * Get reactions to posts by specific author
     */
    getReactionsToPostsByAuthor(authorName) {
        return this.reactions.filter(r => 
            r.post_author.toLowerCase().includes(authorName.toLowerCase())
        );
    }
}

// Auto-run extraction function
function extractLinkedInReactions() {
    console.log('❤️ LinkedIn Reactions Extractor (Browser DevTools)');
    console.log('='.repeat(60));
    
    const extractor = new LinkedInReactionsExtractor();
    
    // Extract reactions
    const reactions = extractor.extractReactions();
    
    // Print summary
    extractor.printSummary();
    
    // Provide options for export
    console.log('\n📤 EXPORT OPTIONS:');
    console.log('-'.repeat(60));
    console.log('To download CSV file:');
    console.log('  extractor.downloadCSV()');
    console.log('');
    console.log('To copy CSV to clipboard:');
    console.log('  extractor.copyToClipboard()');
    console.log('');
    console.log('To get raw data:');
    console.log('  extractor.getReactions()');
    console.log('');
    console.log('To filter by reaction type:');
    console.log('  extractor.getReactionsByType("love")');
    console.log('');
    console.log('To filter by user:');
    console.log('  extractor.getReactionsByUser("John Doe")');
    
    // Make extractor available globally
    window.linkedInReactionsExtractor = extractor;
    
    return extractor;
}

// Quick extraction function
function quickExtractReactions() {
    const extractor = extractLinkedInReactions();
    extractor.downloadCSV();
    return extractor;
}

// Usage instructions
console.log(`
❤️ LinkedIn Reactions Extractor - Browser DevTools Version
==========================================================

INSTRUCTIONS:
1. Navigate to a LinkedIn user's activity page
2. Click on "More" and select "Reactions" to view reactions
3. Scroll down to load more reactions if needed
4. Open Developer Tools (F12)
5. Paste this entire script into the Console
6. Run one of these commands:

COMMANDS:
• extractLinkedInReactions()  - Extract and show summary
• quickExtractReactions()     - Extract and auto-download CSV
• extractor.downloadCSV()     - Download CSV file
• extractor.copyToClipboard() - Copy CSV to clipboard

EXTRACTED DATA INCLUDES:
• Reaction ID and Feed Update ID
• Post author name, title, and content
• Post timestamp and URL
• Reactor name and profile URL
• Reaction type (love, like, celebrate, etc.)
• Full reaction text
• Extraction timestamp

FILTERING OPTIONS:
• Filter by reaction type
• Filter by reactor name
• Filter reactions to specific post authors

Ready to extract reactions! 🚀
`);

// Make functions available globally
window.extractLinkedInReactions = extractLinkedInReactions;
window.quickExtractReactions = quickExtractReactions; 