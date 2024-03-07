from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def external_references_similarity(node1, node2):
    references1 = list(node1['external'])
    references2 = list(node2['external'])

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(references1 + references2)

    cos_sim = cosine_similarity(tfidf_matrix[:len(references1)], tfidf_matrix[len(references1):])

    return cos_sim[0][0]


def reference_counts_similarity(node1, node2):
    total_refs1 = len(node1.get('internal', set())) + len(node1.get('package', set())) + len(
        node1.get('linked_reference', []))
    total_refs2 = len(node2.get('internal', set())) + len(node2.get('package', set())) + len(
        node2.get('linked_reference', []))

    return 1 - abs(total_refs1 - total_refs2) / (total_refs1 + total_refs2 + 1e-10)


def node_similarity(node1, node2):
    external_sim = external_references_similarity(node1, node2)
    count_sim = reference_counts_similarity(node1, node2)

    return (external_sim + count_sim) / 2
