from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional
import time

import ijson


class VICParser:
    """Parser for Project VIC JSON files with memory-efficient streaming capabilities."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.context = None
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def get_context(self, cancel_check: Optional[Callable[[], None]] = None) -> str:
        """Get the @odata.context from the input file."""
        if self.context is None:
            with open(self.file_path, 'rb') as f:
                parser = ijson.parse(f)
                for prefix, event, value in parser:
                    if cancel_check is not None:
                        cancel_check()
                    if prefix == '@odata.context':
                        self.context = value
                        break
        return self.context

    def count_items(
        self,
        cancel_check: Optional[Callable[[], None]] = None,
        progress: Optional[Callable[[int], None]] = None,
    ) -> int:
        """Count the total number of items in the JSON array.

        cancel_check is invoked periodically so a GUI can interrupt this pass.
        A short sleep is included so the UI thread can process a Cancel click.
        """
        count = 0
        last_coop = time.monotonic()
        with open(self.file_path, 'rb') as f:
            for _ in ijson.items(f, 'value.item'):
                count += 1
                now = time.monotonic()
                if now - last_coop >= 0.05:
                    last_coop = now
                    if cancel_check is not None:
                        cancel_check()
                    if progress is not None:
                        progress(count)
                    # Yield the GIL so Tk can handle Cancel immediately.
                    time.sleep(0.001)
        return count

    def stream_items(self, category: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """Stream through items in the VIC data, optionally filtering by category."""
        with open(self.file_path, 'rb') as f:
            for item in ijson.items(f, 'value.item'):
                if category is None or (isinstance(item, dict) and item.get('Category') == category):
                    yield item
