
def print_tags(clusters, all_keywords):
    final_tags = create_tags(clusters, all_keywords)
    print("Final Tags for each keyword:")
    for keyword, tag in final_tags.items():
        print(f"{keyword}: {tag}")


def create_tags(clusters, all_keywords):
    keyword_presence = create_presence_vector(clusters, all_keywords)
    default_presence = max(keyword_presence.values(),
                           key=lambda s: len([k for k, v in keyword_presence.items() if v == s]))
    difference_info = build_difference_information(keyword_presence, default_presence)
    final_tags = assign_tags(difference_info)
    update_clusters(clusters, final_tags, difference_info, default_tag=0)
    return final_tags


def create_presence_vector(clusters, all_keywords):
    keyword_presence = {keyword: set() for keyword in all_keywords}
    for cluster in clusters:
        cluster_id = cluster['id']
        for keyword in cluster['unique_keywords']:
            if keyword in keyword_presence:
                keyword_presence[keyword].add(cluster_id)
    return keyword_presence


def build_difference_information(keyword_presence, default_presence):
    difference_info = {}
    for keyword, presence_set in keyword_presence.items():
        if presence_set != default_presence:
            extra_present = presence_set - default_presence
            extra_missing = default_presence - presence_set
            difference_info[keyword] = {'extra_present': extra_present, 'extra_missing': extra_missing}
        else:
            difference_info[keyword] = 0
    return difference_info


def assign_tags(difference_info):
    frequency_counter = {}
    for info in difference_info.values():
        if info != 0:
            key = (frozenset(info['extra_present']), frozenset(info['extra_missing']))
            frequency_counter[key] = frequency_counter.get(key, 0) + 1

    tag_numbering = {}
    for i, item in enumerate(sorted(frequency_counter.keys(), key=lambda x: -frequency_counter[x]), 1):
        tag_numbering[item] = i

    tags = {}
    for keyword, info in difference_info.items():
        if info == 0:
            tags[keyword] = 0
        else:
            key = (frozenset(info['extra_present']), frozenset(info['extra_missing']))
            tags[keyword] = tag_numbering[key]

    return tags


def update_clusters(clusters, final_tags, difference_info, default_tag):
    # Adding required_tags and skip_tags fields to each cluster
    for cluster in clusters:
        cluster_id = cluster['id']
        cluster['required_tags'] = set()
        cluster['skip_tags'] = set()
        for keyword, tag in final_tags.items():
            # Check if this keyword tag is not default
            if tag != default_tag:
                tag_info = difference_info[keyword]
                if cluster_id in tag_info['extra_present']:
                    # Add to required_tags
                    cluster['required_tags'].add(tag)
                if cluster_id in tag_info['extra_missing']:
                    # Add to skip_tags
                    cluster['skip_tags'].add(tag)
