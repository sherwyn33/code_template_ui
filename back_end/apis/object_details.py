from copy import deepcopy

from flask import jsonify, request
from flask_restx import Namespace, Resource

from ..main.create_string_maker.create_template_string import create_template_string
from ..main.find_keywords.get_field_names import get_object_detail_from_similar_nodes
from ..main.find_paths.find_similar_paths_main import get_similar_pairs

object_details_namespace = Namespace('object_details', description='Index related operations')


# Endpoint for root route
@object_details_namespace.route('/')
class Index(Resource):
    def get(self):
        similar_nodes = get_similar_pairs()
        object_details = get_object_detail_from_similar_nodes(similar_nodes)
        # Convert similar_pairs into a format for the frontend
        table_data = []
        table_index = 1
        linked_id = 0
        for pair in similar_nodes:
            linked_id += 1
            for node in pair:
                details = object_details.get(node.file_path, [])
                table_data.append({
                    'id': table_index,
                    'linkedId': linked_id,
                    'file': node.toDict(),
                    'details': details
                })
                table_index += 1
        return table_data


# Endpoint for file_content
@object_details_namespace.route('/file_content')
class FileContent(Resource):
    def get(self):
        file_path = request.args.get('file_path')
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return jsonify({'content': content})
        except Exception as e:
            return jsonify({'error': str(e)})



@object_details_namespace.route('/template', methods=['POST'])
class Template(Resource):
    def post(self):
        # Get the JSON data from the request and validate it
        table_data = request.json.get('table_data', [])
        if not isinstance(table_data, list):
            return jsonify({"error": "table_data must be a list"}), 400

        # Initial lists for keyword_mappings and titles
        keyword_mappings = [dict(inner_array['details']) for inner_array in table_data if inner_array]
        titles = []

        for mapping in keyword_mappings:
            keys_to_remove = [key for key, value in mapping.items() if value == 0]
            titles.append(keys_to_remove)
            for key in keys_to_remove:
                del mapping[key]

        keyword_mappings_copy = deepcopy(keyword_mappings)

        # Extract all the main file paths from table_data
        all_main_file_paths = [entry['file']['file_path'] for entry in table_data]

        # Call create_template_string for all main file paths collectively
        main_file_path_output = create_template_string(all_main_file_paths, keyword_mappings_copy, titles)

        # Data structure to store outputs
        outputs = {
            'all_main_file_paths_output': main_file_path_output,
            'individual_outputs': []
        }
        individual_outputs = []

        # Loop through the indices from 0 to len(table_data) - 1
        for i in range(len(table_data)):
            # Collect all file_paths for the current index i
            linked_connected_file_paths = [entry['file']['connected_files'][i]["file_path"] for entry in table_data if
                                           i < len(entry['file']['connected_files'])]
            keyword_mappings_copy = deepcopy(keyword_mappings)
            result = create_template_string(linked_connected_file_paths, keyword_mappings_copy, titles)
            individual_outputs.append(result)

        outputs['individual_outputs'] = individual_outputs
        return jsonify({'templates': outputs})



