# VIC-CatParser

Category Parser for ProjectVIC files

## Description ##

The standard distribution file from Project VIC contains items from every Category interspersed together in the same file. While this is convenient for most forensic analysis tools, it may be useful in certain cases to isolate Category items into their own file. For example, during a triage operation in the field, you might only be interested in matching Category 1 items.

This project allows the extraction of items matching a specific Category from a properly formatted Project VIC JSON file. The located items can then be output to their own file, or output to the screen, if desired.

## Requirements ##

**Quick summary *(tl;dr)*:**  Any Project VIC file that is uncompressed may be processed by these tools. A standard install/environment for Python 3 is necessary, along with the required packages listed in the project.

### Detailed Requirements ###

* Your system must have a working Python 3 environment installed.
* Having a working **pip3** installation is strongly recommended, and is required for automatic processing of the *requirements.txt* file.
* Ensure the required packages are installed from the *requirements.txt* file. With pip3 installed, this can be done as follows:
    ```
    pip3 install -r requirements.txt
    ```
* Your source Project VIC file must be uncompressed/unzipped prior to processing.
* The generated Project VIC Category file may be quite large depending on the source file and chosen output Category. Ensure you have enough disk space in your output drive/location.

## Installation ##

The script(s) in this project are standalone and do not require any special installation beyond the above Requirements.

## Usage ##

```
usage: vic-catparser.py [-h] [-o OUTPUTFILE] [-f {json,readable,hashonly}] [--hash {md5,sha1,photodna}]
                        json_file category

positional arguments:
  json_file             Path to the VIC JSON file
  category              Category number to search for

options:
  -h, --help            show this help message and exit
  -o OUTPUTFILE, --output OUTPUTFILE
                        Optional output file for results
  -f {json,readable,hashonly}, --format {json,readable,hashonly}
                        Output format: 'json', 'readable', or 'hashonly' (default: json). The 'hashonly' format option
                        requires the --hash option to be specified, and outputs the chosen hashes one per line.
  --hash {md5,sha1,photodna}
                        Hash type to output when using the 'hashonly' format option (default: md5). Otherwise this
                        option is ignored

Examples:
  vic-catparser.py input.json 1                      # Find Category 1 items, output as JSON
  vic-catparser.py input.json 0 -f readable          # Find Category 0 items in readable format
  vic-catparser.py input.json 2 -o Category2.json    # Save Category 2 items to a file
  vic-catparser.py input.json 1 -f hashonly --hash md5     # Output only MD5 hashes
  vic-catparser.py input.json 1 -f hashonly --hash sha1    # Output only SHA1 hashes
```

### Output Formats ###

The script supports three output formats:

1. **json** (default): Outputs the full JSON data in Project VIC format, including @odata.context
2. **readable**: Human-readable format showing all fields with clear labels
3. **hashonly**: Outputs only the specified hash type (MD5, SHA1, or PhotoDNA), one per line. Use the `--hash` option to specify which hash type you want:
   - `--hash md5` (default): Output MD5 hashes
   - `--hash sha1`: Output SHA1 hashes
   - `--hash photodna`: Output PhotoDNA hashes

## Utility Tools ##

The project includes several utility tools in the `utils` directory:

### JSON Structure Analyzer ###

Located at `utils/json_structure_analyzer.py`, this tool helps analyze the structure of any JSON file. It is useful for understanding the schema of Project VIC files or verifying the structure of output files.

Usage:
```
python3 utils/json_structure_analyzer.py input.json [--max-sample 50]
```

### Example Files ###

- `utils/example-VIC-data.json`: A minimal example of a Project VIC JSON file and structure
- `utils/example-VIC-structure.txt`: Basic structure analysis of a Project VIC file

These examples can help with understanding a basic Project VIC file format and with test the tools.

## Support ##

Please use the project Issues List to report any bugs or request enhancements.

## Contributing

If you would like to contribute to the project, feel free to create a Pull Request and provide the necessary explanations/documentation with your request.  For detailed submissions, please create a corresponding request on the Issues List.

### License ###

This project is freely available for use and modification under the Apache 2.0 license. For further information, see the project COPYRIGHT documentation.

