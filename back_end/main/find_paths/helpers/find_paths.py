import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from back_end.main.find_paths.helpers.config import get_project_by_id
from back_end.main.find_paths.helpers.processTypescript import to_absolute_path
from back_end.main.find_paths.helpers.node import Node


def process_codebase(main_codebase_path, config):
    all_relationships = {}
    all_trees = {}

    for project in config["projects"]:
        project_path = os.path.join(main_codebase_path, project['path'])
        project_tree, project_relationship = find_related_files(project_path, project["language"],
                                                                project["relative_root"])

        all_trees[project["id"]] = project_tree
        all_relationships[project["id"]] = project_relationship

    # Finding linked references
    linked_references = find_linked_references(all_trees, all_relationships, config)

    # Adding linked references to the relationships
    for (file, proj_id), linked_files in linked_references.items():
        if 'linked_reference' not in all_relationships[proj_id][file]:
            all_relationships[proj_id][file]['linked_reference'] = []
        all_relationships[proj_id][file]['linked_reference'].append(linked_files)

    return all_trees, all_relationships



def build_tree_structure(dirpath, base_path, ext):
    """Recursively build the project's tree structure."""
    root_node = Node(os.path.basename(dirpath), is_directory=True)

    for entry in os.listdir(dirpath):
        entry_path = os.path.join(dirpath, entry)
        if os.path.isdir(entry_path):
            child_node = build_tree_structure(entry_path, base_path, ext)
            if child_node:  # Add directories only if they contain relevant files (matching the extension)
                root_node.add_child(child_node)
        elif entry.endswith(ext):
            child_node = Node(entry)
            root_node.add_child(child_node)

    return root_node if root_node.children else None


def find_imports(file_path, language):
    """
    Given a file path and a language, find and return all referenced files or libraries in the import/include statements.
    """
    patterns = {
        'python': r'from (\S+) import|import (\S+)',
        'java': r'import (\S+);',
        'csharp': r'using (\S+);',
        'typescript': r'import.*from [\'"](\S+)[\'"];'
    }

    pattern = patterns.get(language)
    if not pattern:
        raise ValueError(f"Unsupported language: {language}")

    with open(file_path, 'r') as f:
        content = f.read()
        imports = re.findall(pattern, content)
        return [i[0] if isinstance(i, tuple) and i[0] else i for i in imports]


def find_identifiers(file_path, language):
    """
    Given a file path and a language, find and return all potential identifiers that might refer to other files.
    """
    patterns = {
        # This is a simplistic pattern to capture potential identifiers; refine it based on actual needs
        'python': r'\b([a-zA-Z_]\w*)\b',
        'java': r'\b([a-zA-Z_]\w*)\b',
        'csharp': r'\b([a-zA-Z_]\w*)\b',
        'typescript': r'\b([a-zA-Z_]\w*)\b'
    }

    pattern = patterns.get(language)
    if not pattern:
        raise ValueError(f"Unsupported language: {language}")

    with open(file_path, 'r') as f:
        content = f.read()
        identifiers = re.findall(pattern, content)
        return set(identifiers)


