// LinkedIn Reposts Extractor with CSV Export
function extractRepostsDataToCSV() {
  const repostsData = [];
  
  // Select individual repost items from the reposts modal
  const repostItems = document.querySelectorAll('.feed-shared-update-v2[role="article"]');
  
  repostItems.forEach((item, index) => {
    try {
      // Extract reposter name from the header
      const reposterHeaderElement = item.querySelector('.update-components-header__text-view a');
      const reposterName = reposterHeaderElement ? reposterHeaderElement.textContent.trim() : 'N/A';
      
      // Extract reposter profile URL from header
      const reposterHeaderLink = item.querySelector('.update-components-header__text-wrapper a[href*="linkedin.com/in/"]');
      const reposterProfileUrl = reposterHeaderLink ? reposterHeaderLink.href : 'N/A';
      
      // Extract reposter profile image from header
      const reposterHeaderImg = item.querySelector('.update-components-header__image img');
      const reposterProfileImageUrl = reposterHeaderImg ? reposterHeaderImg.src : 'N/A';
      
      // Extract original post author name
      const originalAuthorElement = item.querySelector('.update-components-actor__title .hoverable-link-text span[dir="ltr"] span[aria-hidden="true"]');
      const originalAuthorName = originalAuthorElement ? originalAuthorElement.textContent.trim() : 'N/A';
      
      // Extract original post author profile URL
      const originalAuthorLink = item.querySelector('.update-components-actor__meta-link[href*="linkedin.com/in/"]');
      const originalAuthorProfileUrl = originalAuthorLink ? originalAuthorLink.href : 'N/A';
      
      // Extract original post author job title/description
      const originalAuthorJobElement = item.querySelector('.update-components-actor__description span[aria-hidden="true"]');
      const originalAuthorJobTitle = originalAuthorJobElement ? originalAuthorJobElement.textContent.trim() : 'N/A';
      
      // Extract original post author profile image
      const originalAuthorImg = item.querySelector('.update-components-actor__avatar img');
      const originalAuthorProfileImageUrl = originalAuthorImg ? originalAuthorImg.src : 'N/A';
      
      // Extract post timestamp
      const timestampElement = item.querySelector('.update-components-actor__sub-description span[aria-hidden="true"]');
      const timestamp = timestampElement ? timestampElement.textContent.trim().split('•')[0].trim() : 'N/A';
      
      // Extract post content preview
      const contentElement = item.querySelector('.update-components-text .break-words span[dir="ltr"]');
      const postContent = contentElement ? contentElement.textContent.trim().substring(0, 200) + '...' : 'N/A';
      
      // Extract post URN (unique identifier)
      const postUrn = item.getAttribute('data-urn') || 'N/A';
      
      // Extract visibility info
      const visibilityElement = item.querySelector('.update-components-actor__sub-description .visually-hidden');
      const visibility = visibilityElement ? visibilityElement.textContent.trim().split('•').pop().trim() : 'N/A';
      
      repostsData.push({
        index: index + 1,
        reposterName: reposterName,
        reposterProfileUrl: reposterProfileUrl,
        reposterProfileImageUrl: reposterProfileImageUrl,
        originalAuthorName: originalAuthorName,
        originalAuthorProfileUrl: originalAuthorProfileUrl,
        originalAuthorJobTitle: originalAuthorJobTitle,
        originalAuthorProfileImageUrl: originalAuthorProfileImageUrl,
        timestamp: timestamp,
        visibility: visibility,
        postUrn: postUrn,
        postContentPreview: postContent
      });
    } catch (error) {
      console.error(`Error processing repost item ${index}:`, error);
    }
  });
  
  return repostsData;
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

function downloadCSV(data, filename = 'linkedin_reposts.csv') {
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

// ------------

const getPostReposts = () => downloadCSV(extractRepostsDataToCSV(), 'linkedin_reposts.csv');
// getPostReposts()
