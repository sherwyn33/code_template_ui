import math
import re
from collections import Counter
from statistics import mode

import numpy as np
from numpy import average


def find_segments(paragraph, title_words, keyword_mappings, skip_words):
    # Split paragraph into lines, then words, treating each stopping character as a separate word
    stop_chars = ['\n']
    word_list = split_into_words_and_symbols(paragraph, stop_chars, keyword_mappings.keys(), title_words, skip_words)
    # Compute positions of keywords (case insensitive)
    keyword_positions = [i for i, word in enumerate(word_list) if word.lower() in keyword_mappings.keys()]

    if len(keyword_positions) == 0:
        return None, None, None
    # Group keyword positions
    keyword_position_groups = group_keyword_positions(keyword_positions, title_words, word_list)
    # [[66, 68, 70, 72, 74, 76, 78],
    #  [88, 195, 210, 226, 230, 236, 242, 246, 254, 258, 264, 268, 274, 278, 284, 288, 294, 298, 304], [335],
    #  [368, 370, 372, 374, 376, 378, 380], [388, 392], [408, 410, 412, 414, 416, 418], [424, 426, 428, 430, 432, 434],
    #  [448, 452, 454, 458, 460, 464, 468, 472, 474, 478, 480, 484, 492], [547, 558, 568, 581, 592, 603, 614, 625]]
    # [[66, 68, 70, 72, 74, 76, 78], [88, 236], [242, 246, 254, 258, 264, 268, 274, 278, 284, 288, 294, 298, 304], [368, 370, 372, 374, 376, 378, 380], [388, 392], [408, 410, 412, 414, 416, 418], [424, 426, 428, 430, 432, 434], [448, 452, 454, 458, 460, 464, 468, 472, 474, 478, 480, 484, 492], [547, 558, 568, 581, 592, 603, 614, 625]]
    # Initialize segments
    all_segments = []
    all_left_ends = []
    group_pos = 0
    max_group_pos = len(keyword_position_groups)
    last_right_end = 0
    # Process each group of keyword positions
    for keyword_positions in keyword_position_groups:
        i = 0
        segment_index = 0
        segments = []
        left_ends = []
        left_ends_length = []
        right_ends = []
        right_ends_length = []
        while i < len(keyword_positions):
            # If multiple occurrences of the same keyword appear sequentially, consider them as part of the same segment
            start_pos = keyword_positions[i]
            end_pos = start_pos
            while i+1 < len(keyword_positions) and (word_list[keyword_positions[i]].lower() == word_list[keyword_positions[i+1]].lower() \
                    or word_list[keyword_positions[i+1]] in title_words):
                if word_list[keyword_positions[i+1]] in title_words:
                    end_pos = keyword_positions.pop(i+1)
                else:
                    end_pos = keyword_positions[i+1]
                    i += 1
            if i != len(keyword_positions) - 1:  # Not the last keyword
                new_lines_pos = [j + keyword_positions[i] for j, x in enumerate(word_list[keyword_positions[i]: keyword_positions[i + 1]]) if x.__contains__('\n')]

                if len(new_lines_pos) > 0:
                    right_half_len = new_lines_pos[math.ceil((len(new_lines_pos) - 1) / 2)] - keyword_positions[i]
                    right_end = end_pos + right_half_len
                else:
                    right_half_len = math.ceil((keyword_positions[i + 1] - end_pos + 1) / 2)
                    right_end = end_pos + right_half_len

                # Adjust right end to the nearest stopping character
                # Check for the nearest start line
                start_line_end = right_end - 1
                try:
                    while start_line_end > end_pos and word_list[start_line_end] not in stop_chars:
                        start_line_end -= 1
                    if word_list[start_line_end] in stop_chars:
                        start_line_end += 1
                except:
                    print('test')

                while right_end < len(word_list) and word_list[right_end] not in stop_chars and right_end < (keyword_positions[i+1]):
                    right_end += 1

