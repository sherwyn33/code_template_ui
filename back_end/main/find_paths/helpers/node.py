class Node:
    def __init__(self, name, is_directory=False):
        self.name = name
        self.is_directory = is_directory
        self.children = []  # List of Node objects.
        self.relationship = None  # Will store the internal and external references for files.

    def add_child(self, child):
        self.children.append(child)
