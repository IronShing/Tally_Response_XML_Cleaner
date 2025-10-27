#!/usr/bin/env python3
"""
Tally XML Cleaner
Removes empty tags and unwanted sections from Tally XML files.
"""

import xml.etree.ElementTree as ET
import argparse
import sys
from pathlib import Path


def remove_empty_elements(element):
    """
    Recursively remove empty elements from the XML tree.
    An element is considered empty if it has no children and its text is None, whitespace, or "0".
    """
    # Process children first (bottom-up approach)
    for child in list(element):
        remove_empty_elements(child)

    # Remove empty children
    for child in list(element):
        # Check if element is empty (no children, no meaningful text, no attributes)
        if len(child) == 0:
            text = child.text
            if text is None or text.strip() == "" or text.strip() == "0":
                # Only remove if no important attributes
                if len(child.attrib) == 0:
                    element.remove(child)


def remove_company_sections(root):
    """
    Remove all TALLYMESSAGE elements that contain COMPANY elements.
    """
    # Find all TALLYMESSAGE elements
    for parent in root.findall('.//REQUESTDATA'):
        for tallymessage in list(parent.findall('TALLYMESSAGE')):
            # Check if this TALLYMESSAGE contains a COMPANY element
            if tallymessage.find('COMPANY') is not None:
                parent.remove(tallymessage)


def clean_xml(input_file, output_file):
    """
    Clean the XML file by removing empty elements and company sections.

    Args:
        input_file: Path to input XML file
        output_file: Path to output XML file
    """
    try:
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Remove company sections
        remove_company_sections(root)

        # Remove empty elements
        remove_empty_elements(root)

        # Write the cleaned XML to output file
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"✓ Successfully cleaned XML file")
        print(f"  Input:  {input_file}")
        print(f"  Output: {output_file}")

        return True

    except ET.ParseError as e:
        print(f"✗ Error parsing XML file: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return False


def clean_xml_from_string(xml_string):
    """
    Clean XML from a string and return the cleaned string.

    Args:
        xml_string: XML content as string

    Returns:
        Cleaned XML as string
    """
    try:
        # Parse the XML string
        root = ET.fromstring(xml_string)

        # Remove company sections
        remove_company_sections(root)

        # Remove empty elements
        remove_empty_elements(root)

        # Convert back to string
        return ET.tostring(root, encoding='unicode')

    except ET.ParseError as e:
        print(f"✗ Error parsing XML string: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Clean Tally XML files by removing empty tags and unwanted sections.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clean a single file
  python xml_cleaner.py input.xml -o output.xml

  # Clean a file (output will be input_cleaned.xml)
  python xml_cleaner.py input.xml

  # Read from stdin, write to stdout
  cat input.xml | python xml_cleaner.py - -o -
        """
    )

    parser.add_argument('input',
                        help='Input XML file (use "-" for stdin)')
    parser.add_argument('-o', '--output',
                        help='Output XML file (default: <input>_cleaned.xml, use "-" for stdout)')

    args = parser.parse_args()

    # Handle stdin input
    if args.input == '-':
        xml_content = sys.stdin.read()
        cleaned = clean_xml_from_string(xml_content)
        if cleaned:
            if args.output == '-' or args.output is None:
                print(cleaned)
            else:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                print(f"✓ Successfully cleaned XML and saved to {args.output}", file=sys.stderr)
        else:
            sys.exit(1)
        return

    # Handle file input
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"✗ Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    # Determine output file path
    if args.output:
        if args.output == '-':
            # Write to stdout
            tree = ET.parse(input_path)
            root = tree.getroot()
            remove_company_sections(root)
            remove_empty_elements(root)
            print(ET.tostring(root, encoding='unicode'))
            return
        else:
            output_path = Path(args.output)
    else:
        # Default output filename
        output_path = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"

    # Clean the XML file
    success = clean_xml(input_path, output_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
