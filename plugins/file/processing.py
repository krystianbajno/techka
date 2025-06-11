import os
import shutil
import re
import pdfplumber
import magic
from pathlib import Path
from zipfile import ZipFile
from docx import Document

def detect_file_type(filepath):
    """Detect file type using python-magic (MIME type detection)."""
    try:
        mime = magic.from_file(filepath, mime=True)
        if mime == 'application/pdf':
            return 'pdf'
        elif mime in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return 'docx'
        elif mime == 'text/rtf':
            return 'rtf'
        elif mime.startswith('text/'):
            return 'txt'
        else:
            return 'unknown'
    except Exception as e:
        print(f"Error detecting file type: {str(e)}")
        return 'unknown'

def extract_text_from_pdf(filepath):
    text_content = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
    return text_content if text_content else ["No text found in PDF"]

def extract_text_from_docx(filepath):
    text_content = []
    try:
        doc = Document(filepath)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        return text_content if text_content else ["No text found in DOCX"]
    except Exception as e:
        return [f"Error reading DOCX: {str(e)}"]

def extract_text_from_txt(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().splitlines()
    except Exception as e:
        return [f"Error reading text file: {str(e)}"]

def get_pdfs(filepath):
    """Extract text content based on detected file type."""
    filetype = detect_file_type(filepath)
    if filetype == 'pdf':
        return extract_text_from_pdf(filepath)
    elif filetype == 'docx':
        return extract_text_from_docx(filepath)
    elif filetype in ['txt', 'rtf']:
        return extract_text_from_txt(filepath)
    else:
        return [f"Unsupported or unknown file type: {filetype}"]

def get_emails(filepath):
    """Extract emails from file content using regex."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = set()

    text_lines = get_pdfs(filepath)
    for line in text_lines:
        found_emails = re.findall(email_pattern, line)
        emails.update(found_emails)

    return emails

def get_keywords(filepath, keywords):
    """Find keywords and return (location, index, line) tuples."""
    if not keywords:
        keywords = []

    results = []
    text_lines = get_pdfs(filepath)

    for idx, line in enumerate(text_lines, 1):
        for keyword in keywords:
            if keyword.lower() in line.lower():
                results.append((f"Line {idx}", idx, line.strip()))

    return results
