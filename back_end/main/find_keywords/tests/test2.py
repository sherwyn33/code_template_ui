import os
import re


SPECIAL_KEYWORDS = {
    'java': ['import ', '//', '/*', '*/'],
    'cs': ['using ', '//', '/*', '*/'],
    'py': ['import ', '#'],
    'ts': ['import ', '//', '/*', '*/'],
}


def filter_content(content, lang):
    """Filter out lines that contain special keywords."""
    return '\n'.join([line for line in content.split('\n') if
                      not any(keyword in line for keyword in SPECIAL_KEYWORDS.get(lang, []))])


def unique_token_percentage(file_path, lang):
    """Extract tokens from a given file based on its language."""
    token_patterns = {
        'java': r'\b\w+\b',
        'cs': r'\b\w+\b',
        'py': r'\b\w+\b',
        'ts': r'\b\w+\b',
    }

    pattern = token_patterns.get(lang)
    tokens = set()

    if not pattern:
        return tokens

    with open(file_path, 'r') as f:
        content = filter_content(f.read(), lang)
        tokens = (re.findall(pattern, content))
    return len(set(tokens))/len(tokens)


def determine_entity_class(node):
    """Determine which file in the node's connected files is the entity class."""
    _, ext = os.path.splitext(node.file_path)
    lang = ext[1:]

    file_token_counts = {}

    for file_node in node.connected_files:
        score = unique_token_percentage(file_node.file_path, lang)
        file_token_counts[file_node.file_path] = score

    # The file with the most unique tokens is likely the entity class
    entity_class_file = max(file_token_counts, key=file_token_counts.get)

    return entity_class_file


def extract_fields_from_entity_class(file_path, lang):
    """Extract fields from the determined entity class."""
    field_patterns = {
        'java': r'(private|protected|public)\s+\w+\s+(\w+);',
        'cs': r'(private|protected|public)\s+\w+\s+(\w+);',
        'py': r'self\.(\w+)',
        'ts': r'(private|protected|public)\s+(\w+):',
    }

    pattern = field_patterns.get(lang)
    fields = set()

    if not pattern:
        return fields

    with open(file_path, 'r') as f:
        content = f.read()
        matches = re.findall(pattern, content)
        fields = {match[1] for match in matches}

    return fields
