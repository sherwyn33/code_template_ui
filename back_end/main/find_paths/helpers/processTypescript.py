import os


def to_absolute_path(current_file_path, import_path):
    # Get the directory of the current file
    dir_path = os.path.dirname(current_file_path)

    # Join the directory path with the import path to create a full path
    full_path = os.path.join(dir_path, import_path)

    # Normalize the path (handle "..", "." etc.)
    normalized_path = os.path.normpath(full_path)

    # If the path doesn't have an extension, assume it's a ".ts" file
    if not os.path.splitext(normalized_path)[1]:
        normalized_path += ".ts"

    return normalized_path


# Test
current_file = "C:\\Users\\Sherwyn\\IdeaProjects\\untitled\\ui\\Employee\\employee.component.ts"
import_ref = "./employee"
print(to_absolute_path(current_file, import_ref))
