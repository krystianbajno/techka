function extractLikesDataToCSV() {
  const likesData = [];
  const listItems = document.querySelectorAll('.social-details-reactors-tab-body-list-item');
  
  listItems.forEach((item, index) => {
    try {
      const nameElement = item.querySelector('.text-view-model');
      const name = nameElement ? nameElement.textContent.trim() : 'N/A';
      
      const linkElement = item.querySelector('a[href*="linkedin.com/in/"]');
      const profileUrl = linkElement ? linkElement.href : 'N/A';
      
      const captionElement = item.querySelector('.artdeco-entity-lockup__caption');
      const jobTitle = captionElement ? captionElement.textContent.trim() : 'N/A';
      
      const reactionIcon = item.querySelector('.reactions-icon');
      const reactionType = reactionIcon ? reactionIcon.getAttribute('data-test-reactions-icon-type') : 'UNKNOWN';
      
      const degreeElement = item.querySelector('.artdeco-entity-lockup__degree');
      const connectionDegree = degreeElement ? degreeElement.textContent.trim() : 'N/A';
      
      const imgElement = item.querySelector('img[src*="media.licdn.com"]');
      const profileImageUrl = imgElement ? imgElement.src : 'N/A';
      
      likesData.push({
        index: index + 1,
        name: name,
        profileUrl: profileUrl,
        jobTitle: jobTitle,
        reactionType: reactionType,
        connectionDegree: connectionDegree,
        profileImageUrl: profileImageUrl
      });
    } catch (error) {
      console.error(`Error processing item ${index}:`, error);
    }
  });
  
  return likesData;
}

function convertToCSV(data) {
  if (data.length === 0) return '';
  
  const headers = Object.keys(data[0]);
  
  const csvContent = [
    headers.join(','), 
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        const stringValue = String(value).replace(/"/g, '""');
        return stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n') 
          ? `"${stringValue}"` 
          : stringValue;
      }).join(',')
    )
  ].join('\n');
  
  return csvContent;
}

function downloadCSV(data, filename = 'linkedin_reactions.csv') {
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

const getPostLikes = () => downloadCSV( extractLikesDataToCSV(), 'linkedin_reactions.csv');
getPostLikes()