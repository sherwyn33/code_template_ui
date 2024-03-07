import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# function for finding uncommon tokens
def find_uncommon_tokens(subarray1, subarray2):
    flat_subarray1 = [item for sublist in subarray1 for item in sublist]
    flat_subarray2 = [item for sublist in subarray2 for item in sublist]
    return list(set([token for token in flat_subarray1 if token not in flat_subarray2]))


# function for replacing uncommon tokens
def replace_uncommon_tokens(token_dict, subarray, uncommon_tokens, title_words, skip_words: []):
    title_words = [title_word.lower() for title_word in title_words]
    for i, token in enumerate(uncommon_tokens):
        token = token.lower()
        if token in skip_words:  # check if token is a number in format 1nnnn
            continue
        if token in token_dict:
            replace_value = token_dict.get(token)
        else:
            if token in title_words:
                replace_value = 20000 + (i + 1)
            else:
                replace_value = 30000 + (i + 1)
            if token not in token_dict:
                token_dict[token] = replace_value
        # subarray = [[str(replace_value) if y.lower() == token else y for y in x] for x in subarray]
    return subarray, token_dict


# function for computing cosine similarity
def compute_similarity(subarray1, subarray2):
    flat_subarray1 = [item for sublist in subarray1 for item in sublist]
    flat_subarray2 = [item for sublist in subarray2 for item in sublist]
    words1 = ' '.join(flat_subarray1)
    words2 = ' '.join(flat_subarray2)
    if len(words1) > 2 and len(words2) > 2:
        vectorizer = CountVectorizer().fit_transform([words1, words2])
        vectors = vectorizer.toarray()
        return cosine_similarity(vectors)[0][1]
    elif len(words1) == len(words2):
        return 1
    else:
        return 0


def get_diff(array1, array2, title_words1, title_words2, keywords: []):
    # process
    new_array1 = []
    token_dict = {}
    window_size = 2  # change this value to increase or decrease the window size
    global_uncommon_tokens = []
    # len_array2 = len(array2)
    for i in range(len(array1)):
        # if len_array2 < i:
        #     continue

        # compute similarities with neighbouring subarrays in array2
        try:
            similarities = [compute_similarity(array1[i], array2[j]) if j < len(array2) else 0 for j in
                        range(i - window_size, i + window_size + 1)]
        except:
            print()

        max_sim_index = np.argmax(similarities) + i - window_size

        uncommon_tokens = find_uncommon_tokens(array1[i], array2[max_sim_index])


        new_subarray1, subarray_token_dict = replace_uncommon_tokens(token_dict, array1[i], uncommon_tokens, title_words1 + title_words2, keywords)
        new_array1.append(new_subarray1)


        # token_dict.update({k: v for k, v in subarray_token_dict.items() if k not in token_dict})

    return new_array1, token_dict


def only_stop_Values(matrix):
    not_allowed_values = ["\n"]
    for array in matrix:
        if set(array).issubset(set(not_allowed_values)):
            return False

    return True

