def print_tree(node, indent=0):
    """
    Print the tree structure in a hierarchical format.
    """
    padding = ' ' * indent
    print(f"{padding}- {node.name}")

    # Print relationships for files
    if not node.is_directory and node.relationship:
        print(f"{padding}  Internal: {', '.join(node.relationship['internal'])}")
        print(f"{padding}  External: {', '.join(node.relationship['external'])}")

    for child in node.children:
        print_tree(child, indent + 2)
