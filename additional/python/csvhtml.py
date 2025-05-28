#!/usr/bin/env python3
"""
CSV to HTML Table Converter
Converts CSV files into beautiful, searchable, and filterable HTML tables.

Usage:
    python csv_to_html_table.py input.csv [output.html]
    
If no output file is specified, it will create one based on the input filename.
"""

import pandas as pd
import argparse
import sys
import os
from pathlib import Path
import csv
import io

def create_html_template(df, table_id="data-table", title="Data Table"):
    """
    Create a complete HTML page with embedded CSS and JavaScript for a searchable table.
    """
    
    # Convert DataFrame to HTML table
    table_html = df.to_html(
        table_id=table_id,
        classes="table table-striped table-hover",
        index=False,
        escape=False
    )
    
    # Get column names for filter dropdowns
    columns = df.columns.tolist()
    
    # Create filter dropdowns HTML
    filter_dropdowns = ""
    for i, col in enumerate(columns):
        unique_values = sorted(df[col].astype(str).unique())
        options = ''.join([f'<option value="{val}">{val}</option>' for val in unique_values])
        filter_dropdowns += f'''
        <div class="col-md-3 mb-2">
            <label for="filter-{i}" class="form-label">{col}</label>
            <select class="form-select filter-select" data-column="{i}" id="filter-{i}">
                <option value="">All</option>
                {options}
            </select>
        </div>
        '''
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {{
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .container-fluid {{
            padding: 2rem;
        }}
        
        .card {{
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            border: none;
            border-radius: 0.5rem;
        }}
        
        .card-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 0.5rem 0.5rem 0 0 !important;
            padding: 1.5rem;
        }}
        
        .search-container {{
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        }}
        
        .table-container {{
            background-color: white;
            border-radius: 0.5rem;
            overflow: hidden;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        }}
        
        #data-table {{
            margin-bottom: 0;
        }}
        
        .table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.875rem;
            letter-spacing: 0.5px;
            padding: 1rem 0.75rem;
        }}
        
        .table td {{
            padding: 0.75rem;
            vertical-align: middle;
            border-color: #e9ecef;
        }}
        
        .table-striped tbody tr:nth-of-type(odd) {{
            background-color: rgba(102, 126, 234, 0.05);
        }}
        
        .table-hover tbody tr:hover {{
            background-color: rgba(102, 126, 234, 0.1);
            transform: scale(1.001);
            transition: all 0.2s ease-in-out;
        }}
        
        .search-input {{
            border: 2px solid #e9ecef;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        
        .search-input:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }}
        
        .filter-select {{
            border: 2px solid #e9ecef;
            border-radius: 0.5rem;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        
        .filter-select:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }}
        
        .stats-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
        }}
        
        .stats-number {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }}
        
        .stats-label {{
            font-size: 0.875rem;
            opacity: 0.9;
        }}
        
        .clear-filters {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 0.375rem;
            font-weight: 500;
            transition: all 0.2s ease-in-out;
        }}
        
        .clear-filters:hover {{
            transform: translateY(-1px);
            box-shadow: 0 0.25rem 0.5rem rgba(102, 126, 234, 0.3);
            color: white;
        }}
        
        .export-btn {{
            background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);
            border: none;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 0.375rem;
            font-weight: 500;
            transition: all 0.2s ease-in-out;
        }}
        
        .export-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 0.25rem 0.5rem rgba(54, 209, 220, 0.3);
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .container-fluid {{
                padding: 1rem;
            }}
            
            .table-responsive {{
                border-radius: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="card">
            <div class="card-header">
                <div class="row align-items-center">
                    <div class="col">
                        <h1 class="h3 mb-0">
                            <i class="bi bi-table"></i> {title}
                        </h1>
                        <p class="mb-0 mt-2 opacity-75">Interactive data table with search and filtering capabilities</p>
                    </div>
                    <div class="col-auto">
                        <div class="stats-card">
                            <div class="stats-number" id="total-rows">{len(df)}</div>
                            <div class="stats-label">Total Rows</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="search-container">
            <div class="row align-items-end">
                <div class="col-md-6 mb-2">
                    <label for="search-input" class="form-label fw-bold">
                        <i class="bi bi-search"></i> Search Table
                    </label>
                    <input type="text" class="form-control search-input" id="search-input" 
                           placeholder="Search across all columns...">
                </div>
                <div class="col-md-3 mb-2">
                    <button class="btn clear-filters" onclick="clearAllFilters()">
                        <i class="bi bi-arrow-clockwise"></i> Clear Filters
                    </button>
                </div>
                <div class="col-md-3 mb-2">
                    <button class="btn export-btn" onclick="exportFilteredData()">
                        <i class="bi bi-download"></i> Export CSV
                    </button>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <h6 class="fw-bold mb-3">
                        <i class="bi bi-funnel"></i> Column Filters
                    </h6>
                </div>
                {filter_dropdowns}
            </div>
            
            <div class="row mt-3">
                <div class="col">
                    <div class="d-flex align-items-center">
                        <span class="fw-bold me-2">Showing:</span>
                        <span id="visible-rows" class="badge bg-primary">{len(df)}</span>
                        <span class="mx-2">of</span>
                        <span id="total-rows-display" class="badge bg-secondary">{len(df)}</span>
                        <span class="ms-2">rows</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="table-container">
            <div class="table-responsive">
                {table_html}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let originalData = [];
        let filteredData = [];
        
        // Initialize the table
        document.addEventListener('DOMContentLoaded', function() {{
            const table = document.getElementById('{table_id}');
            const rows = Array.from(table.getElementsByTagName('tr'));
            
            // Skip header row
            originalData = rows.slice(1).map(row => {{
                return Array.from(row.cells).map(cell => cell.textContent.trim());
            }});
            
            filteredData = [...originalData];
            
            // Add search functionality
            const searchInput = document.getElementById('search-input');
            searchInput.addEventListener('input', function() {{
                filterTable();
            }});
            
            // Add filter functionality
            const filterSelects = document.querySelectorAll('.filter-select');
            filterSelects.forEach(select => {{
                select.addEventListener('change', function() {{
                    filterTable();
                }});
            }});
        }});
        
        function filterTable() {{
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const filterSelects = document.querySelectorAll('.filter-select');
            const table = document.getElementById('{table_id}');
            const rows = Array.from(table.getElementsByTagName('tr')).slice(1); // Skip header
            
            let visibleCount = 0;
            filteredData = [];
            
            rows.forEach((row, index) => {{
                let shouldShow = true;
                const cells = Array.from(row.cells);
                const rowData = cells.map(cell => cell.textContent.trim());
                
                // Apply search filter
                if (searchTerm) {{
                    const rowText = rowData.join(' ').toLowerCase();
                    if (!rowText.includes(searchTerm)) {{
                        shouldShow = false;
                    }}
                }}
                
                // Apply column filters
                filterSelects.forEach(select => {{
                    const columnIndex = parseInt(select.dataset.column);
                    const filterValue = select.value;
                    if (filterValue && rowData[columnIndex] !== filterValue) {{
                        shouldShow = false;
                    }}
                }});
                
                if (shouldShow) {{
                    row.style.display = '';
                    visibleCount++;
                    filteredData.push(rowData);
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            // Update visible count
            document.getElementById('visible-rows').textContent = visibleCount;
        }}
        
        function clearAllFilters() {{
            // Clear search
            document.getElementById('search-input').value = '';
            
            // Clear all filter selects
            const filterSelects = document.querySelectorAll('.filter-select');
            filterSelects.forEach(select => {{
                select.value = '';
            }});
            
            // Show all rows
            const table = document.getElementById('{table_id}');
            const rows = Array.from(table.getElementsByTagName('tr')).slice(1);
            rows.forEach(row => {{
                row.style.display = '';
            }});
            
            // Reset counts
            const totalRows = originalData.length;
            document.getElementById('visible-rows').textContent = totalRows;
            filteredData = [...originalData];
        }}
        
        function exportFilteredData() {{
            if (filteredData.length === 0) {{
                alert('No data to export!');
                return;
            }}
            
            // Get headers
            const table = document.getElementById('{table_id}');
            const headerRow = table.getElementsByTagName('tr')[0];
            const headers = Array.from(headerRow.cells).map(cell => cell.textContent.trim());
            
            // Create CSV content
            let csvContent = headers.join(',') + '\\n';
            filteredData.forEach(row => {{
                csvContent += row.map(cell => `"${{cell.replace(/"/g, '""')}}"`).join(',') + '\\n';
            }});
            
            // Download CSV
            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            if (link.download !== undefined) {{
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', 'filtered_data.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
        }}
    </script>
</body>
</html>
    """
    
    return html_template

def create_html_from_csv(csv_file, table_id="data-table", title="Data Table"):
    """
    Create HTML from CSV file with enhanced error handling.
    """
    try:
        # Try reading with different options to handle CSV parsing issues
        try:
            # First try: standard CSV reading
            df = pd.read_csv(csv_file, encoding='utf-8')
        except pd.errors.ParserError as e:
            print(f"⚠️  Standard CSV parsing failed: {e}")
            print("🔧 Attempting to fix common CSV issues...")
            
            try:
                # Second try: handle potential quoting issues
                df = pd.read_csv(csv_file, encoding='utf-8', quoting=1, escapechar='\\')
            except:
                try:
                    # Third try: use different error handling
                    df = pd.read_csv(csv_file, encoding='utf-8', error_bad_lines=False, warn_bad_lines=True)
                except:
                    # Fourth try: manual line-by-line parsing
                    print("🔧 Attempting manual CSV repair...")
                    df = repair_and_read_csv(csv_file)
        
        print(f"✅ Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
        # Rest of the existing function stays the same
        # Convert DataFrame to HTML table
        table_html = df.to_html(
            table_id=table_id,
            classes="table table-striped table-hover",
            index=False,
            escape=False
        )
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: File '{csv_file}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def convert_csv_to_html(input_file, output_file=None, title=None):
    """
    Convert a CSV file to a searchable HTML table.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output HTML file (optional)
        title (str): Title for the HTML page (optional)
    
    Returns:
        str: Path to the created HTML file
    """
    try:
        # Read CSV file with enhanced error handling
        print(f"Reading CSV file: {input_file}")
        
        # Try different pandas reading strategies
        df = None
        try:
            # First try: standard CSV reading
            df = pd.read_csv(input_file, encoding='utf-8')
        except pd.errors.ParserError as e:
            print(f"⚠️  Standard CSV parsing failed: {e}")
            print("🔧 Attempting to fix common CSV issues...")
            
            try:
                # Second try: handle potential quoting issues
                df = pd.read_csv(input_file, encoding='utf-8', quoting=1)
            except Exception:
                try:
                    # Third try: more lenient parsing
                    df = pd.read_csv(input_file, encoding='utf-8', on_bad_lines='skip')
                except Exception:
                    try:
                        # Fourth try: manual CSV repair
                        print("🔧 Attempting manual CSV repair...")
                        df = repair_and_read_csv(input_file)
                    except Exception as final_error:
                        print(f"❌ All CSV parsing attempts failed: {final_error}")
                        print("💡 Try manually fixing the CSV file:")
                        print("   - Check for unescaped commas in text fields")
                        print("   - Ensure all text fields with commas are quoted")
                        print("   - Remove any stray quote characters")
                        sys.exit(1)
        
        if df is None or df.empty:
            raise ValueError("The CSV file is empty or could not be read properly.")
        
        print(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns")
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = input_path.with_suffix('.html')
        
        # Generate title if not provided
        if not title:
            title = f"Data from {Path(input_file).stem}"
        
        # Create HTML content
        print("Generating HTML table...")
        html_content = create_html_template(df, title=title)
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML table created successfully: {output_file}")
        print(f"🌐 Open {output_file} in your web browser to view the searchable table.")
        
        return str(output_file)
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

def repair_and_read_csv(csv_file):
    """
    Attempt to repair common CSV issues and read the file.
    """
    import csv
    import io
    
    print("🔧 Analyzing CSV structure...")
    
    # Read the file and try to detect issues
    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check header to determine expected column count
    header_line = lines[0].strip()
    # Count columns in header (accounting for quoted fields)
    header_reader = csv.reader([header_line])
    expected_cols = len(next(header_reader))
    
    print(f"📊 Expected columns: {expected_cols}")
    
    # Process each line and fix common issues
    fixed_lines = []
    issues_found = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Use CSV reader to properly parse the line
        try:
            reader = csv.reader([line])
            row = next(reader)
            actual_cols = len(row)
            
            if actual_cols == expected_cols:
                fixed_lines.append(line)
            else:
                issues_found += 1
                print(f"⚠️  Line {i+1}: Found {actual_cols} columns, expected {expected_cols}")
                
                if actual_cols > expected_cols:
                    # Too many columns - try to fix by re-quoting fields
                    try:
                        # Try to reconstruct with proper CSV quoting
                        output = io.StringIO()
                        writer = csv.writer(output)
                        # Take only the expected number of columns
                        writer.writerow(row[:expected_cols])
                        fixed_line = output.getvalue().strip()
                        fixed_lines.append(fixed_line)
                        print(f"🔧 Fixed line {i+1}")
                    except:
                        fixed_lines.append(line)  # Keep as-is if we can't fix it
                else:
                    # Too few columns - pad with empty strings
                    padded_row = row + [''] * (expected_cols - actual_cols)
                    output = io.StringIO()
                    writer = csv.writer(output)
                    writer.writerow(padded_row)
                    fixed_line = output.getvalue().strip()
                    fixed_lines.append(fixed_line)
                    print(f"🔧 Padded line {i+1}")
        except Exception as line_error:
            print(f"⚠️  Could not parse line {i+1}: {line_error}")
            fixed_lines.append(line)  # Keep original line
    
    if issues_found > 0:
        print(f"🔧 Found and attempted to fix {issues_found} problematic lines")
    
    # Create a StringIO object from the fixed lines
    fixed_csv = '\n'.join(fixed_lines)
    csv_buffer = io.StringIO(fixed_csv)
    
    # Read the fixed CSV
    try:
        df = pd.read_csv(csv_buffer, encoding='utf-8')
        print(f"✅ Successfully repaired and loaded CSV")
        return df
    except Exception as e:
        print(f"❌ Even after repair, could not read CSV: {e}")
        raise e

def main():
    parser = argparse.ArgumentParser(
        description="Convert CSV files to beautiful, searchable HTML tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv_to_html_table.py data.csv
  python csv_to_html_table.py data.csv output.html
  python csv_to_html_table.py data.csv --title "Sales Report"
        """
    )
    
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('output_file', nargs='?', help='Output HTML file path (optional)')
    parser.add_argument('--title', '-t', help='Title for the HTML page')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Convert CSV to HTML
    output_path = convert_csv_to_html(args.input_file, args.output_file, args.title)
    
    print(f"\n✅ Conversion completed successfully!")
    print(f"📊 HTML table saved to: {output_path}")
    print(f"🌐 Open the file in your web browser to view the interactive table.")

if __name__ == "__main__":
    main() 