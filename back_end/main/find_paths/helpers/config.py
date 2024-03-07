def get_project_by_id(project_id, config):
    """
    Retrieve the project path given its ID from the config.
    """
    for project in config['projects']:
        if project['id'] == project_id:
            return project
    return None  # Return None if no project is found with the given ID
