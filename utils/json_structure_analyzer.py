#!/usr/bin/env python3

import json
import argparse
from typing import Any, Dict, List, Union
from pathlib import Path

def analyze_structure(data: Any, level: int = 0, max_sample_length: int = 50) -> str:
    """Analyze the structure of a JSON object and return a formatted string representation."""
    indent = "  " * level
    result = ""

    if isinstance(data, dict):
        if not data:
            return f"{indent}Empty dictionary {{}}\n"
        
        for key, value in data.items():
            result += f"{indent}{key} (dict key):\n"
            result += analyze_structure(value, level + 1, max_sample_length)
    
    elif isinstance(data, list):
        if not data:
            return f"{indent}Empty list []\n"
        
        result += f"{indent}List with {len(data)} items, first item type: {type(data[0]).__name__}\n"
        if data:
            result += analyze_structure(data[0], level + 1, max_sample_length)
    
    else:
        sample_value = str(data)
        if len(sample_value) > max_sample_length:
            sample_value = sample_value[:max_sample_length] + "..."
        
        result += f"{indent}Type: {type(data).__name__}, Sample: {sample_value}\n"
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Analyze the structure of a JSON file")
    parser.add_argument("json_file", help="Path to the JSON file to analyze")
    parser.add_argument("--max-sample", type=int, default=50,
                      help="Maximum length of sample values (default: 50)")
    
    args = parser.parse_args()
    file_path = Path(args.json_file)
    
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist")
        return 1
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\nStructure analysis of {file_path}:\n")
        print(analyze_structure(data, max_sample_length=args.max_sample))
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 