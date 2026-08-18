import json
from typing import Any, Dict, List, Optional


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
        """Format a single item to output only the specified hash type."""
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
