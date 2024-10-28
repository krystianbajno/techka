mod file_io;
mod text_processing;
mod models;

use pyo3::prelude::*;
use regex::Regex;
use std::{collections::HashSet, path::PathBuf};

#[pymodule]
fn website_processor(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<DataProcessor>()?;
    Ok(())
}

#[pyclass]
struct DataProcessor;

#[pymethods]
impl DataProcessor {
    #[new]
    fn new() -> Self {
        DataProcessor
    }

    fn get_emails(&self, input_dir: &str) -> PyResult<Vec<String>> {
        let files = text_processing::get_all_files(input_dir);
        Ok(text_processing::extract_emails_from_files(&files))
    }

    fn get_pdfs(&self, input_dir: &str) -> PyResult<Vec<String>> {
        let files = text_processing::get_all_files(input_dir);
        Ok(text_processing::extract_text_from_pdfs(&files))
    }

    fn find_keywords(&self, input_dir: &str, keywords: Vec<String>) -> PyResult<Vec<String>> {
        let files = text_processing::get_all_files(input_dir);
        let keywords_set: HashSet<String> = keywords.into_iter().collect();
        Ok(text_processing::find_keywords_in_files(&files, &keywords_set))
    }

    fn get_emails_from_file(&self, filepath: &str) -> PyResult<Vec<String>> {
        let file = PathBuf::from(filepath);
        let email_regex = Regex::new(r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}").unwrap();
        let result = text_processing::search_patterns_in_files(&[file], &email_regex);
        Ok(result)
    }

    fn get_pdf_text(&self, filepath: &str) -> PyResult<String> {
        let file = PathBuf::from(filepath);
        Ok(text_processing::extract_text_from_file(&file))
    }

    fn find_keywords_in_file(&self, filepath: &str, keywords: Vec<String>) -> PyResult<Vec<String>> {
        let file = PathBuf::from(filepath);
        let keywords_set: HashSet<String> = keywords.into_iter().collect();
        Ok(text_processing::find_keywords_in_files(&[file], &keywords_set))
    }
}
