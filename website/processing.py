def get_subdomains():
    with open("data/output/all_urls.txt") as f:
        subdomains = []
        data = f.readlines()
        
        for entry in data:
            split = entry.split("/")
            if split.__len__() > 2:
                subdomain = entry.split("/")[2].strip()
                if subdomain not in subdomains: 
                    subdomains.append(subdomain)
            
        return subdomains
    
def get_emails():
    with open("data/output/all_urls.txt") as f:
        emails = []
        data = f.readlines()
        
        for entry in data:
            if "mailto" in entry:
                emails.append(entry.split("mailto:")[1])
            
        return emails