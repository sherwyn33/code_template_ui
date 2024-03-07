import re
import os

def tokenize(text):
    # Simple tokenization based on non-alphanumeric characters
    return set(filter(str.isalnum, text.split()))

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


def find_unique_words(file1, file2, common_words=set([])):
    # Determine the language from the file extension
    _, ext1 = os.path.splitext(file1)
    _, ext2 = os.path.splitext(file2)
    lang1 = ext1[1:]
    lang2 = ext2[1:]

    with open(file1, 'r') as f:
        content1 = filter_content(f.read(), lang1)
        tokens1 = tokenize(content1)

    with open(file2, 'r') as f:
        content2 = filter_content(f.read(), lang2)
        tokens2 = tokenize(content2)

    # Remove common tokens
    unique1 = tokens1 - tokens2 - common_words
    unique2 = tokens2 - tokens1 - common_words

    return unique1, unique2


def process_nodes(node0, node1):
    unique_keywords = tuple(set())

    for file_a, file_b in zip(node0.connected_files, node1.connected_files):
        keywords = find_unique_words(file_a.file_path, file_b.file_path)
        unique_keywords = unique_keywords.__add__(keywords)

    return unique_keywords