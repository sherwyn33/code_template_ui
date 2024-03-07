import os
google_api_key = 'AIzaSyCl89hbjXSumRMUnxXWFBvW1_PU73-r5zU'
code_base = os.path.normpath("C:/Users/Sherwyn/IdeaProjects/untitled")
language = 'java'  # or 'java', 'csharp', 'typescript'
config = {
    'projects': [
        {
            "id": "proj1",
            'path': os.path.normpath('C:/Users/Sherwyn/Downloads/spring-petclinic-rest-master'),
            'language': 'java',
            'relative_root': os.path.normpath('src/main/java')
        },
        {
            "id": "proj2",
            'path': os.path.normpath('C:/Users/Sherwyn/IdeaProjects/untitled'),
            'language': 'typescript',
            'relative_root': os.path.normpath('ui')
        }
        # ... potentially more projects
    ],
    "links": [
        {
            "source": {
                "project": "proj1",
                "paths": [""]  # Optional. If not provided, it means the entire project.
            },
            "target": {
                "project": "proj2",
                "paths": [""]  # Optional.
            },
            "metadata": {  # Optional field to provide more context.
                "description": "Reason why these folders or projects are linked",
                "confidence": "high"  # Or could be a numeric value.
            }
        },
    # ... more links
    ]
}
