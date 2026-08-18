import argparse
import sys
from pathlib import Path

import ijson
from tqdm import tqdm

from vic_catparser.formatter import OutputFormatter
from vic_catparser.service import process_vic


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project VIC JSON Parser - Process and filter VIC JSON data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.json 1                           # Find Category 1 items, output as JSON
  %(prog)s input.json 0 -f readable               # Find Category 0 items in readable format
  %(prog)s input.json 2 -o Category2.json         # Save Category 2 items to a file
  %(prog)s input.json 1 -f hashonly --hash md5    # Output only MD5 hashes
  %(prog)s input.json 1 -f hashonly --hash sha1   # Output only SHA1 hashes
        """
    )
    parser.add_argument("json_file", help="Path to the VIC JSON file")
    parser.add_argument("category", type=int, help="Category number to search for")
    parser.add_argument("-o", "--output", metavar="OUTPUTFILE", help="Optional output file for results")
    parser.add_argument("-f", "--format", choices=['json', 'readable', 'hashonly'], default='json',
                        dest='output_format',
                        help="Output format: 'json', 'readable', or 'hashonly' (default: json). "
                             "The 'hashonly' format option requires the --hash option to be specified, "
                             "and outputs the chosen hashes one per line.")
    parser.add_argument("--hash", choices=['md5', 'sha1', 'photodna'], default='md5',
                        help="Hash type to output when using the 'hashonly' format option (default: md5). "
                             "Otherwise this option is ignored")

    args = parser.parse_args()
    formatter = OutputFormatter()
    output_file = Path(args.output) if args.output else None
    stream_immediately = not args.output and args.output_format in ('readable', 'hashonly')
    total_items = 0
    pbar = None

    def match_callback(item):
        if stream_immediately:
            if args.output_format == 'readable':
                print(formatter.format_readable(item))
            elif args.output_format == 'hashonly':
                hash_line = formatter.format_hashonly(item, args.hash)
                if hash_line:
                    print(hash_line, end='')

    def status_callback(message: str):
        if message.startswith("Counting") and "so far" not in message:
            print(message)
        elif message.startswith("Searching"):
            print(f"\nSearching {message.split()[1]} items for desired Category: {args.category}")

    def progress_callback(current: int, total: int):
        nonlocal pbar
        if pbar is None:
            pbar = tqdm(total=total, unit='items')
        pbar.update(1)

    try:
        result = process_vic(
            Path(args.json_file),
            args.category,
            output_format=args.output_format,
            hash_type=args.hash,
            output_file=output_file,
            status_callback=status_callback,
            progress_callback=progress_callback,
            match_callback=match_callback if stream_immediately else None,
        )

        if pbar is not None:
            pbar.close()

        print(f"\nFound {result.matches_found} matches for Category {args.category}")

        if args.output and result.matches:
            print(f"Results have been saved to {args.output}")
        elif args.output_format == 'json' and not args.output:
            print(formatter.format_json(result.matches, result.context))

        if result.empty_hash_count > 0:
            print(f"Warning: {result.empty_hash_count} {args.hash} hashes were empty "
                  f"and not included in the output.")

    except ijson.JSONError as e:
        if pbar is not None:
            pbar.close()
        print(f"Error: Invalid JSON file: {e}")
        return 1
    except Exception as e:
        if pbar is not None:
            pbar.close()
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
