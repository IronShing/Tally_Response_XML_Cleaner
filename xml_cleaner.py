#!/usr/bin/env python3
"""
Tally XML Cleaner
Removes empty tags and unwanted sections from Tally XML files.
"""

import xml.etree.ElementTree as ET
import argparse
import sys
import re
from pathlib import Path


def clean_invalid_xml_chars(xml_content):
    """
    Remove invalid XML character references that cause parsing errors.
    Tally sometimes exports invalid control characters like &#4;

    Valid XML characters are:
    - #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]

    This function removes invalid numeric character references.
    """
    def is_valid_xml_char(char_code):
        """Check if a character code is valid in XML"""
        return (
            char_code == 0x09 or
            char_code == 0x0A or
            char_code == 0x0D or
            (0x20 <= char_code <= 0xD7FF) or
            (0xE000 <= char_code <= 0xFFFD) or
            (0x10000 <= char_code <= 0x10FFFF)
        )

    def replace_invalid_char(match):
        """Replace invalid character references with empty string"""
        char_ref = match.group(1)
        try:
            # Handle both decimal (&#4;) and hex (&#x4;) references
            if char_ref.startswith('x'):
                char_code = int(char_ref[1:], 16)
            else:
                char_code = int(char_ref)

            if is_valid_xml_char(char_code):
                return match.group(0)  # Keep valid characters
            else:
                return ''  # Remove invalid characters
        except ValueError:
            return match.group(0)  # Keep if we can't parse

    # Pattern to match character references like &#4; or &#x4;
    pattern = r'&#(x?[0-9a-fA-F]+);'
    cleaned = re.sub(pattern, replace_invalid_char, xml_content)

    return cleaned


def remove_empty_elements(element):
    """
    Recursively remove empty elements from the XML tree.
    An element is considered empty if it has no children and its text is:
    - None or whitespace
    - "0" (zero)
    - "No" (boolean false)
    - "-1" (default/null value)
    - "Not Applicable" (placeholder value)
    Also removes empty LIST elements and elements with only TYPE attributes.
    """
    # Process children first (bottom-up approach)
    for child in list(element):
        remove_empty_elements(child)

    # Remove empty children
    for child in list(element):
        # Check if element is empty (no children and no meaningful text)
        if len(child) == 0:
            text = child.text
            should_remove = False

            if text is None:
                should_remove = True
            else:
                text_stripped = text.strip()
                # Remove if empty, zero, "No", "-1", or "Not Applicable"
                if text_stripped in ("", "0", "No", "-1", "Not Applicable"):
                    should_remove = True

            # Remove if empty AND (no attributes OR only TYPE attribute OR is a .LIST element)
            if should_remove:
                # Check if only has TYPE attribute
                has_only_type_attr = (
                    len(child.attrib) == 1 and 'TYPE' in child.attrib
                )

                if len(child.attrib) == 0 or has_only_type_attr or child.tag.endswith('.LIST'):
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
        # Read the XML file content
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        # Clean invalid XML character references
        xml_content = clean_invalid_xml_chars(xml_content)

        # Parse the cleaned XML
        root = ET.fromstring(xml_content)

        # Remove company sections
        remove_company_sections(root)

        # Remove empty elements
        remove_empty_elements(root)

        # Write the cleaned XML to output file
        tree = ET.ElementTree(root)
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
        # Clean invalid XML character references
        xml_string = clean_invalid_xml_chars(xml_string)

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
            with open(input_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            xml_content = clean_invalid_xml_chars(xml_content)
            root = ET.fromstring(xml_content)
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
