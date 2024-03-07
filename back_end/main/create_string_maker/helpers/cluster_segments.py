import re
from collections import Counter
from difflib import SequenceMatcher



def cluster_segments(list_of_segment_lists, keyword_mappings: dict, titles: []):
    most_common_keyword_type = Counter(keyword_mappings.values()).most_common(1)[0]
    clusters = {}
    cluster_list = []
    cluster_id = 0
    for segment_list in list_of_segment_lists:
        cluster_id += 1
        if len(segment_list) == 1 and segment_list[0]['keywords'] == []:
            clusters = {}
            cluster_list.append({'id': cluster_id, 0: [segment_list[0]], 'unique_keywords': []})
            continue
        elif len(segment_list) == 0:
            clusters = {}
            continue
        else:
            keywords = {keyword for entry in segment_list for keyword in entry['keywords']}
            title_words = keywords & set(titles)
            diff_words = keywords - set(keyword_mappings.keys()) - title_words
            unique_keywords = keywords - title_words - diff_words
        if len(segment_list) == 1:
            clusters = {'id': cluster_id, 'first': [], 'middle': [segment_list[0]['segment']], 'last': [],
                        'unique_keywords': unique_keywords, 'title_words': title_words, 'diff_words': diff_words,
                        'left_end': [], 'right_end': [],
                        'regex_replace_map': []}
            keyword_type = frozenset(keyword_mappings[key] for key in segment_list[0]['keywords'] if key in keyword_mappings)
            clusters[keyword_type] = segment_list[0]
            cluster_list.append(clusters)
            clusters = {}
            continue
        for i, segment in enumerate(segment_list):
            keyword_type = frozenset(keyword_mappings[key] for key in segment['keywords'] if key in keyword_mappings)
            position = 'first' if i == 0 else 'last' if i == len(segment_list) - 1 else 'middle'

            if 'first' not in clusters:
                clusters = {'id': cluster_id, 'first': [], 'middle': [], 'last': [], 'left_end': [], 'right_end': [],
                            'left_end_pos': None, 'right_end_pos': None, 'unique_keywords': unique_keywords,
                            'title_words': title_words, 'diff_words': diff_words}

            if keyword_type not in clusters and position == 'middle':
                clusters[keyword_type] = segment
                if most_common_keyword_type[0] in keyword_type:
                    segment_copy = segment.copy()
                    segment_copy['segment'] = ['10000' if x == str(most_common_keyword_type[0]) else x for x in segment_copy['segment']]
                    clusters[10000] = segment_copy

            if position == 'middle':
                # Calculate average start position of current cluster
                max_start_position = max([seg['start_pos'] for seg in segment_list])
                min_start_position = min([seg['start_pos'] for seg in segment_list])
                avg_start_position = sum([seg['start_pos'] for seg in segment_list]) / len(segment_list)


                # Determine position based on start position
                if avg_start_position == max_start_position or max_start_position == min_start_position:
                    pos_based_on_start = 'middle_end'
                else:
                    pos_based_on_start = 'right_end' if segment['start_pos'] == max_start_position else 'left_end' if segment[
                                                                                                                      'start_pos'] == min_start_position else 'middle_end'

                if pos_based_on_start == 'middle_end':
                    clusters[position].append(segment)
                else:
                    clusters[pos_based_on_start].append(segment)
                    clusters[pos_based_on_start + '_pos'] = segment['start_pos']

            else:
                clusters[position].append(segment)

            # Perform difference calculation for right_end and left_end groups against non right_end/left_end group
        differences = {}
        pos_based_on_start = ['right_end', 'middle', 'left_end']
        non_end_pos = ['first', 'middle', 'last']

        differences = {}

        if not clusters['middle'] and (clusters['right_end'] or clusters['left_end']):
            if len(clusters['right_end']) >= len(clusters['left_end']):
                clusters['middle'] = clusters['right_end']
            else:
                clusters['middle'] = clusters['left_end']

        # Compare pos_based_on_start with 'middle_end'
        for pos in pos_based_on_start:
            if pos != 'middle' and clusters[pos] and \
                    clusters['middle']:
                differences[f'{pos}_vs_middle'] = get_regex_replacement(
                    clusters[pos][-1]['segment'],
                    clusters['middle'][-1]['segment'], pos == 'right_end'
                )

        # Compare non_end_pos with 'middle'
        for pos in non_end_pos:
            if pos != 'middle' and clusters[pos] and clusters['middle']:
                differences[f'{pos}_vs_middle'] = get_regex_replacement(
                    clusters[pos][-1]['segment'],
                    clusters['middle'][-1]['segment'], pos == 'last'
                )

        # Now differences will contain tuples of (pattern, replacement)
        # So, 'regex_replace_map' can be directly assigned to 'differences'

        clusters['regex_replace_map'] = differences
        cluster_list.append(clusters)
        clusters = {}
    return cluster_list


def get_regex_replacement(target, middle, rhs: bool):
    middle = ' '.join([re.sub(r'\d', '0', word) for word in middle])
    target = ' '.join([re.sub(r'\d', '0', word) for word in target])

    if rhs:  # If it's RHS comparison, reverse the strings
        middle = middle[::-1]
        target = target[::-1]

    matcher = SequenceMatcher(None, middle, target)
    replacements = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            if i1 != 0 and j1 != 0:
                continue
            pattern = (middle[i1:i2])
            replacement = (target[j1:j2])
        elif tag == 'delete':
            pattern = (middle[i1:i2])
            replacement = ''
        elif tag == 'insert':
            pattern = '^' if i1 == 0 else f'(?<={(middle[i1-1:i1])})'
            replacement = (target[j1:j2])
        else:
            continue
        # if rhs:
        #     pattern = pattern[::-1]
        #     replacement = replacement[::-1]
        replacement = replacement.replace('\n', '\\n').replace('\"','\\"')
        pattern = pattern.replace('\n', '\\n').replace('\"','\\"')
        replacements.append((pattern, (replacement)))
    if rhs:
        '' in replacements

    return replacements