# //[1008, 1029, 1049, 1074, 1095, 1116, 1137, 1158]
                # If the start line is closer, adjust right_end to that instead
                if ((right_end - end_pos > end_pos - start_line_end) and start_line_end > end_pos) or (keyword_positions[i+1] == right_end and start_line_end != end_pos):
                    right_end = start_line_end

                right_end = min(len(word_list), right_end)
                right_ends.append(right_end)
                segment_index += 1
                if segment_index == 1:  # First keyword
                    segments.append(word_list[keyword_positions[0]:right_end])
                    right_ends_length.append(right_end - keyword_positions[i])
                    left_ends.append(keyword_positions[0])
                else:  # Middle keywords
                    left_end = right_ends[segment_index-2]
                    # segments[-1] += word_list[keyword_positions[i-1]:left_end]
                    segments.append(word_list[left_end:right_end])
                    left_ends.append(left_end)
                    left_ends_length.append(keyword_positions[i] - left_end)
                    right_ends_length.append(right_end - keyword_positions[i])

            i += 1

        if segment_index > 1:  # There are multiple keywords
            # Last keyword
            left_end = right_ends[-1]
            # left_ends_length.append(keyword_positions[i - 1] - left_end)
            if group_pos == max_group_pos - 1:
                limit = len(word_list)
            else:
                limit = keyword_position_groups[group_pos + 1][0]
            left_ends.append(left_end)
            right_end = min(limit, keyword_positions[-1] + mode(right_ends_length))
            # segments[-1] += word_list[keyword_positions[-1]:left_end]
            segments.append(word_list[left_end:right_end])

            # First keyword
            if group_pos == 0:
                limit = 0
            else:
                limit = last_right_end

            # index_prev_line_end = left_ends[0] - word_list[max(0, left_ends[0] - 50): left_ends[0] + 2][::-1].index('\n') + 1
            if check_mode_frequency(left_ends_length):
                left_end = max(limit, keyword_positions[0] - mode(left_ends_length))
            else:
                try:
                    index_prev_line_end = keyword_positions[0] - round(average(left_ends_length)) - word_list[max(0, keyword_positions[0] - round(average(left_ends_length)) - 50) : keyword_positions[0] - round(average(left_ends_length)) + 1][::-1].index(
                        '\n') + 1
                except:
                    index_prev_line_end = keyword_positions[0] - 1

                left_end = max(limit, min(keyword_positions[0] - round(average(left_ends_length)), index_prev_line_end))
            segments[0] = word_list[left_end:keyword_positions[0]] + segments[0]
            left_ends[0] = left_end

            if left_end > last_right_end:
                segments.insert(0, word_list[last_right_end:left_end])
                left_ends.insert(0, last_right_end)

            if (segments[0] == []):
                segments.pop(0)
                left_ends.pop(0)

            last_right_end = right_end
        else:
            min_left_end = max(0, keyword_positions[0] - 50)
            index_prev_line_end = keyword_positions[0] - min(keyword_positions[0], 50) - word_list[min_left_end: keyword_positions[0]][::-1].index('\n') + 1
            right_end = max(min(keyword_positions[0], index_prev_line_end), last_right_end + 1)
            left_ends.append(right_end)
            segments.append(word_list[last_right_end:right_end])
            index_next_line_end = word_list[keyword_positions[-1]: keyword_positions[-1] + 50].index('\n') + keyword_positions[-1]
            segments.append(word_list[right_end:index_next_line_end])
            left_ends.append(index_next_line_end)
            last_right_end = index_next_line_end

        all_segments.append(segments)
        all_left_ends.append(left_ends)
        group_pos += 1

    if len(word_list) > last_right_end:
        all_segments.append([word_list[last_right_end:len(word_list)]])
        all_left_ends.append([last_right_end])

    return all_segments, all_left_ends, word_list


def group_keyword_positions(keyword_positions, title_words, word_list):
    groups = []
    current_group = [keyword_positions[0]]
    next_distance = keyword_positions[2] - keyword_positions[1]
    prev_distance = 0
    length = len(keyword_positions)
    for i in range(1, length):
        distance = keyword_positions[i] - keyword_positions[i-1]
        words_between = word_list[keyword_positions[i-1]+1:keyword_positions[i]]
        if (0.5*np.sqrt(prev_distance + 1) <= np.sqrt(distance + 1) <= 1.5*np.sqrt(prev_distance + 1)) or word_list[keyword_positions[i]] == word_list[keyword_positions[i-1]] or \
                (len(current_group) == 1 and (0.5*np.sqrt(next_distance + 1) <= np.sqrt(distance + 1) <= 1.5*np.sqrt(next_distance + 1))):
            if any(word.lower() in title_words for word in words_between):
                title_positions_between = [j + keyword_positions[i - 1] + 1 for j, word in enumerate(words_between) if
                                           word.lower() in title_words]
                current_group = current_group + title_positions_between
                current_group.append(keyword_positions[i])
            else:
                current_group.append(keyword_positions[i])
        else:
            if current_group:
                groups.append(current_group)
            if any(word.lower() in title_words for word in words_between):
                title_positions_between = [j + keyword_positions[i - 1] + 1 for j, word in enumerate(words_between) if
                                           word.lower() in title_words]
                groups.append(title_positions_between)
            current_group = [keyword_positions[i]]
        prev_distance = distance
        if i < (length - 2) and word_list[keyword_positions[i]] != word_list[keyword_positions[i - 1]]:
            next_distance = keyword_positions[i + 2] - keyword_positions[i+1]

    groups.append(current_group)
    return groups


def split_into_words_and_symbols(text, stop_chars, keywords, title_words, skip_words):
    word_list = []
    # Split the text into lines
    lines = text.splitlines()

    for line in lines:
        line = line.strip() + '\n' # Remove spaces at the start and end of the line
        if any(line.startswith(word) for word in skip_words):
            continue

        # Split words and symbols, preserving delimiters
        words_symbols = re.split(r'(\b)', line)

        for word_symbol in words_symbols:
            if word_symbol and not word_symbol.isspace():
                # Further split words if necessary
                split_words = split_word(word_symbol, keywords, title_words, stop_chars)

                word_list.extend(split_words)
            else:
                word_list.append(word_symbol)

    return  [item for item in word_list if item != '']


def split_word(word, keywords, title_words, stop_chars):
    # If the word is a keyword, return as is
    for keyword in keywords:
        if keyword.lower() in word.lower():
            return re.split(f'({keyword})', word, flags=re.IGNORECASE)

    # Split the word if it is part of title words
    for title_word in title_words:
        if title_word.lower() in word.lower():
            return re.split(f'({title_word})', word, flags=re.IGNORECASE)

    for stop_char in stop_chars:
        if stop_char.lower() in word.lower():
            return re.split(f'({stop_char})', word, flags=re.IGNORECASE)
    # If it does not match any case, return the word as is
    return [word]



def check_mode_frequency(lst):
    # Count the occurrences of each element in the list
    counter = Counter(lst)

    # Find the mode (most common number) and its frequency
    mode, mode_freq = counter.most_common(1)[0]

    # Find the frequency of the next most common number
    next_common_freq = counter.most_common(2)[1][1] if len(counter) > 1 else 0

    # Calculate the required threshold for comparison
    threshold = next_common_freq * 1.5

    # Check if the mode has at least 50% more elements than the next most common number
    if mode_freq >= threshold and mode_freq > len(lst)*0.5:
        return True
    else:
        return False