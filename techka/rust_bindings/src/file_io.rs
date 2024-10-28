use anyhow::Result;

pub fn mmap_file(filepath: &str) -> Result<String> {
    use memmap2::Mmap;
    use std::fs::File;

    let file = File::open(filepath)?;
    let mmap = unsafe { Mmap::map(&file)? };
    let content = std::str::from_utf8(&mmap).unwrap_or("").to_string();
    Ok(content)
}
