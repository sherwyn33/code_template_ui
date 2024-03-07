import re
import statistics
from difflib import SequenceMatcher


def group_segments(all_segments, all_left_ends, word_list, key_word_mapping):
    groups = []
    j = 0
    word_list.insert(0, '\n')
    for segments in all_segments:
        left_ends = all_left_ends[j]
        index = word_list[max(0, left_ends[0] - 100): left_ends[0] + 2][::-1].index('\n')
        segment_start, keywords = replace_keywords(segments[0], key_word_mapping)
        current_group = [{'segment': segment_start, 'start_pos': (index + 1), 'group_index': j, 'array_index': 0, 'keywords': keywords}]
        average_len = statistics.mean(len(sublist) for sublist in segments)
        len_segments = len(segments)
        for i in range(1, len_segments):
            is_similar, start_pos, keywords = find_similar(segments[i], current_group[0], word_list, left_ends[i], average_len, key_word_mapping)
            if is_similar:
                current_group.append({'segment': segments[i], 'start_pos': start_pos,  'group_index': j, 'array_index': i, 'keywords': keywords})
            else:
                groups.append(current_group)
                if i != len_segments:
                    average_len = statistics.mean(len(sublist) for sublist in segments[i:])
                current_group = [{'segment': segments[i], 'start_pos': start_pos,  'group_index': j, 'array_index': i, 'keywords': keywords}]

        groups.append(current_group)
        j = j + 1

    return groups


def find_similar(seg1, current_group, word_list: list(), seg1_start, average_len, key_word_mapping):
    seg2 = current_group['segment']
    seg1, keywords_1 = replace_keywords(seg1, key_word_mapping)
    seg2, keywords_2 = replace_keywords(seg2, key_word_mapping)
    seg1_non_numeric = [re.sub(r'\d+', ' ', word) for word in seg1]
    seg2_non_numeric = [re.sub(r'\d+', ' ', word) for word in seg2]

    if current_group['keywords'] == [] or keywords_1 == []:
        index = word_list[max(0, seg1_start - 100): seg1_start + 2][::-1].index('\n')
        return False, index + 1, keywords_1

    matcher = SequenceMatcher(None, seg1_non_numeric, seg2_non_numeric)
    match = matcher.find_longest_match()
    # similarity_ratio = matcher.ratio()

    if average_len <= 3:
        min_ratio = 1
    elif average_len <= 20:
        min_ratio = 3
    else:
        min_ratio = 4

    if match.size >= min_ratio:  # Adjust the threshold as needed
        index = word_list[max(0, seg1_start - 100): seg1_start + 2][::-1].index('\n')
        # seg2_start = word_list.index(seg2[0])
        # seg2_line_start = word_list.rindex('\n', 0, seg2_start) if seg2_start != 0 else 0
        return True, index + 1, keywords_1
    else:
        if seg1_non_numeric is not seg2_non_numeric:
            index = word_list[max(0, seg1_start - 100): seg1_start + 2][::-1].index('\n')
            return False, index + 1, keywords_1


def replace_keywords(word_array, key_word_mapping):
    keywords = []
    for i in range(len(word_array)):
        word = word_array[i].lower()
        if word in key_word_mapping:
            word_array[i] = str(key_word_mapping[word])
            keywords.append(word)
    return word_array, keywords


def print_groups(groups):
    for i, group in enumerate(groups):
        print(f"Group {i+1}:")
        for seg_info in group:
            print(f"Index: {seg_info['array_index']}, Start position: {seg_info['start_pos']}, Segment: {' '.join(seg_info['segment'])}, Keywords: {seg_info['keywords']}")
        print()
