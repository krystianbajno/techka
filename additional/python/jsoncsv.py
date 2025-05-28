#!/usr/bin/env python3
"""
OSINT JSON to CSV Converter
Converts nested JSON structures (like osintpl.json) into flat CSV format.

Usage:
    python json_to_csv_converter.py input.json [output.csv]
    
If no output file is specified, it will create one based on the input filename.
"""

import json
import pandas as pd
import argparse
import sys
import os
from pathlib import Path

def extract_tools_from_json(data, category_path="", results=None):
    """
    Recursively extract tools from nested JSON structure and flatten into list.
    
    Args:
        data (dict): JSON data structure
        category_path (str): Current category path (for nested folders)
        results (list): Accumulator for results
    
    Returns:
        list: List of dictionaries representing tools
    """
    if results is None:
        results = []
    
    # Handle different data types
    if isinstance(data, dict):
        item_name = data.get('name', '')
        item_type = data.get('type', '')
        
        # Handle root level with children but no explicit type
        if 'children' in data and not item_type:
            # This is likely the root level, process children
            for child in data['children']:
                extract_tools_from_json(child, category_path, results)
                
        elif item_type == 'url':
            # This is an actual tool/resource
            tool_entry = {
                'Category': category_path,
                'Name': item_name,
                'URL': data.get('url', ''),
                'Description': '',  # Not available in osintpl.json structure
                'Cost': '',         # Not available in osintpl.json structure  
                'Details': ''       # Not available in osintpl.json structure
            }
            results.append(tool_entry)
            
        elif item_type == 'folder' and 'children' in data:
            # This is a folder, process its children with updated path
            if category_path:
                new_category_path = f"{category_path} > {item_name}"
            else:
                new_category_path = item_name
                
            for child in data['children']:
                extract_tools_from_json(child, new_category_path, results)
                
    elif isinstance(data, list):
        # Process list of items
        for item in data:
            extract_tools_from_json(item, category_path, results)
    
    return results

def infer_cost_from_name(name):
    """
    Try to infer cost information from the tool name.
    
    Args:
        name (str): Tool name
        
    Returns:
        str: Inferred cost (Free, Paid, Partially Free, or empty)
    """
    name_lower = name.lower()
    
    # Look for indicators in the name
    if '(r)' in name_lower:
        return 'Registration Required'
    elif '(t)' in name_lower:
        return 'Tool/App'
    elif '(m)' in name_lower:
        return 'Manual/Template'
    elif 'free' in name_lower:
        return 'Free'
    elif 'paid' in name_lower or 'premium' in name_lower:
        return 'Paid'
    else:
        return ''

def clean_tool_name(name):
    """
    Clean tool name by removing common suffixes.
    
    Args:
        name (str): Original name
        
    Returns:
        str: Cleaned name
    """
    # Remove common suffixes
    suffixes_to_remove = [' (R)', ' (T)', ' (M)', ' (r)', ' (t)', ' (m)']
    
    for suffix in suffixes_to_remove:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    return name.strip()

def generate_description_from_url(url):
    """
    Generate a basic description based on the URL domain.
    
    Args:
        url (str): Tool URL
        
    Returns:
        str: Generated description
    """
    if not url:
        return ''
    
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        # Remove common prefixes
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Generate basic description
        if 'github.com' in domain:
            return 'Open source tool hosted on GitHub'
        elif 'google.com' in domain or 'googleapis.com' in domain:
            return 'Google service or tool'
        elif '.gov' in domain:
            return 'Government official resource'
        elif '.edu' in domain:
            return 'Educational institution resource'
        elif 'facebook.com' in domain or 'fb.com' in domain:
            return 'Facebook-related resource'
        elif domain.endswith('.pl'):
            return 'Polish language resource'
        else:
            return f'Web-based resource from {domain}'
    except:
        return 'Web-based resource'

def convert_json_to_csv(input_file, output_file=None, add_descriptions=True):
    """
    Convert JSON file to CSV format.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output CSV file (optional)
        add_descriptions (bool): Whether to generate basic descriptions
        
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Read JSON file
        print(f"Reading JSON file: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Extract tools from JSON
        print("Extracting tools from JSON structure...")
        tools = extract_tools_from_json(json_data)
        
        if not tools:
            raise ValueError("No tools found in the JSON structure.")
        
        print(f"Found {len(tools)} tools/resources")
        
        # Process and clean data
        for tool in tools:
            # Clean tool name and infer cost
            original_name = tool['Name']
            tool['Name'] = clean_tool_name(original_name)
            tool['Cost'] = infer_cost_from_name(original_name)
            
            # Generate basic description if requested
            if add_descriptions:
                tool['Description'] = generate_description_from_url(tool['URL'])
        
        # Create DataFrame
        df = pd.DataFrame(tools)
        
        # Ensure columns are in the right order
        column_order = ['Category', 'Name', 'URL', 'Description', 'Cost', 'Details']
        df = df[column_order]
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = input_path.with_suffix('.csv')
        
        # Write CSV file
        print(f"Writing CSV file: {output_file}")
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"✅ Conversion completed successfully!")
        print(f"📊 CSV file saved to: {output_file}")
        print(f"📈 Total tools converted: {len(tools)}")
        
        # Print category summary
        category_counts = df['Category'].value_counts()
        print(f"\n📋 Categories found:")
        for category, count in category_counts.head(10).items():
            print(f"  • {category}: {count} tools")
        if len(category_counts) > 10:
            print(f"  ... and {len(category_counts) - 10} more categories")
        
        return str(output_file)
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Convert nested JSON files to CSV format (like osintpl.json to bellingcat.csv style)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python json_to_csv_converter.py osintpl.json
  python json_to_csv_converter.py data.json output.csv
  python json_to_csv_converter.py osintpl.json --no-descriptions
        """
    )
    
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('output_file', nargs='?', help='Output CSV file path (optional)')
    parser.add_argument('--no-descriptions', action='store_true', 
                       help='Skip generating basic descriptions from URLs')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Convert JSON to CSV
    add_descriptions = not args.no_descriptions
    output_path = convert_json_to_csv(args.input_file, args.output_file, add_descriptions)
    
    print(f"\n🎉 Use your CSV to HTML converter to create a searchable table:")
    print(f"   python csv_to_html_table.py {output_path}")

if __name__ == "__main__":
    main() 