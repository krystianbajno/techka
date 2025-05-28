function replacePolishChars(text) {
  const polishToAscii = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
    'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
    'Ó': 'O', 'Ś': 'S', 'Ż': 'Z', 'Ź': 'Z'
  };

  return text.split('').map(char => polishToAscii[char] || char).join('');
}

function downloadCSV(csvContent, filename) {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function getCompanyEmployeesCSV() {
  const profileCards = document.querySelectorAll('.org-people-profile-card__profile-card-spacing');
  
  const csvData = [];
  const headers = [
    'name', 
    'job_title', 
    'profile_url', 
    'connection_degree', 
    'mutual_connections',
    'profile_image_url',
    'f.lastname', 
    'flastname', 
    'firstname.lastname', 
    'firstnamelastname', 
    'lastname'
  ];
  csvData.push(headers.join(','));

  for (const card of profileCards) {
    // Extract name
    const nameElement = card.querySelector('.artdeco-entity-lockup__title');
    if (!nameElement) continue;
    
    const originalName = nameElement.innerText.trim();
    
    // Extract job title
    const jobTitleElement = card.querySelector('.artdeco-entity-lockup__subtitle .lt-line-clamp');
    const jobTitle = jobTitleElement ? jobTitleElement.innerText.trim() : '';
    
    // Extract profile URL
    const profileLinkElement = card.querySelector('.artdeco-entity-lockup__title a');
    const profileUrl = profileLinkElement ? profileLinkElement.href : '';
    
    // Extract connection degree
    const connectionElement = card.querySelector('.artdeco-entity-lockup__degree') || 
                             card.querySelector('.a11y-text');
    let connectionDegree = '';
    if (connectionElement) {
      connectionDegree = connectionElement.innerText.trim().replace(/[·\s]/g, '');
    }
    
    // Extract mutual connections
    const mutualConnectionsElement = card.querySelector('.t-12.t-black--light.mt2');
    const mutualConnections = mutualConnectionsElement ? 
                             mutualConnectionsElement.innerText.trim() : '';
    
    // Extract profile image URL
    const profileImageElement = card.querySelector('.artdeco-entity-lockup__image img');
    const profileImageUrl = profileImageElement ? profileImageElement.src : '';
    
    // Generate username variants
    const name = replacePolishChars(originalName).toLowerCase();
    const firstnameLastname = name.split(" ");
    
    let fLastname = '', fLastnameNoSpace = '', firstnameDotLastname = '';
    let firstnameLastnameNoSpace = '', lastname = '';
    
    if (firstnameLastname.length >= 2) {
      fLastname = `${firstnameLastname[0][0]}.${firstnameLastname[1]}`;
      fLastnameNoSpace = `${firstnameLastname[0][0]}${firstnameLastname[1]}`;
      firstnameDotLastname = `${firstnameLastname[0]}.${firstnameLastname[1]}`;
      firstnameLastnameNoSpace = `${firstnameLastname[0]}${firstnameLastname[1]}`;
      lastname = `${firstnameLastname[1]}`;
    }
    
    // Create CSV row - escape quotes and wrap in quotes
    const row = [
      `"${originalName.replace(/"/g, '""')}"`,
      `"${jobTitle.replace(/"/g, '""')}"`,
      `"${profileUrl.replace(/"/g, '""')}"`,
      `"${connectionDegree.replace(/"/g, '""')}"`,
      `"${mutualConnections.replace(/"/g, '""')}"`,
      `"${profileImageUrl.replace(/"/g, '""')}"`,
      `"${fLastname}"`,
      `"${fLastnameNoSpace}"`,
      `"${firstnameDotLastname}"`,
      `"${firstnameLastnameNoSpace}"`,
      `"${lastname}"`
    ];
    
    csvData.push(row.join(','));
  }

  const csvContent = csvData.join('\n');
  downloadCSV(csvContent, 'company-employees-complete.csv');
  
  console.log(`Processed ${csvData.length - 1} employees and downloaded complete CSV file`);
}

const getCompanyEmployeesCombined = () => getCompanyEmployeesCSV(); 

