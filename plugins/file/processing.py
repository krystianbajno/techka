import os
import shutil
import re
import pdfplumber
from pathlib import Path

# Document processing libraries
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import textract
    TEXTRACT_AVAILABLE = True
except ImportError:
    TEXTRACT_AVAILABLE = False

def get_pdfs(filepath):
    """Extract text from PDF and document files"""
    try:
        # Handle PDF files
        if filepath.lower().endswith('.pdf'):
            text_content = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            return text_content if text_content else ["No text found in PDF"]
        
        # Handle DOCX files
        elif filepath.lower().endswith('.docx'):
            if DOCX_AVAILABLE:
                try:
                    doc = Document(filepath)
                    text_content = []
                    for paragraph in doc.paragraphs:
                        if paragraph.text.strip():
                            text_content.append(paragraph.text)
                    return text_content if text_content else ["No text found in DOCX"]
                except Exception as e:
                    if TEXTRACT_AVAILABLE:
                        try:
                            text = textract.process(filepath).decode('utf-8')
                            return [text] if text.strip() else ["No text found in DOCX"]
                        except Exception as e2:
                            return [f"Error reading DOCX with both methods: {str(e)}, {str(e2)}"]
                    else:
                        return [f"Error reading DOCX: {str(e)}"]
            elif TEXTRACT_AVAILABLE:
                try:
                    text = textract.process(filepath).decode('utf-8')
                    return [text] if text.strip() else ["No text found in DOCX"]
                except Exception as e:
                    return [f"Error reading DOCX: {str(e)}"]
            else:
                return ["DOCX processing libraries not available"]
        
        # Handle DOC files
        elif filepath.lower().endswith('.doc'):
            if TEXTRACT_AVAILABLE:
                try:
                    text = textract.process(filepath).decode('utf-8')
                    return [text] if text.strip() else ["No text found in DOC"]
                except Exception as e:
                    return [f"Error reading DOC: {str(e)}"]
            else:
                return ["DOC processing libraries not available"]
        
        else:
            return [f"Unsupported file type: {filepath}"]
            
    except Exception as e:
        return [f"Error reading file: {str(e)}"]
    
def get_emails(filepath):
    """Extract emails from files using regex patterns"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = set()
    
    try:
        # Handle PDF files
        if filepath.lower().endswith('.pdf'):
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        found_emails = re.findall(email_pattern, text)
                        emails.update(found_emails)
        
        # Handle DOCX files
        elif filepath.lower().endswith('.docx'):
            if DOCX_AVAILABLE:
                try:
                    doc = Document(filepath)
                    for paragraph in doc.paragraphs:
                        if paragraph.text:
                            found_emails = re.findall(email_pattern, paragraph.text)
                            emails.update(found_emails)
                except Exception as e:
                    if TEXTRACT_AVAILABLE:
                        try:
                            text = textract.process(filepath).decode('utf-8')
                            found_emails = re.findall(email_pattern, text)
                            emails.update(found_emails)
                        except Exception:
                            print(f"Error extracting emails from DOCX: {str(e)}")
                    else:
                        print(f"Error extracting emails from DOCX: {str(e)}")
            elif TEXTRACT_AVAILABLE:
                try:
                    text = textract.process(filepath).decode('utf-8')
                    found_emails = re.findall(email_pattern, text)
                    emails.update(found_emails)
                except Exception as e:
                    print(f"Error extracting emails from DOCX: {str(e)}")
        
        # Handle DOC files
        elif filepath.lower().endswith('.doc'):
            if TEXTRACT_AVAILABLE:
                try:
                    text = textract.process(filepath).decode('utf-8')
                    found_emails = re.findall(email_pattern, text)
                    emails.update(found_emails)
                except Exception as e:
                    print(f"Error extracting emails from DOC: {str(e)}")
        
        # Handle text files
        elif filepath.lower().endswith(('.txt', '.rtf')):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                found_emails = re.findall(email_pattern, content)
                emails.update(found_emails)
        
        else:
            # Try textract for other file types
            if TEXTRACT_AVAILABLE:
                try:
                    text = textract.process(filepath).decode('utf-8')
                    found_emails = re.findall(email_pattern, text)
                    emails.update(found_emails)
                except Exception as e:
                    print(f"Error extracting emails from {filepath}: {str(e)}")
            
    except Exception as e:
        print(f"Error extracting emails: {str(e)}")
        
    return emails

def get_keywords(filepath, keywords):
        results = []
        try:
            # Handle PDF files
            if filepath.lower().endswith('.pdf'):
                with pdfplumber.open(filepath) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            for line_in_page, line in enumerate(text.split('\n'), 1):
                                for keyword in keywords:
                                    if keyword.lower() in line.lower():
                                        results.append((f"Page {page_num}, Line {line_in_page}", page_num * 1000 + line_in_page, line.strip()))
            
            # Handle DOCX files
            elif filepath.lower().endswith('.docx'):
                if DOCX_AVAILABLE:
                    try:
                        doc = Document(filepath)
                        for para_num, paragraph in enumerate(doc.paragraphs, 1):
                            if paragraph.text:
                                for keyword in keywords:
                                    if keyword.lower() in paragraph.text.lower():
                                        results.append((f"Paragraph {para_num}", para_num, paragraph.text.strip()))
                    except Exception as e:
                        if TEXTRACT_AVAILABLE:
                            try:
                                text = textract.process(filepath).decode('utf-8')
                                for line_num, line in enumerate(text.split('\n'), 1):
                                    for keyword in keywords:
                                        if keyword.lower() in line.lower():
                                            results.append((f"Line {line_num}", line_num, line.strip()))
                            except Exception:
                                print(f"Error searching keywords in DOCX: {str(e)}")
                elif TEXTRACT_AVAILABLE:
                    try:
                        text = textract.process(filepath).decode('utf-8')
                        for line_num, line in enumerate(text.split('\n'), 1):
                            for keyword in keywords:
                                if keyword.lower() in line.lower():
                                    results.append((f"Line {line_num}", line_num, line.strip()))
                    except Exception as e:
                        print(f"Error searching keywords in DOCX: {str(e)}")
            
            # Handle DOC files
            elif filepath.lower().endswith('.doc'):
                if TEXTRACT_AVAILABLE:
                    try:
                        text = textract.process(filepath).decode('utf-8')
                        for line_num, line in enumerate(text.split('\n'), 1):
                            for keyword in keywords:
                                if keyword.lower() in line.lower():
                                    results.append((f"Line {line_num}", line_num, line.strip()))
                    except Exception as e:
                        print(f"Error searching keywords in DOC: {str(e)}")
            
            # Handle text files
            elif filepath.lower().endswith(('.txt', '.rtf')):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    for line_num, line in enumerate(file, 1):
                        for keyword in keywords:
                            if keyword.lower() in line.lower():
                                results.append((f"Line {line_num}", line_num, line.strip()))
            
            else:
                # Try textract for other file types
                if TEXTRACT_AVAILABLE:
                    try:
                        text = textract.process(filepath).decode('utf-8')
                        for line_num, line in enumerate(text.split('\n'), 1):
                            for keyword in keywords:
                                if keyword.lower() in line.lower():
                                    results.append((f"Line {line_num}", line_num, line.strip()))
                    except Exception as e:
                        print(f"Error searching keywords in {filepath}: {str(e)}")
                        
        except Exception as e:
            print(f"Error searching for keywords: {str(e)}")
            
        return results
    
def clean_data(DATA_DIR):
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        print("Scraped data has been removed.")
    else:
        print("No data to clean.")
