# Tally Response XML Cleaner

A simple Python application to clean Tally XML files by removing empty tags and unwanted sections.

## Features

- Removes all empty XML tags (tags with no content or only whitespace)
- Removes entire COMPANY sections (TALLYMESSAGE elements containing COMPANY data)
- Preserves the structure and formatting of important data
- Works on Windows and Linux
- Can process files or accept input via stdin/paste

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone or download this repository
2. Ensure Python 3.6+ is installed:
   ```bash
   python --version
   ```

No additional packages need to be installed.

## Usage

### Basic Usage

Clean a single XML file:
```bash
python xml_cleaner.py input.xml
```

This will create a cleaned file named `input_cleaned.xml` in the same directory.

### Specify Output File

```bash
python xml_cleaner.py input.xml -o output.xml
```

### Using Paste/Stdin

You can paste XML content directly:

**On Linux/Mac:**
```bash
cat input.xml | python xml_cleaner.py - -o output.xml
```

**On Windows (PowerShell):**
```powershell
Get-Content input.xml | python xml_cleaner.py - -o output.xml
```

**Interactive paste:**
```bash
python xml_cleaner.py - -o output.xml
# Then paste your XML content and press Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows)
```

### Output to stdout

```bash
python xml_cleaner.py input.xml -o -
```

## What Gets Removed

### 1. Empty Tags

All tags with no content or only whitespace are removed:

**Before:**
```xml
<RATEDETAILS.LIST>       </RATEDETAILS.LIST>
<SUMMARYALLOCS.LIST>       </SUMMARYALLOCS.LIST>
<SERVICETAXDETAILS.LIST>       </SERVICETAXDETAILS.LIST>
```

**After:**
These tags are completely removed.

### 2. COMPANY Sections

All `<TALLYMESSAGE>` elements that contain `<COMPANY>` data are removed:

**Before:**
```xml
<TALLYMESSAGE xmlns:UDF="TallyUDF">
  <COMPANY>
    <REMOTECMPINFO.LIST MERGE="Yes">
      <NAME>f6f96fa4-c9c6-463a-a4fe-544548a2867c</NAME>
      <REMOTECMPNAME>PRIMARY AUTO TRADING CO. W.L.L.</REMOTECMPNAME>
      <REMOTECMPSTATE>Al Asimah</REMOTECMPSTATE>
    </REMOTECMPINFO.LIST>
  </COMPANY>
</TALLYMESSAGE>
```

**After:**
This entire `<TALLYMESSAGE>` block is removed.

## Examples

### Example 1: Clean a file with default output name

```bash
python xml_cleaner.py tally_response.xml
```

Output: `tally_response_cleaned.xml`

### Example 2: Clean and specify output location

```bash
python xml_cleaner.py data/input.xml -o data/cleaned/output.xml
```

### Example 3: Process multiple files (bash script)

```bash
for file in *.xml; do
    python xml_cleaner.py "$file" -o "cleaned_$file"
done
```

### Example 4: Process multiple files (PowerShell)

```powershell
Get-ChildItem *.xml | ForEach-Object {
    python xml_cleaner.py $_.Name -o "cleaned_$($_.Name)"
}
```

## Help

To see all available options:
```bash
python xml_cleaner.py --help
```

## Troubleshooting

### Error: "Input file not found"
- Check that the file path is correct
- Use quotes around paths with spaces: `python xml_cleaner.py "my file.xml"`

### Error: "Error parsing XML file"
- Ensure your input file is valid XML
- Check that the file is not corrupted
- Verify the file encoding is UTF-8

### Permission Denied
- On Linux/Mac, you may need to make the script executable:
  ```bash
  chmod +x xml_cleaner.py
  ./xml_cleaner.py input.xml
  ```

## License

This is free and unencumbered software released into the public domain.

## Contributing

Feel free to submit issues or pull requests for improvements.
