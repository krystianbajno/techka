use std::{collections::HashSet, path::PathBuf};
use regex::Regex;

use pyo3::prelude::*;

use crate::text_processing;

#[pyclass]
pub struct DataProcessor;

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

    fn find_keywords(&self, input_dir: &str, keywords: Vec<String>) -> PyResult<Vec<(String, usize, String)>> {
        let files = text_processing::get_all_files(input_dir);
        let keywords_set: HashSet<String> = keywords.into_iter().collect();
        let keyword_regex = Regex::new(&keywords_set.iter().map(|k| regex::escape(k)).collect::<Vec<_>>().join("|")).unwrap();
        Ok(text_processing::search_detailed_patterns_in_files(&files, &keyword_regex, 64))
    }

    fn get_emails_from_file(&self, filepath: &str) -> PyResult<Vec<String>> {
        let file = PathBuf::from(filepath);
        let result = text_processing::extract_emails_from_files(&[file]);
        Ok(result)
    }

    fn get_pdf_text(&self, filepath: &str) -> PyResult<String> {
        let file = PathBuf::from(filepath);
        Ok(text_processing::extract_text_from_file(&file))
    }

    fn find_keywords_in_file(&self, filepath: &str, keywords: Vec<String>) -> PyResult<Vec<(String, usize, String)>> {
        let file = PathBuf::from(filepath);
        let keywords_set: HashSet<String> = keywords.into_iter().collect();
        let keyword_regex = Regex::new(&keywords_set.iter().map(|k| regex::escape(k)).collect::<Vec<_>>().join("|")).unwrap();
        Ok(text_processing::search_detailed_patterns_in_files(&[file], &keyword_regex, 64))
    }
}
