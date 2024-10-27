use anyhow::Result;
use crate::models::MetadataEntry;
use std::fs;
use std::path::Path;

pub fn load_metadata(filepath: &str) -> Result<Vec<MetadataEntry>> {
    let metadata: Vec<MetadataEntry> = serde_json::from_str(&fs::read_to_string(filepath)?)?;
    Ok(metadata)
}

pub fn write_output(data: &Vec<MetadataEntry>, output_path: &str) -> Result<()> {
    let output_json = serde_json::to_string_pretty(data)?;
    fs::create_dir_all(Path::new(output_path).parent().unwrap())?;
    fs::write(output_path, output_json)?;
    Ok(())
}

pub fn mmap_file(filepath: &str) -> Result<String> {
    use memmap2::Mmap;
    use std::fs::File;

    let file = File::open(filepath)?;
    let mmap = unsafe { Mmap::map(&file)? };
    let content = std::str::from_utf8(&mmap).unwrap_or("").to_string();
    Ok(content)
}
