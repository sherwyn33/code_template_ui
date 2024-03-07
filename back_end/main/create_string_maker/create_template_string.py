import textwrap
from copy import deepcopy

from back_end.main.create_string_maker.helpers.cluster_segments import cluster_segments
from back_end.main.create_string_maker.helpers.combine_clusters import combine_clusters
from back_end.main.create_string_maker.helpers.create_segments import find_segments
from back_end.main.create_string_maker.helpers.create_string import create_string
from back_end.main.create_string_maker.helpers.create_tags import create_tags, print_tags
from back_end.main.create_string_maker.helpers.diff import get_diff
from back_end.main.create_string_maker.helpers.get_object_details import paragraph, skip_words, title, title2
from back_end.main.create_string_maker.helpers.group_segments import group_segments, print_groups, replace_keywords

def read_file_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        return data
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except IOError:
        print("An error occurred while trying to read the file.")
        return None

def create_template_string(file_paths, keyword_mappings: [dict()], titles: [[]]):
    i = -1
    paragraphs = []
    for file_path in file_paths:
        i += 1
        paragraphs.append(read_file_to_string(file_path))
    if len(keyword_mappings) == 0:
        return no_keywords_found(titles, paragraphs)
    j = 0

    all_segments2, all_left_ends2, word_list2 = find_segments(paragraphs[0], titles[0], keyword_mappings[0], skip_words)

    if all_segments2 is None:
        return no_keywords_found(titles, paragraphs)
    clusters = {}
    keyword_mapping = {}
    constant_dict_all = {}

    while j < i:
        all_segments, all_left_ends, word_list = all_segments2, all_left_ends2, word_list2
        all_segments2, all_left_ends2, word_list2 = find_segments(paragraphs[j + 1], titles[j + 1], keyword_mappings[j + 1], skip_words)

        if all_segments2 is None:
            return no_keywords_found(titles, paragraphs)

        all_segments, constant_dict = get_diff(all_segments, all_segments2, titles[j], titles[j + 1],
                                               list(keyword_mappings[j].keys()))

        keyword_mapping = keyword_mappings[j] | keyword_mapping
        keyword_mappings[j] = keyword_mappings[j] | constant_dict
        constant_dict_all = constant_dict_all | constant_dict

        groups = group_segments(all_segments, all_left_ends, word_list, keyword_mappings[j])
        clusters_new = cluster_segments(groups, keyword_mappings[j], titles[j])
        if len(clusters) == 0:
            clusters = deepcopy(clusters_new)
        else:
            clusters = combine_clusters(clusters, clusters_new)
        j += 1

    tags = create_tags(clusters, keyword_mapping)


    # Call the function
    result_string = create_string(clusters, titles, constant_dict_all)
    result_string = textwrap.indent(result_string, ' ' * 2)
    result_string = 'import re\ndef create(variable_map, variable_options, title):\n' + result_string
    return result_string


def no_keywords_found(titles, paragraphs):
    paragraph_0 = paragraphs[0]
    for index, word in enumerate(titles[0]):
        if word in paragraph_0:
            replacement = f'""" + title[{index}] + """'
            paragraph_0 = paragraph_0.replace(word, replacement)
    result_string = textwrap.indent(paragraph_0, ' ' * 2)
    result_string = 'import re\ndef create(variable_map, variable_options, title):\n' + result_string
    return result_string