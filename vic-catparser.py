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
        self.context = None
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def get_context(self) -> str:
        """Get the @odata.context from the input file."""
        if self.context is None:
            with open(self.file_path, 'rb') as f:
                # Get just the context field
                parser = ijson.parse(f)
                for prefix, event, value in parser:
                    if prefix == '@odata.context':
                        self.context = value
                        break
        return self.context

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
        output.append("\n")
        return '\n'.join(output)

    @staticmethod
    def format_hashonly(item: Dict[str, Any], hash_type: str) -> Optional[str]:
        """Format a single item to output only the specified hash type.
        
        Args:
            item: The item containing hash values
            hash_type: Type of hash to output ('md5', 'sha1', or 'photodna')
            
        Returns:
            A string containing the hash value and newline if the hash exists,
            or None if the hash value is empty.
        """
        hash_map = {
            'md5': 'MD5',
            'sha1': 'SHA1',
            'photodna': 'PhotoDNA'
        }
        hash_value = item.get(hash_map[hash_type], '')
        return f"{hash_value}\n" if hash_value else None

    @staticmethod
    def format_json(items: List[Dict[str, Any]], context: str) -> str:
        """Format items as a JSON string with @odata.context."""
        vic_data = {
            "@odata.context": context,
            "value": items
        }
        return json.dumps(vic_data, separators=(',', ':'))

    @staticmethod
    def write_json_file(items: List[Dict[str, Any]], context: str, file_path: str) -> None:
        """Write items to a file in VIC JSON format with @odata.context."""
        vic_data = {
            "@odata.context": context,
            "value": items
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(vic_data, f, separators=(',', ':'))

def main():
    parser = argparse.ArgumentParser(
        description="Project VIC JSON Parser - Process and filter VIC JSON data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.json 1                      # Find Category 1 items, output as JSON
  %(prog)s input.json 0 -f readable          # Find Category 0 items in readable format
  %(prog)s input.json 2 -o Category2.json    # Save Category 2 items to a file
  %(prog)s input.json 1 -f hashonly --hash md5     # Output only MD5 hashes
  %(prog)s input.json 1 -f hashonly --hash sha1    # Output only SHA1 hashes
        """
    )
    parser.add_argument("json_file", help="Path to the VIC JSON file")
    parser.add_argument("category", type=int, help="Category number to search for")
    parser.add_argument("-o", "--output", metavar="OUTPUTFILE", help="Optional output file for results")
    parser.add_argument("-f", "--format", choices=['json', 'readable', 'hashonly'], default='json',
                      dest='output_format',
                      help="Output format: 'json', 'readable', or 'hashonly' (default: json). The 'hashonly' format option requires the --hash option to be specified, and outputs the chosen hashes one per line.")
    parser.add_argument("--hash", choices=['md5', 'sha1', 'photodna'], default='md5',
                      help="Hash type to output when using the 'hashonly' format option (default: md5). Otherwise this option is ignored")
    
    args = parser.parse_args()
    
    try:
        # Initialize parser
        vic_parser = VICParser(Path(args.json_file))
        formatter = OutputFormatter()
        
        # Get the context from the input file
        context = vic_parser.get_context()
        
        # Count items and prepare progress bar
        print("Counting total items in all categories...")
        total_items = vic_parser.count_items()
        print(f"\nSearching {total_items} items for desired Category: {args.category}")

        # Process items
        matches = [] # List of matches found for later output processing
        matches_found_count = 0 # Total count of matches found
        hash_matches_processed_count = 0 # Total count of hash matches processed. If hashes are needed but these are not equal, it means some of the hash fields were empty. Print a message if this is the case.
        with tqdm(total=total_items, unit='items') as pbar:
            for item in vic_parser.stream_items():
                # Check if the item is valid and if the Category matches the desired category
                if (isinstance(item, dict) and item.get('Category') == args.category):
                    # We found a match. Update the matches count.
                    matches_found_count += 1
                    # Add the match to the list of matches for later output processing, unless we dumping to the console output (which we do right away)
                    if args.output or args.output_format == 'json':
                        matches.append(item)
                    else:
                        # Print immediately for readable or hashonly format
                        if args.output_format == 'readable':
                            print(formatter.format_readable(item))
                        elif args.output_format == 'hashonly':
                            hash_line = formatter.format_hashonly(item, args.hash)
                            if hash_line:
                                print(hash_line, end='')
                # Done processing this item. Update the progress bar.
                pbar.update(1)

        print(f"\nFound {matches_found_count} matches for Category {args.category}")

        # Handle output processing if an output file is specified and we have matches to process
        if args.output and matches:
            print(f"\nWriting results to {args.output}...")
            if args.output_format == 'readable':
                with open(args.output, 'w', encoding='utf-8') as f:
                    for item in matches:
                        f.write(formatter.format_readable(item))
            elif args.output_format == 'hashonly':
                with open(args.output, 'w', encoding='utf-8') as f:
                    for item in matches:
                        hash_line = formatter.format_hashonly(item, args.hash)
                        if hash_line:
                            # We found a non-empty hash. Update the hash matches processed count and print the output.
                            hash_matches_processed_count += 1
                            f.write(hash_line)
            else:  # json format
                formatter.write_json_file(matches, context, args.output)
            print(f"Results have been saved to {args.output}")
        elif args.output_format == 'json':
            # Print JSON to console
            print(formatter.format_json(matches, context))
        
        # If we are in hashonly mode, print a warning if the hash matches processed count is less than the matches found count. This means some of the hash fields were empty.
        if args.output_format == 'hashonly' and (hash_matches_processed_count < matches_found_count):
            print(f"Warning: {matches_found_count - hash_matches_processed_count} {args.hash} hashes were empty and not included in the output.")
        
    except ijson.JSONError as e:
        print(f"Error: Invalid JSON file: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 