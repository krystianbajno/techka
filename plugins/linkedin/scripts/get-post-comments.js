function extractCommentsDataToCSV() {
  const commentsData = [];
  const commentItems = document.querySelectorAll('.comments-comment-entity');
  
  commentItems.forEach((item, index) => {
    try {
      const nameElement = item.querySelector('.comments-comment-meta__description-title');
      const name = nameElement ? nameElement.textContent.trim() : 'N/A';
      
      const linkElement = item.querySelector('.comments-comment-meta__description-container[href*="linkedin.com/in/"]');
      const profileUrl = linkElement ? linkElement.href : 'N/A';
      
      const jobTitleElement = item.querySelector('.comments-comment-meta__description-subtitle');
      const jobTitle = jobTitleElement ? jobTitleElement.textContent.trim() : 'N/A';
      
      const commentTextElement = item.querySelector('.comments-comment-item__main-content .update-components-text');
      const commentText = commentTextElement ? commentTextElement.textContent.trim() : 'N/A';
      
      const timeElement = item.querySelector('.comments-comment-meta__data time, .comments-comment-meta__info time');
      const timePosted = timeElement ? timeElement.textContent.trim() : 'N/A';
      
      const degreeElement = item.querySelector('.comments-comment-meta__data');
      const connectionDegree = degreeElement ? degreeElement.textContent.trim().split('•').pop().trim() : 'N/A';
      
      const imgElement = item.querySelector('.comments-comment-meta__actor img[src*="media.licdn.com"], .comments-comment-meta__actor img[src*="dms"]');
      const profileImageUrl = imgElement ? imgElement.src : 'N/A';
      
      // const editedElement = item.querySelector('.comments-comment-meta__data:contains("(edited)")');
      // const isEdited = editedElement ? true : false;
      
      const isReply = item.classList.contains('comments-comment-entity--reply');
      
      const reactionCountElement = item.querySelector('.comments-comment-social-bar__reactions-count--cr');
      const reactionCount = reactionCountElement ? 
        reactionCountElement.textContent.trim().match(/\d+/) ? 
        reactionCountElement.textContent.trim().match(/\d+/)[0] : '0' : '0';
      
      const reactionIcons = item.querySelectorAll('.reactions-icon[data-test-reactions-icon-type]');
      const reactionTypes = Array.from(reactionIcons).map(icon => 
        icon.getAttribute('data-test-reactions-icon-type')
      ).join(', ');
      
      const hasPremium = item.querySelector('.text-view-model__linkedin-bug-premium-v2') ? true : false;
      
      const isVerified = item.querySelector('.text-view-model__verified-icon') ? true : false;
      
      // Check if author badge exists
      const isAuthor = item.querySelector('.comments-comment-meta__badge') ? true : false;
      
      commentsData.push({
        index: index + 1,
        name: name,
        profileUrl: profileUrl,
        jobTitle: jobTitle,
        commentText: commentText,
        timePosted: timePosted,
        connectionDegree: connectionDegree,
        profileImageUrl: profileImageUrl,
        // isEdited: isEdited,
        isReply: isReply,
        reactionCount: reactionCount,
        reactionTypes: reactionTypes,
        hasPremium: hasPremium,
        isVerified: isVerified,
        isAuthor: isAuthor
      });
    } catch (error) {
      console.error(`Error processing comment ${index}:`, error);
    }
  });
  
  return commentsData;
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

function downloadCSV(data, filename = 'linkedin_comments.csv') {
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


const getPostComments = () => downloadCSV( extractCommentsDataToCSV(), 'linkedin_comments.csv');
getPostComments()