import os


from back_end.main.find_paths.helpers.FileNode import create_relationship_tree, find_unique_connected_components
from back_end.main.find_paths.helpers.find_paths import process_codebase
from back_end.main.find_paths.helpers.find_similar_branches import find_similar_nodes, print_similar_clusters
from config import code_base, config


def get_similar_pairs():
    all_trees, all_relationships = process_codebase(code_base, config)

    # Example:

    relationship_tree = create_relationship_tree(all_relationships)

    # branches = find_unique_connected_components(relationship_tree.values())

    # for idx, branch in enumerate(branches):
    #     print(f"Branch {idx + 1}: {[node.file_path for node in branch]}")

    # To view the components:
    # for component in relationship_tree:
    #     print(f"Component {component}: {[node.file_path for node in relationship_tree[component].connected_files]}")

    # similar_pairs = find_similar_branches(branches)
    similar_pairs = find_similar_nodes(relationship_tree)
    # similar_pairs = print_similar_pairs(branches)
    # similar_pairs = print_similar_clusters(similar_pairs)

    # result = process_nodes(similar_pairs[1][0], similar_pairs[1][1])
    # result = determine_entity_class(similar_pairs[0][1])
    # print(result)

    return similar_pairs