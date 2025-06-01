/**
 * LinkedIn Comments Extractor (Browser DevTools)
 * Extracts user comments from LinkedIn HTML page and saves as CSV
 * Run this in browser developer tools console
 */

class LinkedInCommentsExtractor {
    constructor() {
        this.comments = [];
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
            post_content: "",
            post_url: ""
        };

        try {
            // Extract post author name
            const authorNameElement = feedUpdateElement.querySelector('.update-components-actor__title .hoverable-link-text');
            if (authorNameElement) {
                postInfo.post_author = this.cleanText(authorNameElement.textContent);
            }

            // Extract post author title/description
            const authorDescElement = feedUpdateElement.querySelector('.update-components-actor__description');
            if (authorDescElement) {
                postInfo.post_author_title = this.cleanText(authorDescElement.textContent);
            }

            // Extract post content
            const postContentElement = feedUpdateElement.querySelector('.feed-shared-text .update-components-text');
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

            // Try to extract post URL from permalink
            const permalinkElement = feedUpdateElement.querySelector('[data-urn]');
            if (permalinkElement) {
                const urn = permalinkElement.getAttribute('data-urn');
                if (urn) {
                    // Extract activity ID from URN like "urn:li:activity:7327743543861469184"
                    const activityMatch = urn.match(/activity:(\d+)/);
                    if (activityMatch) {
                        postInfo.post_url = `https://www.linkedin.com/feed/update/${urn}/`;
                    }
                }
            }

        } catch (error) {
            console.warn("Error extracting post info:", error);
        }

