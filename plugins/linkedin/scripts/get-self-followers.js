// LinkedIn Followers Extractor with CSV Export - Using Stable Selectors
function extractFollowersDataToCSV() {
  const followersData = [];
  
  // Use more stable selectors - look for items with data-chameleon-result-urn attribute
  const listItems = document.querySelectorAll('[data-chameleon-result-urn*="urn:li:member:"]');
  
  listItems.forEach((item, index) => {
    try {
      // Extract name from profile link or image alt text
      let name = 'N/A';
      const profileLink = item.querySelector('a[href*="linkedin.com/in/"]');
      if (profileLink) {
        // Try to get name from the link text first
        const linkText = profileLink.textContent.trim();
        if (linkText && linkText !== '') {
          name = linkText;
        } else {
          // Fallback to image alt text
          const profileImg = item.querySelector('img[alt]');
          if (profileImg && profileImg.alt) {
            name = profileImg.alt.replace(/^(.*?)\s+(is\s+open\s+to\s+work|profile\s+photo)$/i, '$1').trim();
          }
        }
      }
      
      // Extract profile URL
      const profileUrl = profileLink ? profileLink.href : 'N/A';
      
      // Extract job title/description - look for text content in the card structure
      let jobTitle = 'N/A';
      const textElements = item.querySelectorAll('div');
      for (const element of textElements) {
        const text = element.textContent.trim();
        // Look for job-title-like content (avoid names and button text)
        if (text && 
            text.length > 10 && 
            !text.includes('Following') && 
            !text.includes('followed') &&
            !text.toLowerCase().includes('status is') &&
            !text.includes(name) &&
            (text.includes('@') || text.includes('|') || text.includes('at ') || text.includes('CEO') || text.includes('Manager') || text.includes('Engineer') || text.includes('Director'))) {
          jobTitle = text;
          break;
        }
      }
      
      // Extract profile image URL
      const imgElement = item.querySelector('img[src*="media.licdn.com"]');
      const profileImageUrl = imgElement ? imgElement.src : 'N/A';
      
      // Extract connection insights (mutual connections info)
      let connectionInsights = 'N/A';
      const textContent = item.textContent;
      const followedMatch = textContent.match(/(.*?\s+followed|.*?\s+you\s+know\s+followed)/i);
      if (followedMatch) {
        connectionInsights = followedMatch[0].trim();
      }
      
      // Check if user has "Following" button (indicates they are being followed back)
      const followingButton = item.querySelector('button[aria-label*="stop following"], button[aria-label*="Following"]');
      const isFollowingBack = followingButton ? 'Yes' : 'No';
      
      // Extract the follower's member URN for unique identification
      const memberUrn = item.getAttribute('data-chameleon-result-urn') || 'N/A';
      
      // Only add if we found a valid name
      if (name !== 'N/A' && name.length > 0) {
        followersData.push({
          index: index + 1,
          name: name,
          profileUrl: profileUrl,
          jobTitle: jobTitle,
          profileImageUrl: profileImageUrl,
          connectionInsights: connectionInsights,
          isFollowingBack: isFollowingBack,
          memberUrn: memberUrn,
          extractedDate: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error(`Error processing follower item ${index}:`, error);
    }
  });
  
  return followersData;
}

function convertToCSV(data) {
  if (data.length === 0) return '';
  
  // Get headers
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    headers.join(','), // Header row
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Escape quotes and wrap in quotes if contains comma or quote
        const stringValue = String(value).replace(/"/g, '""');
        return stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n') 
          ? `"${stringValue}"` 
          : stringValue;
      }).join(',')
    )
  ].join('\n');
  
  return csvContent;
}

function downloadCSV(data, filename = 'linkedin_followers.csv') {
  const csvContent = convertToCSV(data);
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
  }
}

// Function to find "Show more" button using various methods
function findShowMoreButton() {
  // Try multiple approaches to find the button
  let button = null;
  
  // Method 1: Look for buttons with specific class patterns
  button = document.querySelector('button[class*="load-button"]') ||
           document.querySelector('button[class*="show-more"]') ||
           document.querySelector('.scaffold-finite-scroll__load-button');
  
  if (button) return button;
  
  // Method 2: Look for buttons with specific text content
  const buttons = document.querySelectorAll('button');
  for (const btn of buttons) {
    const text = btn.textContent.toLowerCase().trim();
    if (text.includes('show more') || text.includes('load more') || text.includes('more results')) {
      return btn;
    }
  }
  
  // Method 3: Look for buttons with specific ARIA labels
  button = document.querySelector('button[aria-label*="more"]') ||
           document.querySelector('button[aria-label*="load"]');
  
  return button;
}

// Helper function to scroll and load more followers
function scrollToLoadMoreFollowers(maxScrolls = 10, scrollDelay = 2000) {
  let scrollCount = 0;
  
  const scrollInterval = setInterval(() => {
    // Scroll to bottom
    window.scrollTo(0, document.body.scrollHeight);
    
    // Check if "Show more results" button exists and click it
    const showMoreButton = findShowMoreButton();
    
    if (showMoreButton && !showMoreButton.disabled && showMoreButton.style.display !== 'none') {
      showMoreButton.click();
      console.log('Clicked "Show more results" button');
    }
    
    scrollCount++;
    console.log(`Scroll ${scrollCount}/${maxScrolls} completed`);
    
    if (scrollCount >= maxScrolls) {
      clearInterval(scrollInterval);
      console.log('Finished scrolling, ready to extract data');
      
      // Wait a bit more for final content to load, then extract
      setTimeout(() => {
        const followersData = extractFollowersDataToCSV();
        console.log('Extracted followers data:', followersData);
        console.log(`Total followers found: ${followersData.length}`);
        
        // Download CSV file
        downloadCSV(followersData, 'linkedin_followers.csv');
        console.log('CSV file downloaded successfully!');
      }, 3000);
    }
  }, scrollDelay);
}

// Main execution function
function extractAllFollowers() {
  console.log('Starting LinkedIn followers extraction...');
  console.log('This will scroll through the page to load more followers, then download the CSV.');
  console.log('Please wait while the script completes...');
  
  // First, try to extract currently visible followers
  const initialData = extractFollowersDataToCSV();
  console.log(`Initially found ${initialData.length} followers`);
  
  // Check if there are more followers to load
  const showMoreButton = findShowMoreButton();
  
  if (showMoreButton && !showMoreButton.disabled) {
    console.log('Found "Show more results" button, will scroll to load all followers...');
    scrollToLoadMoreFollowers();
  } else {
    // No more followers to load, download what we have
    console.log('No more followers to load, downloading current data...');
    downloadCSV(initialData, 'linkedin_followers.csv');
    console.log('CSV file downloaded successfully!');
  }
}

// Alternative function to extract only currently visible followers (without scrolling)
function extractVisibleFollowers() {
  console.log('Extracting only currently visible followers...');
  const followersData = extractFollowersDataToCSV();
  console.log('Extracted followers data:', followersData);
  console.log(`Total followers found: ${followersData.length}`);
  
  downloadCSV(followersData, 'linkedin_followers_visible.csv');
  console.log('CSV file downloaded successfully!');
}

// Run the extraction (you can choose which function to use)
console.log('LinkedIn Followers Extractor loaded!');
console.log('Run extractAllFollowers() to get all followers (with scrolling)');
console.log('Run extractVisibleFollowers() to get only visible followers');
extractAllFollowers(); 