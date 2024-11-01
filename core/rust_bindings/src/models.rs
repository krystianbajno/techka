use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MetadataEntry {
    pub filepath: String,
    pub title: String,
    pub url: String,
    pub collection_date: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ProcessedItem {
    pub title: String,
    pub link: String,
    pub filepath: String,
    pub collection_date: String,
}
