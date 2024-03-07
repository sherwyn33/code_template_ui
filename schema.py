import re


def get_type_mapping():
    return {
        10001: "int",
        10002: "string",
        10003: "decimal",
        10004: "boolean",
        10005: "float",
        10006: "char",
        10007: "datetime",
        10008: "list",
        10009: "dictionary",
        10010: "long",
        10011: "short",
        10012: "byte",
        10013: "object",
        10014: "date",
    }

def get_inverted_type_mapping():
    type_mapping = get_type_mapping()
    return {v: k for k, v in type_mapping.items()}

def get_java_type_mapping():
    inverted_mapping = get_inverted_type_mapping()
    return {
        "int": inverted_mapping["int"],
        "String": inverted_mapping["string"],
        "double": inverted_mapping["decimal"],
        "boolean": inverted_mapping["boolean"],
        "float": inverted_mapping["float"],
        "char": inverted_mapping["char"],
        "long": inverted_mapping["long"],
        "short": inverted_mapping["short"],
        "byte": inverted_mapping["byte"],
        "LocalDate": inverted_mapping["date"],
        "LocalDateTime": inverted_mapping["datetime"],
        re.compile(r"List<\w+>"): inverted_mapping["list"],
        re.compile(r"Dictionary<K, V>"): inverted_mapping["dictionary"],
        "Object": inverted_mapping["object"],
        # ... continue for other Java types
    }

def get_cs_type_mapping():
    inverted_mapping = get_inverted_type_mapping()
    return {
        "int": inverted_mapping["int"],
        "string": inverted_mapping["string"],
        "decimal": inverted_mapping["decimal"],
        "bool": inverted_mapping["boolean"],
        "float": inverted_mapping["float"],
        "char": inverted_mapping["char"],
        "DateTime": inverted_mapping["datetime"],
        re.compile(r"List<\w+>"): inverted_mapping["list"],
        re.compile(r"Dictionary<K, V>"): inverted_mapping["dictionary"],
        "long": inverted_mapping["long"],
        "short": inverted_mapping["short"],
        "byte": inverted_mapping["byte"],
        "object": inverted_mapping["object"],
        # ... continue for other C# types
    }

def get_py_type_mapping():
    inverted_mapping = get_inverted_type_mapping()
    return {
        "int": inverted_mapping["int"],
        "str": inverted_mapping["string"],
        "float": inverted_mapping["float"],
        "bool": inverted_mapping["boolean"],
        "char": inverted_mapping["char"],
        "list": inverted_mapping["list"],
        "dict": inverted_mapping["dictionary"],
        "datetime": inverted_mapping["datetime"],
        "bytes": inverted_mapping["byte"],
        # ... continue for other Python types
    }

def get_ts_type_mapping():
    inverted_mapping = get_inverted_type_mapping()
    return {
        "number": inverted_mapping["int"],  # or perhaps float, based on TS context
        "string": inverted_mapping["string"],
        "boolean": inverted_mapping["boolean"],
        "any": inverted_mapping["object"],
        "Array<T>": inverted_mapping["list"],
        # ... continue for other TypeScript types
    }

def get_type_id(language, field_type) -> int:
    if language == "java":
        type_mapping = get_java_type_mapping()
    elif language == "cs":
        type_mapping = get_cs_type_mapping()
    elif language == "py":
        type_mapping = get_py_type_mapping()
    elif language == "ts":
        type_mapping = get_ts_type_mapping()
    else:
        return 10000  # or some default value

    # Check if the type is directly available in the mapping
    type_id = type_mapping.get(field_type)
    if type_id:
        return type_id

    # If not found, loop through the mapping to check regex patterns
    for key, value in type_mapping.items():
        if isinstance(key, re.Pattern) and key.match(field_type):
            return value
    return 10000  # If no match is found, return default value


def get_language_from_filepath(file_path):
    # Get the file extension
    extension = file_path.split('.')[-1].lower()

    # Map file extensions to languages
    extension_to_language = {
        'java': 'java',
        'cs': 'cs',
        'py': 'py',
        'ts': 'ts',
        'js': 'js',
        # You can extend this mapping with more extensions as needed
    }

    return extension_to_language.get(extension, 'unknown')
