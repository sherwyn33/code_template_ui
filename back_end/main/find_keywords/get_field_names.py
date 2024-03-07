import re

from back_end.main.find_paths.find_similar_paths_main import get_similar_pairs
from schema import get_type_id, get_language_from_filepath

token_patterns = {
    'java': [
        r"(?:private|public|protected|static|final|volatile|transient)?\s*\w+\s+\w+\s*;",
        r"(?:private|public|protected|static|final|volatile|transient)?\s*\w+\[\]\s+\w+\s*;"
    ],
    'csharp': [
        r"(?:private|public|protected|static|readonly|const|internal|protected\s+internal)?\s*\w+\s+\w+\s*;",
        r"(?:private|public|protected|static|readonly|const|internal|protected\s+internal)?\s*\w+\[\]\s+\w+\s*;"
    ],
    'py': [
        r"(\w+)\s*=\s*\w+",
        r"(\w+)\s*:\s*\w+",
        r"(\w+)\s*:\s*List\[\w+\]",
        r"(\w+)\s*:\s*Dict\[\w+, \w+\]",
        r"(\w+)\s*:\s*Tuple\[\w+(?:, \w+)*\]"
    ],
    'ts': [
        r"(?:private|public|readonly|static)?\s*(\w+)\s*:\s*(\w+)(?:\s*;|\s*=)?",
        r"(?:private|public|readonly|static)?\s*(\w+)\s*:\s*\w+\[]",
        r"(?:private|public|readonly|static)?\s*(\w+)\s*:\s*{\s*\[key: \w+\]: \w+\s*}",
        r"(?:private|public|readonly|static)?\s*(\w+)\s*:\s*\[\w+(?:, \w+)*\]"
    ]
}


def extract_fields_from_pattern(file_path, language):
    fields = []
    patterns = token_patterns.get(language, [])

    with open(file_path, 'r') as f:
        content = f.read()

        if language == 'java' or language == 'csharp':
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    parts = match.split()
                    if len(parts) >= 3:
                        field_type = parts[1]
                        field_name = parts[2].replace(";", "").lower()
                        fields.append((field_name, get_type_id(language, field_type)))

        elif language == 'py':
            pattern = r'(\w+)\s*:\s*(\w+)\s*='
            matches = re.findall(pattern, content)
            for match in matches:
                field_name = match[0].replace(";", "").lower()
                field_type = match[1]
                fields.append((field_name, get_type_id(language, field_type)))

        elif language == 'ts':
            patterns = [r'(\w+)\s*:\s*(\w+)\s*;', r'\binterface\b\s+\w+\s*\{([\s\S]*?)\}']
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 2:
                        field_name = match[0].replace(";", "")
                        field_type = match[1]
                        fields.append((field_name, get_type_id(language, field_type)))
                    else:
                        # This is for the 'interface' pattern, which captures the entire interface body
                        # We need to process this further
                        inner_matches = re.findall(r'(\w+)\s*:\s*(\w+)', match[0])
                        for inner_match in inner_matches:
                            field_name = inner_match[0].lower()
                            field_type = inner_match[1]
                            fields.append((field_name, get_type_id(language, field_type)))

    return fields


def get_object_detail_from_similar_nodes(similar_nodes: list()):
    results = {}

    for similars in similar_nodes:
        for node1 in similars:
            language = get_language_from_filepath(node1.file_path)
            fields_node1 = extract_fields_from_pattern(node1.file_path, language)
            results[node1.file_path] = fields_node1
            extract_fields_from_connected_files(node1.connected_files, language, results, node1.file_path)

    return results


def extract_fields_from_connected_files(connected_files, language, results, file_path):

    for file_node in connected_files:
        fields = extract_fields_from_pattern(file_node.file_path, language)
        results[file_path] = results[file_path] + fields



# Sample usage:
# Assuming node1, node2, node3, and node4 are instances of the FileNode class
# language = 'java'  # Choose the appropriate language
# similar_nodes = get_similar_pairs()
# fields_results = get_object_detail_from_similar_nodes(similar_nodes)
# for file, fields in fields_results.items():
#     print(f"File: {file}")
#     for field, type_id in fields:
#         print(f"Field Name: {field}, Type ID: {type_id}")
#     print("-----------------------------")
