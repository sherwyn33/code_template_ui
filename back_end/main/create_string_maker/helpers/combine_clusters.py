def are_clusters_similar(cluster1, cluster2):
    return len(cluster1) == len(cluster2)


def combine_single_items(item1, item2):
    combined_item = {
        'id': item1['id'],  # Assuming ids are the same due to the order
        'first': item1['first'] + item2['first'],
        'middle': item1['middle'] + item2['middle'],
        'last': item1['last'] + item2['last'],
        'left_end': item1['left_end'] + item2['left_end'],
        'right_end': item1['right_end'] + item2['right_end'],
        'unique_keywords': item1['unique_keywords'] + item2['unique_keywords'],
        'title_words': item1['title_words'] + item2['title_words'],
        'diff_words': item1['diff_words'] + item2['diff_words'],
    }

    # Determine left_end_pos
    if item1.get('left_end_pos') is None:
        combined_item['left_end_pos'] = item2.get('left_end_pos')
    elif item2.get('left_end_pos') is None:
        combined_item['left_end_pos'] = item1.get('left_end_pos')
    else:
        combined_item['left_end_pos'] = min(item1['left_end_pos'], item2['left_end_pos'])

    # Determine right_end_pos
    if item1.get('right_end_pos') is None:
        combined_item['right_end_pos'] = item2.get('right_end_pos')
    elif item2.get('right_end_pos') is None:
        combined_item['right_end_pos'] = item1.get('right_end_pos')
    else:
        combined_item['right_end_pos'] = max(item1['right_end_pos'], item2['right_end_pos'])

    # Handle regex_replace_map components
    regex_components = ['first_vs_middle', 'left_end_vs_middle', 'last_vs_middle', 'right_end_vs_middle']

    if 'regex_replace_map' in item1 or 'regex_replace_map' in item2:
        combined_item['regex_replace_map'] = {}
        for component in regex_components:
            if item1.get('regex_replace_map', {}).get(component):
                combined_item['regex_replace_map'][component] = item1['regex_replace_map'][component]
            elif item2.get('regex_replace_map', {}).get(component):
                combined_item['regex_replace_map'][component] = item2['regex_replace_map'][component]
            # If neither have it, don't include the component

    return combined_item


def combine_clusters(cluster1, cluster2):
    if not are_clusters_similar(cluster1, cluster2):
        return cluster1

    combined_cluster = set()

    # Using zip to iterate over paired items from both clusters
    for item1, item2 in zip(cluster1, cluster2):
        combined_item = combine_single_items(item1, item2)
        combined_cluster.add(combined_item)

    return combined_cluster