        return postInfo;
    }

    /**
     * Extract user name from comment entity
     */
    extractUserName(commentEntity) {
        const nameElement = commentEntity.querySelector('.comments-comment-meta__description-title');
        if (nameElement) {
            return this.cleanText(nameElement.textContent);
        }
        return "Unknown User";
    }

    /**
     * Extract user professional title/subtitle
     */
    extractUserTitle(commentEntity) {
        const subtitleElement = commentEntity.querySelector('.comments-comment-meta__description-subtitle');
        if (subtitleElement) {
            return this.cleanText(subtitleElement.textContent);
        }
        return "";
    }

    /**
     * Extract user profile URL
     */
    extractUserProfileUrl(commentEntity) {
        const profileLink = commentEntity.querySelector('.comments-comment-meta__image-link, .comments-comment-meta__description-container');
        if (profileLink && profileLink.href) {
            return profileLink.href;
        }
        return "";
    }

    /**
     * Extract comment timestamp
     */
    extractCommentTime(commentEntity) {
        const timeElement = commentEntity.querySelector('time.comments-comment-meta__data');
        if (timeElement) {
            return this.cleanText(timeElement.textContent);
        }
        return "";
    }

    /**
     * Extract the main comment text content
     */
    extractCommentText(commentEntity) {
        const contentElement = commentEntity.querySelector('.comments-comment-item__main-content');
        if (contentElement) {
            // Find the div with update-components-text class which contains the actual text
            const textDiv = contentElement.querySelector('.update-components-text');
            if (textDiv) {
                // Extract text and preserve line breaks
                let text = "";
                const walker = document.createTreeWalker(
                    textDiv,
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
                return this.cleanText(text);
            }
        }
        return "";
    }

    /**
     * Extract reaction count from comment
     */
    extractReactionCount(commentEntity) {
        const reactionButton = commentEntity.querySelector('.comments-comment-social-bar__reactions-count--cr');
        if (reactionButton) {
            const reactionText = reactionButton.textContent;
            // Extract number from text like "1 Reaction"
            const match = reactionText.match(/(\d+)/);
            if (match) {
                return match[1];
            }
        }
        return "0";
    }

    /**
     * Extract reply count from comment
     */
    extractReplyCount(commentEntity) {
        const replySpan = commentEntity.querySelector('.comments-comment-social-bar__replies-count--cr');
        if (replySpan) {
            const replyText = replySpan.textContent;
            // Extract number from text like "1 reply"
            const match = replyText.match(/(\d+)/);
            if (match) {
                return match[1];
            }
        }
        return "0";
    }

    /**
     * Check if comment is a reply (nested comment)
     */
    isReplyComment(commentEntity) {
        return commentEntity.classList.contains('comments-comment-entity--reply');
    }

    /**
     * Extract all comments from the current page
     */
    extractComments() {
        console.log("🔄 Extracting comments from current page...");
        const comments = [];
        
        // Find all feed update containers
        const feedUpdates = document.querySelectorAll('.feed-shared-update-v2');
        
        console.log(`📊 Found ${feedUpdates.length} feed updates`);
        
        feedUpdates.forEach((feedUpdate, feedIdx) => {
            try {
                // Extract post information for this feed update
                const postInfo = this.extractPostInfo(feedUpdate);
                
                // Find all comment entities within this feed update
                const commentEntities = feedUpdate.querySelectorAll('article.comments-comment-entity');
                
                commentEntities.forEach((commentEntity, commentIdx) => {
                    try {
                        const commentData = {
                            comment_id: comments.length + 1,
                            feed_update_id: feedIdx + 1,
                            post_author: postInfo.post_author,
                            post_author_title: postInfo.post_author_title,
                            post_content: postInfo.post_content.substring(0, 500) + (postInfo.post_content.length > 500 ? '...' : ''),
                            post_url: postInfo.post_url,
                            commenter_name: this.extractUserName(commentEntity),
                            commenter_title: this.extractUserTitle(commentEntity),
                            commenter_profile_url: this.extractUserProfileUrl(commentEntity),
                            comment_text: this.extractCommentText(commentEntity),
                            timestamp: this.extractCommentTime(commentEntity),
                            reaction_count: this.extractReactionCount(commentEntity),
                            reply_count: this.extractReplyCount(commentEntity),
                            is_reply: this.isReplyComment(commentEntity)
                        };
                        
                        // Only add if we have actual comment text
                        if (commentData.comment_text) {
                            comments.push(commentData);
                            console.log(`✓ Extracted comment ${comments.length}: ${commentData.commenter_name} on post by ${commentData.post_author}`);
                        }
                        
                    } catch (error) {
                        console.warn(`⚠️  Error extracting comment ${commentIdx + 1}:`, error);
                    }
                });
                
            } catch (error) {
                console.warn(`⚠️  Error processing feed update ${feedIdx + 1}:`, error);
            }
        });
        
        console.log(`✅ Successfully extracted ${comments.length} comments`);
        this.comments = comments;
        return comments;
    }

    /**
     * Convert data to CSV format
     */
    convertToCSV() {
        if (this.comments.length === 0) {
            console.warn("⚠️  No comments to convert. Run extractComments() first.");
            return "";
        }
        
        const headers = [
            'comment_id', 'feed_update_id', 'post_author', 'post_author_title', 'post_content',
            'post_url', 'commenter_name', 'commenter_title', 'commenter_profile_url',
            'comment_text', 'timestamp', 'reaction_count', 'reply_count', 'is_reply'
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
        
        this.comments.forEach(comment => {
            const row = headers.map(header => escapeCSV(comment[header])).join(',');
            csvContent += row + '\n';
        });
        
        return csvContent;
    }

    /**
     * Download CSV file
     */
    downloadCSV(filename = 'linkedin_comments.csv') {
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
     * Print a summary of extracted comments
     */
    printSummary() {
        if (this.comments.length === 0) {
            console.log("No comments extracted.");
            return;
        }
        
        const totalComments = this.comments.length;
        const replies = this.comments.filter(c => c.is_reply).length;
        const mainComments = totalComments - replies;
        const uniquePosters = new Set(this.comments.map(c => c.post_author)).size;
        const uniqueCommenters = new Set(this.comments.map(c => c.commenter_name)).size;
        
        console.log('\n📊 EXTRACTION SUMMARY');
        console.log('='.repeat(60));
        console.log(`Total comments extracted: ${totalComments}`);
        console.log(`Main comments: ${mainComments}`);
        console.log(`Replies: ${replies}`);
        console.log(`Unique post authors: ${uniquePosters}`);
        console.log(`Unique commenters: ${uniqueCommenters}`);
        console.log('='.repeat(60));
        
        console.log('\n📝 SAMPLE COMMENTS:');
        console.log('-'.repeat(60));
        
        this.comments.slice(0, 3).forEach((comment, i) => {
            const commentType = comment.is_reply ? "Reply" : "Main";
            console.log(`${i + 1}. [${commentType}] ${comment.commenter_name} → ${comment.post_author}`);
            console.log(`   Post: "${comment.post_content.substring(0, 80)}..."`);
            console.log(`   Comment: "${comment.comment_text.substring(0, 80)}..."`);
            console.log(`   ${comment.timestamp} | ❤️ ${comment.reaction_count} | 💬 ${comment.reply_count}\n`);
        });
    }

    /**
     * Get comments as array of objects
     */
    getComments() {
        return this.comments;
    }
}

// Auto-run extraction function
function extractLinkedInComments() {
    console.log('🔍 LinkedIn Comments Extractor (Browser DevTools)');
    console.log('='.repeat(60));
    
    const extractor = new LinkedInCommentsExtractor();
    
    // Extract comments
    const comments = extractor.extractComments();
    
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
    console.log('  extractor.getComments()');
    
    // Make extractor available globally
    window.linkedInExtractor = extractor;
    
    return extractor;
}

// Quick extraction function
function quickExtract() {
    const extractor = extractLinkedInComments();
    extractor.downloadCSV();
    return extractor;
}

// Usage instructions
console.log(`
🔍 LinkedIn Comments Extractor - Browser DevTools Version
==========================================================

INSTRUCTIONS:
1. Navigate to a LinkedIn user's activity page (Comments section)
2. Scroll down to load more comments if needed
3. Open Developer Tools (F12)
4. Paste this entire script into the Console
5. Run one of these commands:

COMMANDS:
• extractLinkedInComments()  - Extract and show summary
• quickExtract()             - Extract and auto-download CSV
• extractor.downloadCSV()    - Download CSV file
• extractor.copyToClipboard() - Copy CSV to clipboard

EXTRACTED DATA INCLUDES:
• Comment ID and Feed Update ID
• Post author name and title
• Post content (truncated)
• Post URL
• Commenter name, title, and profile URL
• Comment text and timestamp
• Reaction and reply counts
• Whether comment is a reply

Ready to extract! 🚀
`);

// Make functions available globally
window.extractLinkedInComments = extractLinkedInComments;
window.quickExtract = quickExtract; 