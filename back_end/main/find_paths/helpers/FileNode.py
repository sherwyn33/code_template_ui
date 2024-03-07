class FileNode:
    def __init__(self, file_path):
        self.file_path = file_path
        self.connected_files = set()  # Nodes connected to this node
        self.parent_files = set()  # Nodes connected to this node
        self.content: str

    def connect(self, other_node):
        if other_node not in self.connected_files:
            self.connected_files.add(other_node)
        if self not in other_node.parent_files:
            other_node.parent_files.add(self)

    def toDict(self, visited=None):
        if visited is None:
            visited = set()

        node_id = id(self)
        if node_id in visited:
            # Return a reduced representation to avoid cycles/infinite recursion
            return {"file_path": self.file_path}

        visited.add(node_id)

        return {
            "file_path": self.file_path,
            "connected_files": [node.toDict(visited) for node in self.connected_files],
            "parent_files": [node.toDict(visited) for node in self.parent_files]
        }


def create_relationship_tree(all_relationships):
    file_nodes = {}
    for proj_id, relationships in all_relationships.items():
        for file, relationship_data in relationships.items():
            # Ensure that each file has a FileNode
            if file not in file_nodes:
                file_nodes[file] = FileNode(file)

            # Handle internal relationships
            for internal_file in relationship_data.get('internal', []):
                if internal_file not in file_nodes:
                    file_nodes[internal_file] = FileNode(internal_file)
                file_nodes[file].connect(file_nodes[internal_file])

            # Handle package relationships
            for package_file in relationship_data.get('package', []):
                if package_file not in file_nodes:
                    file_nodes[package_file] = FileNode(package_file)
                file_nodes[file].connect(file_nodes[package_file])

            # Handle linked relationships
            for linked_files in relationship_data.get('linked_reference', []):
                for linked_file, linked_proj_id in linked_files:
                    if linked_file not in file_nodes:
                        file_nodes[linked_file] = FileNode(linked_file)
                    file_nodes[file].connect(file_nodes[linked_file])

    return file_nodes


def get_connected_component(node, visited):
    component = set()
    stack = [node]

    while stack:
        current_node = stack.pop()
        if current_node not in visited:
            visited.add(current_node)
            component.add(current_node)
            stack.extend([neighbor for neighbor in current_node.connected_files if neighbor not in visited])

    return component


def find_connected_components(all_nodes):
    visited = set()
    components = []

    for node in all_nodes:
        if node not in visited:
            component = get_connected_component(node, visited)
            components.append(component)

    return components


def find_unique_connected_components(all_nodes):
    visited = set()
    components = []

    for node in all_nodes:
        if node not in visited:
            component = get_connected_component(node, visited)
            if component not in components:  # Ensure uniqueness
                components.append(component)

    return components