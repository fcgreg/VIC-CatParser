from dataclasses import dataclass, field
from pathlib import Path
from threading import Event
from typing import Callable, Dict, List, Optional
import time

from vic_catparser.formatter import OutputFormatter
from vic_catparser.parser import VICParser


class CancelledError(Exception):
    """Raised when processing is cancelled by the user."""


@dataclass
class ProcessResult:
    matches_found: int
    hash_matches_processed: int
    empty_hash_count: int
    output_path: Optional[Path]
    matches: List[Dict] = field(default_factory=list)
    context: Optional[str] = None


def _check_cancelled(cancel_event: Optional[Event]) -> None:
    if cancel_event is not None and cancel_event.is_set():
        raise CancelledError("Processing was cancelled.")


def process_vic(
    json_file: Path,
    category: int,
    output_format: str = "json",
    hash_type: str = "md5",
    output_file: Optional[Path] = None,
    *,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    match_callback: Optional[Callable[[Dict], None]] = None,
    cancel_event: Optional[Event] = None,
    collect_matches: bool = True,
    max_preview_matches: int = 500,
) -> ProcessResult:
    """Process a VIC JSON file and extract items matching the given category."""
    vic_parser = VICParser(json_file)
    formatter = OutputFormatter()

    def cancel_check() -> None:
        _check_cancelled(cancel_event)

    if status_callback:
        status_callback("Reading file context...")
    cancel_check()
    context = vic_parser.get_context(cancel_check=cancel_check)

    if status_callback:
        status_callback("Counting total items in all categories...")
    cancel_check()

    def count_progress(count: int) -> None:
        if status_callback:
            status_callback(f"Counting total items in all categories... ({count:,} so far)")

    total_items = vic_parser.count_items(cancel_check=cancel_check, progress=count_progress)

    if status_callback:
        status_callback(f"Searching {total_items} items for Category {category}...")

    store_matches = collect_matches and (output_file is not None or output_format == 'json')
    stream_immediately = not output_file and output_format in ('readable', 'hashonly')

    matches: List[Dict] = []
    preview_matches: List[Dict] = []
    matches_found_count = 0
    hash_matches_processed_count = 0
    processed = 0
    last_coop = time.monotonic()

    for item in vic_parser.stream_items():
        cancel_check()
        processed += 1

        if isinstance(item, dict) and item.get('Category') == category:
            matches_found_count += 1

            if store_matches:
                matches.append(item)
            elif len(preview_matches) < max_preview_matches:
                preview_matches.append(item)

            if match_callback:
                match_callback(item)

            if stream_immediately:
                if output_format == 'hashonly':
                    hash_line = formatter.format_hashonly(item, hash_type)
                    if hash_line:
                        hash_matches_processed_count += 1

        if progress_callback:
            progress_callback(processed, total_items)

        now = time.monotonic()
        if now - last_coop >= 0.05:
            last_coop = now
            time.sleep(0.001)

    output_path: Optional[Path] = None

    if output_file and matches:
        cancel_check()
        if status_callback:
            status_callback(f"Writing results to {output_file}...")

        output_path = output_file
        if output_format == 'readable':
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in matches:
                    f.write(formatter.format_readable(item))
        elif output_format == 'hashonly':
            hash_matches_processed_count = 0
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in matches:
                    hash_line = formatter.format_hashonly(item, hash_type)
                    if hash_line:
                        hash_matches_processed_count += 1
                        f.write(hash_line)
        else:
            formatter.write_json_file(matches, context, str(output_file))

    empty_hash_count = 0
    if output_format == 'hashonly' and hash_matches_processed_count < matches_found_count:
        empty_hash_count = matches_found_count - hash_matches_processed_count

    result_matches = matches if store_matches else preview_matches

    return ProcessResult(
        matches_found=matches_found_count,
        hash_matches_processed=hash_matches_processed_count,
        empty_hash_count=empty_hash_count,
        output_path=output_path,
        matches=result_matches,
        context=context,
    )
