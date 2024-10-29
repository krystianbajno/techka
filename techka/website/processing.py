import os
import shutil

def get_subdomains(ALL_URLS):
    with open(ALL_URLS) as f:
        subdomains = []
        data = f.readlines()
        
        for entry in data:
            split = entry.split("/")
            if split.__len__() > 2:
                subdomain = entry.split("/")[2].strip()
                if subdomain not in subdomains: 
                    subdomains.append(subdomain)
            
        return subdomains
    
def get_pdfs(DATA_DIR):
    from website_processor import DataProcessor
    processor = DataProcessor()
    
    pdf_texts = processor.get_pdfs(DATA_DIR)
    return pdf_texts
    
def get_emails(DATA_DIR):
    from website_processor import DataProcessor
    processor = DataProcessor()
    
    with open("data/output/all_urls.txt") as f:
        emails = []
        data = f.readlines()
        
        for entry in data:
            if "mailto" in entry:
                emails.append(entry.split("mailto:")[1])
                
    emails.extend(processor.get_emails(DATA_DIR))
            
    return emails

def get_keywords(DATA_DIR, keywords):
    from website_processor import DataProcessor
    processor = DataProcessor()
    
    keywords_result = processor.find_keywords(DATA_DIR, keywords)
    return keywords_result
    
    
def clean_data(DATA_DIR):
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        print("Scraped data has been removed.")
    else:
        print("No data to clean.")