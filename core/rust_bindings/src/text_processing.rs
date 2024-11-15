use std::collections::HashSet;
use std::error::Error;
use std::path::PathBuf;
use lopdf::Object;
use regex::Regex;
use walkdir::WalkDir;
use crate::file_io::mmap_file;

pub fn get_all_files(base_dir: &str) -> Vec<PathBuf> {
    WalkDir::new(base_dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|entry| entry.file_type().is_file())
        .map(|entry| entry.path().to_path_buf())
        .collect()
}

pub fn extract_emails_from_files(files: &[PathBuf]) -> Vec<String> {
    let email_regex = Regex::new(r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}").unwrap();
    search_patterns_in_files(files, &email_regex)
}

pub fn find_keywords_in_files(files: &[PathBuf], keywords: &HashSet<String>) -> Vec<String> {
    let keyword_regex = Regex::new(&keywords.iter().map(|k| regex::escape(k)).collect::<Vec<_>>().join("|")).unwrap();
    search_patterns_in_files(files, &keyword_regex)
}

pub fn extract_text_from_pdfs(files: &[PathBuf]) -> Vec<String> {
    files.iter()
        .filter_map(|file| {
            file.extension()
                .and_then(|ext| ext.to_str())
                .filter(|ext| ext.eq_ignore_ascii_case("pdf"))
                .and_then(|_| extract_text_from_pdf(file).ok())
        })
        .collect()
}
pub fn search_detailed_patterns_in_files(
    files: &[PathBuf],
    pattern: &Regex,
    truncate: u32, 
) -> Vec<(String, usize, String)> {  
    let mut results = Vec::new();

    for file in files {
        let content = extract_text_from_file(file);
        if content.is_empty() {
            continue;
        }

        for (line_number, line) in content.lines().enumerate() {
            if let Some(match_found) = pattern.find(line) {
                let filename = file.file_name().unwrap_or_default().to_string_lossy();

                let start = match_found.start();
                let end = match_found.end();

                let left_context = if start >= truncate as usize {
                    &line[start - truncate as usize..start]
                } else {
                    &line[0..start]  
                };

                let right_context = if line.len() > end + truncate as usize {
                    &line[end..end + truncate as usize]
                } else {
                    &line[end..] 
                };

                let context = format!("{}{}{}", left_context, match_found.as_str(), right_context);

                results.push((
                    filename.to_string(),
                    line_number + 1,
                    context
                ));
            }
        }
    }

    results
}

pub fn search_patterns_in_files(files: &[PathBuf], pattern: &Regex) -> Vec<String> {
    let mut results = Vec::new();

    for file in files {
        let content = extract_text_from_file(file);
        if !content.is_empty() {
            for match_found in pattern.find_iter(&content) {
                results.push(match_found.as_str().to_string());
            }
        }
    }

    results
}

pub fn extract_text_from_file(filepath: &PathBuf) -> String {
    let mut text = String::new();
    let extension = filepath.extension().and_then(|ext| ext.to_str()).unwrap_or("");

    if extension.eq_ignore_ascii_case("pdf") {
        match extract_text_from_pdf(filepath) {
            Ok(pdf_text) => text = pdf_text,
            Err(e) => eprintln!("Error extracting text from PDF {:?}: {}", filepath, e),
        }
    } else {
        match mmap_file(filepath.to_str().unwrap()) {
            Ok(file_content) => text = file_content,
            Err(e) => eprintln!("Error reading file {:?}: {}", filepath, e),
        }
    }

    text
}

pub fn extract_text_from_pdf(path: &PathBuf) -> Result<String, Box<dyn Error>> {
    use lopdf::{content::Content, Document};

    let doc = Document::load(path)?;
    let mut full_text = String::new();

    for (_, page_id) in doc.get_pages() {
        let page = doc.get_dictionary(page_id)?;

        let contents = match page.get(b"Contents") {
            Ok(content) => content,
            Err(_) => continue,
        };

        let mut streams = Vec::new();
        match contents {
            Object::Reference(r) => {
                let stream = doc.get_object(*r)?;
                streams.push(stream);
            }
            Object::Array(arr) => {
                for obj in arr {
                    if let Object::Reference(r) = obj {
                        let stream = doc.get_object(*r)?;
                        streams.push(stream);
                    }
                }
            }
            _ => {}
        }

        for stream in streams {
            if let Object::Stream(stream_dict) = stream {
                let content_data = stream_dict.decompressed_content()?;
                let content = Content::decode(&content_data)?;

                for operation in content.operations {
                    match operation.operator.as_ref() {
                        "Tj" | "TJ" => {
                            if let Some(text) = extract_text_from_operands(&operation.operands) {
                                full_text.push_str(&text);
                            }
                        }
                        _ => {}
                    }
                }
            }
        }
    }

    Ok(full_text)
}

fn extract_text_from_operands(operands: &[Object]) -> Option<String> {
    let mut text = String::new();

    for operand in operands {
        match operand {
            Object::String(ref bytes, _) => {
                let decoded = String::from_utf8_lossy(bytes);
                text.push_str(&decoded);
            }
            Object::Array(ref arr) => {
                for obj in arr {
                    if let Object::String(ref bytes, _) = obj {
                        let decoded = String::from_utf8_lossy(bytes);
                        text.push_str(&decoded);
                    }
                }
            }
            _ => {}
        }
    }

    if text.is_empty() {
        None
    } else {
        Some(text)
    }
}
