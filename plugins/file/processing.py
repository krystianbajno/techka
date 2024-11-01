import os
import shutil

    
def get_pdfs(filepath):
    from techka_rust_bindings import DataProcessor
    processor = DataProcessor()
    
    pdf_text = processor.get_pdf_text(filepath)
    return pdf_text
    
def get_emails(filepath):
    from techka_rust_bindings import DataProcessor
    processor = DataProcessor()
    
    emails = processor.get_emails_from_file(filepath)

    return emails

def get_keywords(filepath, keywords):
    from techka_rust_bindings import DataProcessor
    processor = DataProcessor()
    
    keywords_result = processor.find_keywords_in_file(filepath, keywords)
    return keywords_result
    
def clean_data(DATA_DIR):
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        print("Scraped data has been removed.")
    else:
        print("No data to clean.")