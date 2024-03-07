import re


def extract_fields_from_pattern(file_path, regex_patterns):
    """
    Extract fields from a file based on provided patterns.

    Args:
    - file_path (str): Path to the file.
    - patterns (list): List of patterns with {field} placeholder.

    Returns:
    - set: Set of fields extracted from the file.
    """
    fields = set()

    # Convert patterns to regex patterns
    with open(file_path, 'r') as f:
        content = f.read()

        for regex in regex_patterns:
            matches = re.findall(regex, content)
            fields.update(matches)

    return fields

# Test
file_path = "path_to_your_file.java"
patterns = ["private {field};", "public {field} ", "protected {field}["]
print(extract_fields_from_pattern(file_path, patterns))
