# VIC-CatParser

Category Parser for Project VIC files

## Background ##

The standard distribution file from Project VIC contains items from every Category interspersed together in the same file. While this is convenient for most forensic analysis tools, it is sometimes useful to extract items from a specific Category into their own file. For example, during a triage operation in the field, you might only be interested in matching against Category 1 items, and scanning others would be a waste of time.

This project allows the easy scanning and extraction of items from a properly formatted Project VIC JSON file. The items are extracted by Category, *one Category at a time*. The located items can then be output into their own file, or output to the screen, if desired.

## Requirements ##

**Quick summary *(tl;dr)*:**  Any Project VIC file that is uncompressed can be processed by these tools. If you are using Windows, there are pre-built executables for you--no installation is required. If you are using another operating system (based on Linux, macOS, etc.), a standard install/environment for Python 3 is necessary, along with the required packages listed in the project.

Special Notes:

* Your source Project VIC file must be uncompressed/unzipped prior to processing.
* The generated Project VIC Category file may be quite large depending on the source file and chosen output Category. Ensure you have enough disk space in your output drive/location.

## Installation ##

Ensure that all files are unzipped together into the same folder so required libraries can be located. For Windows-based systems, nothing else is required.

### Installation requirements for development or running directly within Python on any system ###

* Your system needs a working Python 3 environment installed.
* Having a working **pip3** installation is strongly recommended, and is required for automatic processing of the *requirements.txt* file.
* Ensure the required packages are installed from the *requirements.txt* file. With pip3 installed, this can be done as follows:
    ```
    pip3 install -r requirements.txt
    ```

## Graphical User Interface ##

This project includes a Windows-friendly GUI built with the CustomTkinter package. The GUI provides the same core functionality as the CLI with a point-and-click interface. For this to work, you will need the TKinter packages installed on your system.

## Command-Line Usage ##

```
usage: vic-catparser.py [-h] [-o OUTPUTFILE] [-f {readable,hashonly,json}] [--hash {md5,sha1,photodna}] json_file category

positional arguments:
  json_file             Path to the VIC JSON file
  category              Category number to search for

options:
  -h, --help            show this help message and exit
  -o OUTPUTFILE, --output OUTPUTFILE
                        Optional output file for results
  -f {readable,hashonly,json}, --format {readable,hashonly,json}
                        Output format: 'readable', 'hashonly', or 'json' (default: hashonly). The 'hashonly' format outputs the chosen hashes one per line (see --hash).
  --hash {md5,sha1,photodna}
                        Hash type to output when using the 'hashonly' format option (default: md5). Otherwise this option is ignored

Examples:
  vic-catparser.py input.json 1                           # Find Category 1 items, output hashes only (defaults to "hashonly" option, outputs MD5 by default)
  vic-catparser.py input.json 0 -f readable               # Find Category 0 items and output in a readable format
  vic-catparser.py input.json 2 -f json -o Category2.json # Save Category 2 items to a file in JSON format
  vic-catparser.py input.json 1 --hash sha1               # Output only SHA1 hashes (Example here uses Category 1)
  vic-catparser.py input.json 1 -f json                   # Output full JSON to stdout (Example here uses Category 1)
```

The CLI can be launched via the package module, or from the built Windows executable:

```
python -m vic_catparser.cli input.json 1 -o Category1.json
VIC-CatParser.exe input.json 1 -o Category1.json
```

### Output Formats ###

The script supports three output formats:

1. **hashonly** (default): Outputs only the specified hash type (MD5, SHA1, or PhotoDNA), one per line. Use the `--hash` option to specify which hash type you want:
   - `--hash md5` (default): Output MD5 hashes
   - `--hash sha1`: Output SHA1 hashes
   - `--hash photodna`: Output PhotoDNA hashes
2. **json**: Outputs the full JSON data in Project VIC format, including @odata.context
3. **readable**: Human-readable format showing all fields with clear labels


## Development

### Running the GUI from a Python environment (or for development) ###

From the project root folder, after installing the requirements:

```
python -m gui.app
```

### Building the standalone Windows Executables ###

You can build two standalone Windows executables that run without a Python installation. Both are written to the same folder and share one `_internal/` runtime:

| File | Description |
|------|-------------|
| `dist/VIC-CatParser/VIC-CatParser.exe` | Console program; same arguments as `vic-catparser.py` |
| `dist/VIC-CatParser/VIC-CatParser-GUI.exe` | Windowed graphical app |

```
dist/VIC-CatParser/
├── VIC-CatParser.exe
├── VIC-CatParser-GUI.exe
└── _internal/
```

1. Install runtime and build dependencies:

```
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

2. Build both executables:

```
python -m PyInstaller build.spec
```

3. Close any running copy of VIC-CatParser or VIC-CatParser-GUI before rebuilding, or the build may fail with a permission error.

**Distribution:** Copy the entire `dist/VIC-CatParser/` folder. It includes both executable programs and a shared `_internal/` subfolder with `python314.dll`, CustomTkinter theme files, and other bundled libraries.

**Do not copy only the `.exe` files.** Both programs depend on `_internal/` sitting next to them.

#### Troubleshooting the executables ####

| Problem | Solution |
|---------|----------|
| *Failed to load Python DLL... python314.dll* | Copy the **entire** `dist/VIC-CatParser/` folder, including `_internal/`. Do not copy only the `.exe` files. |
| *CustomTkinter .json theme file could not be found* | This applies to `VIC-CatParser-GUI.exe` only. Confirm `_internal/customtkinter/assets/themes/blue.json` exists inside `dist/VIC-CatParser/`. Rebuild and copy the full folder. |
| Build fails with *Access is denied* | Close any running VIC-CatParser or VIC-CatParser-GUI process, then rebuild. |
| App blocked by antivirus | Add an exception for the folder, or sign the executable for production use. |
| App fails on another PC | Install the [Microsoft Visual C++ Redistributable (x64)](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist). The build already bundles these DLLs, but some locked-down systems still require the redistributable package. |

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

If you would like to contribute to the project, create a Pull Request and provide the necessary explanations/documentation with your request.  For detailed submissions, please create a corresponding request on the Issues List.

## License ##

This project is freely available for use and modification under the MIT License. See [LICENSE](LICENSE) and [COPYRIGHT.md](COPYRIGHT.md) for details.

