function extractPostsActivityToCSV() {
  const postsData = [];
  
  const postContainers = document.querySelectorAll('div[data-urn*="urn:li:activity:"]');
  
  postContainers.forEach((container, index) => {
    try {
      const postUrn = container.getAttribute('data-urn') || 'N/A';
      const postId = postUrn.includes(':') ? postUrn.split(':').pop() : 'N/A';
      
      const authorNameElement = container.querySelector('.update-components-actor__title .hoverable-link-text span[dir="ltr"] span[aria-hidden="true"]');
      const authorName = authorNameElement ? authorNameElement.textContent.trim() : 'N/A';
      
      const authorProfileLink = container.querySelector('.update-components-actor__meta-link');
      const authorProfileUrl = authorProfileLink ? authorProfileLink.href : 'N/A';
      
      const authorTitleElement = container.querySelector('.update-components-actor__description span[aria-hidden="true"]');
      const authorTitle = authorTitleElement ? authorTitleElement.textContent.trim() : 'N/A';
      
      const timestampElement = container.querySelector('.update-components-actor__sub-description span[aria-hidden="true"]');
      const timestampText = timestampElement ? timestampElement.textContent.trim() : 'N/A';
      const timestamp = timestampText.split('•')[0]?.trim() || 'N/A';
      
      const postTextElement = container.querySelector('.update-components-text .break-words span[dir="ltr"]');
      const postText = postTextElement ? postTextElement.textContent.trim() : 'N/A';
      
      const hashtagElements = container.querySelectorAll('a[href*="hashtag"]');
      const hashtags = Array.from(hashtagElements).map(el => el.textContent.trim()).join(', ') || 'N/A';
      
      const reactionsElement = container.querySelector('.social-details-social-counts__reactions-count');
      const reactionsCount = reactionsElement ? reactionsElement.textContent.trim() : '0';
      
      const commentsElement = container.querySelector('button[aria-label*="comments"]');
      const commentsCount = commentsElement ? commentsElement.textContent.match(/\d+/)?.[0] || '0' : '0';
      
      const repostsElement = container.querySelector('button[aria-label*="reposts"]');
      const repostsCount = repostsElement ? repostsElement.textContent.match(/\d+/)?.[0] || '0' : '0';
      
      const repostIndicator = container.querySelector('.update-components-header__text-view');
      const isRepost = repostIndicator && repostIndicator.textContent.includes('reposted') ? 'Yes' : 'No';
      
      const imageElements = container.querySelectorAll('.update-components-image img');
      const hasMedia = imageElements.length > 0 ? 'Yes' : 'No';
      
      postsData.push({
        index: index + 1,
        postId: postId,
        authorName: authorName,
        authorTitle: authorTitle,
        authorProfileUrl: authorProfileUrl,
        timestamp: timestamp,
        postText: postText,
        hashtags: hashtags,
        reactionsCount: reactionsCount,
        commentsCount: commentsCount,
        repostsCount: repostsCount,
        isRepost: isRepost,
        hasMedia: hasMedia,
        extractedAt: new Date().toISOString()
      });
      
    } catch (error) {
      console.error(`Error processing post ${index + 1}:`, error);
    }
  });
  
  return postsData;
}

function convertToCSV(data) {
  if (data.length === 0) return '';
  
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row => 
      headers.map(header => {
        const value = row[header] || '';
        const stringValue = String(value).replace(/"/g, '""');
        return stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n') 
          ? `"${stringValue}"` 
          : stringValue;
      }).join(',')
    )
  ].join('\n');
  
  return csvContent;
}

function downloadCSV(data, filename = 'linkedin_posts.csv') {
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

function extractAndDownload() {
  
  const postsData = extractPostsActivityToCSV();
  
  if (postsData.length === 0) {
    console.log('No posts found. Make sure you are on the LinkedIn activity page.');
    return;
  }
    
  downloadCSV(postsData, `linkedin_posts.csv`);
  console.log('CSV downloaded!');
  
  return postsData;
}

extractAndDownload(); 