def find_related_files(code_base, language, relative_root=''):
    """
    Given a code base, a language, and a relative root, returns a tree structure of the project and a dictionary where keys are filenames and values are a dictionary of 'internal' and 'external' references.
    """
    relationship = {}
    extensions = {
        'python': '.py',
        'java': '.java',
        'csharp': '.cs',
        'typescript': '.ts'
    }

    ext = extensions.get(language)
    if not ext:
        raise ValueError(f"Unsupported language: {language}")

    # Determine the actual path based on the code base and relative root
    actual_path = os.path.join(code_base, relative_root)

    # Build the project tree structure
    project_tree = build_tree_structure(actual_path, actual_path, ext)

    # Prepare a set of all filenames without extensions for reference checks
    all_paths_without_extension = dict()
    all_files_without_extension = set()
    for dirpath, _, filenames in os.walk(actual_path):
        for file in filenames:
            if file.endswith(ext):
                if language in ['typescript']:
                    files_without_extension = os.path.splitext(file)[0]
                    all_files_without_extension.add(files_without_extension)
                elif language in ['java', 'python', 'csharp']:
                    relative_path = os.path.splitext(os.path.relpath(os.path.join(dirpath, file), actual_path))[0]
                    files_without_extension = relative_path.replace(os.path.sep, '.')
                    all_files_without_extension.add(files_without_extension)
                all_paths_without_extension[files_without_extension] = os.path.join(dirpath, file)


    # Walk through all files in the code base
    for dirpath, _, filenames in os.walk(actual_path):
        for file in filenames:
            if file.endswith(ext):
                file_path = os.path.join(dirpath, file)
                referenced_files = find_imports(file_path, language)
                potential_references = find_identifiers(file_path, language)

                internal_references = set()
                external_references = set()

                for ref in referenced_files:
                    if language in ['typescript']:
                        absolute_path = to_absolute_path(file_path, ref)
                        if absolute_path in all_paths_without_extension.values():
                            internal_references.add(absolute_path)
                        else:
                            external_references.add(ref)
                    elif any(ref in word for word in all_files_without_extension):
                        internal_references.add(all_paths_without_extension[ref])
                    else:
                        external_references.add(ref)

                # Check implicit references within the same directory
                files_in_same_directory = {os.path.splitext(f)[0] for f in filenames}
                implicit_references = potential_references.intersection(files_in_same_directory) - {
                    os.path.splitext(file)[0]}

                # Validate if these references are used inside the file
                valid_references = set()
                if language not in ['typescript']:
                    with open(os.path.join(dirpath, file), 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        for ref in implicit_references:
                            # Extract just the class name (i.e., file name without .java or other extensions)
                            class_name = os.path.splitext(ref)[0]
                            if class_name in file_content:
                                # relative_ref_path = os.path.relpath(os.path.join(dirpath, ref), actual_path)
                                # dotted_path = relative_ref_path.replace(os.path.sep, '.')
                                valid_references.add(os.path.join(dirpath, ref) + ext)

                relationship[os.path.join(dirpath, file)] = {
                    'package': valid_references,
                    'internal': internal_references,
                    'external': external_references
                }

                # Store the relationships in the project_tree nodes
                nodes = [project_tree]
                while nodes:
                    current_node = nodes.pop()
                    if current_node.name == file:
                        file_path = os.path.join(dirpath, file)

                        # Ensure that relationship[file_path] is a dictionary
                        if not isinstance(relationship.get(file_path), dict):
                            relationship[file_path] = {}

                        # Make current_node.relationship point to relationship[file_path]
                        current_node.relationship = relationship[file_path]
                        break
                    nodes.extend(current_node.children)

    return project_tree, relationship


def group_related_files(relationship):
    """
    Given a relationship dictionary, group related files.
    """
    visited = set()
    groups = []

    def dfs(file, group):
        if file not in visited:
            visited.add(file)
            group.add(file)
            for related_file in relationship.get(file, set()):
                dfs(related_file, group)

    for file in relationship:
        if file not in visited:
            group = set()
            dfs(file, group)
            groups.append(group)

    return groups


from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_linked_references(main_project_tree, all_project_trees, config):
    tfidf_matrix, file_paths_index = build_tfidf_and_index(main_project_tree, config)


    linked_references = {}

    # Build a quick lookup for project paths
    # project_paths = {project["id"]: project["path"] for project in config["projects"]}

    for link in config["links"]:
        source_project = link["source"]["project"]
        source_paths = link["source"]["paths"]

        target_project = link["target"]["project"]
        target_paths = link["target"]["paths"]

        # Get trees for source and target
        source_tree = main_project_tree[source_project]
        target_tree = main_project_tree[target_project]

        for source_path in source_paths:
            for target_path in target_paths:
                # Compute similarity between files in source_path and target_path
                # If the similarity crosses a threshold, add to linked_references

                # Example (simplified and naive) logic:
                source_project_config = get_project_by_id(source_project, config)
                target_project_config = get_project_by_id(target_project, config)
                source_files = get_files_from_path(source_tree, source_path,
                                                   os.path.join(source_project_config["path"], source_project_config["relative_root"]))
                target_files = get_files_from_path(target_tree, target_path,
                                                   os.path.join(target_project_config["path"], target_project_config["relative_root"]))

                for s_file in source_files:
                    for t_file in target_files:
                        if are_files_similar(s_file, t_file, tfidf_matrix, file_paths_index):
                            linked_references.setdefault((s_file, source_project), []).append((t_file, target_project))
                            linked_references.setdefault((t_file, target_project), []).append(
                                (s_file, source_project))  # Since it's bidirectional

    return linked_references

def get_files_with_full_path(tree, prefix=""):
    """Recursively extract all files with their full paths from the tree."""
    files = []
    for key, value in tree.items():
        if isinstance(value, dict):
            # It's a directory, recurse further
            files.extend(get_files_with_full_path(value, os.path.join(prefix, key)))
        else:
            # It's a file, add to the list with its full path
            files.append(os.path.join(prefix, key))
    return files


def get_files_from_path(node, path, current_path=''):
    """
    Recursively search for all files within a given path in the project tree.
    If the path is empty, return all files under the given node.
    """
    files = []

    # If path is empty, return all files under the node
    if not path:
        return get_all_files(node, current_path)

    components = path.split("/")

    if not components:
        return files

    first, *rest = components
    for child_node in node.children:
        if child_node.name == first:
            new_current_path = os.path.join(current_path, child_node.name)
            if child_node.is_directory:
                # If there are more path components, navigate deeper based on the path
                if rest:
                    files.extend(get_files_from_path(child_node, "/".join(rest), new_current_path))
                # If there are no more path components, get all files under this directory
                else:
                    files.extend(get_all_files(child_node, new_current_path))
            elif not rest:  # It's a file and we're at the end of our path
                files.append(new_current_path)

    return files


def get_all_files(node, current_path=''):
    """
    Get all files under the given node, recursively.
    """
    files = []

    if node.is_directory:
        for child_node in node.children:
            new_current_path = os.path.join(current_path, child_node.name)
            files.extend(get_all_files(child_node, new_current_path))
    else:
        files.append(current_path)

    return files





def compute_tfidf_matrix(file_paths):
    """
    Computes the TF-IDF matrix for a set of documents.
    """
    documents = [tokenize_file_content(file_path) for file_path in file_paths]
    vectorizer = TfidfVectorizer(use_idf=True, lowercase=True, tokenizer=lambda x: x, preprocessor=lambda x: x)
    tfidf_matrix = vectorizer.fit_transform(documents)
    return tfidf_matrix

def compute_cosine_similarity(tfidf_matrix, index1, index2):
    """
    Computes the cosine similarity between two documents in the TF-IDF matrix.
    """
    return cosine_similarity(tfidf_matrix[index1], tfidf_matrix[index2])[0][0]



def are_files_similar(file1_path, file2_path, tfidf_matrix, file_paths_index, threshold=0.3):
    """
    Check if two files are considered similar based on their content.
    """
    # Use the TF-IDF matrix to compute the cosine similarity
    index1 = file_paths_index[file1_path]
    index2 = file_paths_index[file2_path]
    similarity = compute_cosine_similarity(tfidf_matrix, index1, index2)

    return similarity >= threshold


def tokenize_file_content(file_path):
    """
    Tokenize a file's content into words.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        # Remove punctuation, numbers, and split by whitespace
        tokens = re.findall(r'\b\w+\b', content)
    return set(tokens)


def collect_all_file_paths(main_project_tree, config):
    """
    Collect all file paths from the main project tree.
    """
    all_file_paths = []
    for project_id, tree in main_project_tree.items():
        project = get_project_by_id(project_id, config)
        project_root_path = os.path.join(project["path"], project["relative_root"])
        all_file_paths.extend(get_all_files_with_paths(tree, project_root_path))
    return all_file_paths


def get_all_files_with_paths(node, prefix=""):
    """
    Recursively extract all files with their full paths from the tree node.
    """
    files = []
    if node.is_directory:
        for child_node in node.children:
            files.extend(get_all_files_with_paths(child_node, os.path.join(prefix, child_node.name)))
    else:
        files.append(prefix)
    return files

def build_tfidf_and_index(main_project_tree, config):
    """
    Build the TF-IDF matrix and the file paths index.
    """
    # 1. Collect all file paths
    all_file_paths = collect_all_file_paths(main_project_tree, config)

    # 2. Compute the TF-IDF matrix
    tfidf_matrix = compute_tfidf_matrix(all_file_paths)

    # 3. Build the file paths index
    file_paths_index = {file_path: index for index, file_path in enumerate(all_file_paths)}

    return tfidf_matrix, file_paths_index
