mod file_io;
mod text_processing;
mod models;
mod data_processor;
use data_processor::DataProcessor;
use pyo3::prelude::*;

#[pymodule]
fn techka_rust_bindings(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<DataProcessor>()?;
    Ok(())
}