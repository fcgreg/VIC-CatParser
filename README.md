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
    pip install -r requirements.txt
    ```
* Your source Project VIC file must be uncompressed/unzipped prior to processing.
* The generated Project VIC Category file may be quite large depending on the source file and chosen output Category. Ensure you have enough disk space in your output drive/location.

## Installation ##

The script(s) in this project are standalone and do not require any special installation beyond the above Requirements.

## Usage ##

```
usage: vic-catparser.py [-h] [-o OUTPUT] [-f {json,readable}] json_file category

Project VIC JSON Parser - Process and filter VIC JSON data files

positional arguments:
  json_file             Path to the VIC JSON file
  category              Category number to search for

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Optional output file for results
  -f {json,readable}, --format {json,readable}
                        Output format: 'json' or 'readable' (default: json)

Examples:
  vic-catparser.py input.json 1                      # Find Category 1 items, output as JSON
  vic-catparser.py input.json 0 -f readable          # Find Category 0 items in readable format
  vic-catparser.py input.json 2 -o Category2.json    # Save Category 2 items to a file
```

## Support ##

Please use the project Issues List to report any bugs or request enhancements.

## Contributing

If you would like to contribute to the project, feel free to create a Pull Request and provide the necessary explanations/documentation with your request.  For detailed submissions, please create a corresponding request on the Issues List.

### License ###

This project is freely available for use and modification under the Apache 2.0 license. For further information, see the project COPYRIGHT documentation.

