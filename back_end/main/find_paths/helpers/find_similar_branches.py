import os
import re
from os.path import splitext, basename
from difflib import SequenceMatcher

from back_end.main.find_paths.helpers.FileNode import FileNode


def jaccard_similarity(s1, s2):
    """Compute Jaccard Similarity between two strings."""
    set1, set2 = set(s1), set(s2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union


def levenshtein_distance_ratio(s1, s2):
    """Compute Levenshtein distance ratio between two strings."""
    return SequenceMatcher(None, s1, s2).ratio()


def path_depth(file_path):
    """Get depth of a file path by counting path separators."""
    return file_path.count('\\') + file_path.count('/')


def compute_similarity(branch1, branch2):
    """Compute a similarity score between two branches."""

    # Compare length
    if len(branch1) != len(branch2):
        return 0  # The branches are not similar based on length

    score = 0
    max_score = 0
    for file1, file2 in zip(branch1, branch2):
        max_score += get_total_score()
        score += calculate_score(file1, file2)

    return score / max_score


def find_similar_branches(branches):
    """Find similar branches among a list of branches."""
    similar_pairs = []
    for i in range(len(branches)):
        if len(branches[i]) <= 1:
            continue
        for j in range(i + 1, len(branches)):
            if len(branches[j]) <= 1:
                continue
            if compute_similarity(branches[i], branches[j]) >= 0.75:  # Threshold can be adjusted
                similar_pairs.append((branches[i], branches[j]))
    return similar_pairs


def print_similar_pairs(branches):
    """Print similar branches among a list of branches."""
    similar_pairs = find_similar_branches(branches)

    if not similar_pairs:
        print("No similar branch pairs found.")
        return

    print(f"Found {len(similar_pairs)} similar branch pairs:")
    for index, (branch1, branch2) in enumerate(similar_pairs, 1):
        print(f"\nPair {index}:")
        print("Branch 1:")
        for branch_set in branch1:
            print(f"  - {branch_set.file_path}")

        print("\nBranch 2:")
        for branch_set in branch2:
            print(f"  - {branch_set.file_path}")
        print('-' * 40)  # separator

# Example usage:
# branches = [...]
# print_similar_pairs(branches)

def print_similar_clusters(similar_clusters):
    for index, cluster in enumerate(similar_clusters, 1):
        print(f"Cluster {index}:")
        for node in cluster:
            print(f"Node from Cluster {index}:", node.file_path)
            print("Connected to:")
            for connected_node in node.connected_files:
                print("\t", connected_node.file_path)
            print()  # Separate nodes within the same cluster
        print('-' * 80)  # separator between clusters



def find_similar_nodes(relationship_tree) -> list[list[FileNode]]:
    """Find similar nodes among the relationship_tree."""
    similar_dict = {}  # Stores nodes as keys and similar nodes as values (in a set)
    node_keys = list(relationship_tree.keys())

    # Step 1: Populate the similar_dict
    for i in range(len(node_keys)):
        node1 = relationship_tree[node_keys[i]]
        if len(node1.connected_files) <= 1:
            continue
        for j in range(i + 1, len(node_keys)):
            node2 = relationship_tree[node_keys[j]]
            if len(node2.connected_files) <= 1:
                continue
            if compute_similarity_tree(node1, node2) >= 0.75:  # Threshold can be adjusted
                similar_dict.setdefault(node1, set()).add(node2)
                similar_dict.setdefault(node2, set()).add(node1)

    # Step 2: Identify common nodes between pairs
    result = []
    visited = set()  # Keep track of nodes that are already included in the result

    for node, similars in similar_dict.items():
        if node in visited:
            continue
        cluster = [node] + list(similars)
        result.append(cluster)  # append the cluster as a list without converting to tuple
        visited.update(cluster)

    return result


def compute_similarity_tree(node1, node2):
    """Compute a similarity score between two nodes and their connections."""

    # Get the connected nodes
    connected_files1 = node1.connected_files
    connected_files2 = node2.connected_files

    # Compare length of connections
    if len(connected_files1) != len(connected_files2):
        return 0  # The branches are not similar based on length

    score = 0
    max_score = 0
    for file1, file2 in zip(connected_files1, connected_files2):
        max_score += get_total_score()
        score += calculate_score(file1, file2)

    return score / max_score


def calculate_score(file1, file2):
    score = 0
    # File Extension
    file_path1 = file1.file_path
    file_path2 = file2.file_path

    score += ext_match(file_path1, file_path2)

    # Depth of path
    score += depth_match(file_path1, file_path2)

    # Short name similarity using Jaccard Similarity
    score += name_match(file_path1, file_path2)

    return score


def ext_match(file_path1, file_path2):
    _, ext1 = splitext(file_path1)
    _, ext2 = splitext(file_path2)
    if ext1 == ext2:
        return 3
    else:
        return -100


def depth_match(file_path1, file_path2):
    # Remove the filename and get only the directories
    dirs1 = os.path.dirname(file_path1).split(os.path.sep)
    dirs2 = os.path.dirname(file_path2).split(os.path.sep)

    # If either path does not have a penultimate directory, return 0
    if len(dirs1) < 1 or len(dirs2) < 1:
        return 0

    # Compare the penultimate directories
    if dirs1[-1].lower() == dirs2[-1].lower():
        return 5

    # If they don't match exactly, consider depth difference
    depth_diff = abs(len(dirs1) - len(dirs2))
    return max(2 - depth_diff, 0)


def name_match(file_path1, file_path2):
    short_name1, short_name2 = basename(file_path1), basename(file_path2)
    token1 = get_last_token_by_casing(short_name1)
    token2 = get_last_token_by_casing(short_name2)
    return 3 if token1 == token2 else 0

    # Alternatively, you can use Levenshtein distance ratio for short name similarity
    # if levenshtein_distance_ratio(short_name1, short_name2) > 0.7:  # Threshold can be adjusted
    #     score += 1


def split_by_casing(word):
    # Replace underscore or hyphen with a space to ensure splitting on snake_case or kebab-case
    word_with_spaces = re.sub(r'[_\-]', ' ', word)
    # Split the word by spaces or casing changes
    return re.findall('[a-z]+|[A-Z][a-z]*', word_with_spaces)


def get_last_token_by_casing(word):
    tokens = split_by_casing(word)
    return tokens[-2] if tokens else ""


def get_total_score():
    return 11
