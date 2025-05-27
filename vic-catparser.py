#!/usr/bin/env python3

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional
import ijson
import sys
from tqdm import tqdm

class VICParser:
    """Parser for Project VIC JSON files with memory-efficient streaming capabilities."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def count_items(self) -> int:
        """Count the total number of items in the JSON array."""
        count = 0
        with open(self.file_path, 'rb') as f:
            for _ in ijson.items(f, 'value.item'):
                count += 1
        return count

    def stream_items(self, category: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """Stream through items in the VIC data, optionally filtering by category.
        
        Args:
            category: Optional category number to filter by. If None, returns all items.
        """
        with open(self.file_path, 'rb') as f:
            for item in ijson.items(f, 'value.item'):
                if category is None or (isinstance(item, dict) and item.get('Category') == category):
                    yield item

class OutputFormatter:
    """Handles formatting and output of VIC data items."""

    @staticmethod
    def format_readable(item: Dict[str, Any]) -> str:
        """Format a single item as a readable string."""
        output = []
        output.append("----------------------------------------")
        output.append(f"MediaID: {item.get('MediaID')}")
        output.append(f"MD5: {item.get('MD5')}")
        output.append(f"SHA1: {item.get('SHA1')}")
        output.append(f"PhotoDNA: {item.get('PhotoDNA')}")
        output.append(f"MediaSize: {item.get('MediaSize')}")
        output.append(f"DateUpdated: {item.get('DateUpdated')}")
        if 'Exifs' in item:
            output.append("Exif Data:")
            for exif in item['Exifs']:
                output.append(f"  - {exif.get('PropertyName')}: {exif.get('PropertyValue')}")
        output.append("----------------------------------------\n")
        return '\n'.join(output)

    @staticmethod
    def format_json(item: Dict[str, Any]) -> str:
        """Format a single item as a JSON string."""
        return json.dumps(item, separators=(',', ':'))

def main():
    parser = argparse.ArgumentParser(
        description="Project VIC JSON Parser - Process and filter VIC JSON data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.json 1                      # Find Category 1 items, output as JSON
  %(prog)s input.json 0 -f readable          # Find Category 0 items in readable format
  %(prog)s input.json 2 -o Category2.json    # Save Category 2 items to a file
        """
    )
    parser.add_argument("json_file", help="Path to the VIC JSON file")
    parser.add_argument("category", type=int, help="Category number to search for")
    parser.add_argument("-o", "--output", help="Optional output file for results")
    parser.add_argument("-f", "--format", choices=['json', 'readable'], default='json',
                      dest='output_format',
                      help="Output format: 'json' or 'readable' (default: json)")
    
    args = parser.parse_args()
    
    try:
        # Initialize parser
        vic_parser = VICParser(Path(args.json_file))
        formatter = OutputFormatter()
        
        # Count items and prepare progress bar
        print("Counting total items in all categories...")
        total_items = vic_parser.count_items()
        print(f"\nSearching {total_items} items for desired Category: {args.category}")

        # Process items
        matches = []
        with tqdm(total=total_items, unit='items') as pbar:
            for item in vic_parser.stream_items(args.category):
                if args.output:
                    matches.append(item)
                else:
                    # Print immediately for console output
                    if args.output_format == 'readable':
                        print(formatter.format_readable(item))
                    else:  # json format
                        print(formatter.format_json(item))
                pbar.update(1)

        # Handle file output if specified
        if args.output:
            print(f"\nWriting results to {args.output}...")
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.output_format == 'readable':
                    for item in matches:
                        f.write(formatter.format_readable(item))
                else:  # json format
                    json.dump(matches, f, separators=(',', ':'))
            print(f"Results have been saved to {args.output}")
        
    except ijson.JSONError as e:
        print(f"Error: Invalid JSON file: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 