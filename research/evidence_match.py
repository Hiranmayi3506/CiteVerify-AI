
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def match_evidence(claim, abstracts, top_k=3):

    if not abstracts:
        return []

    # Convert research abstracts into numerical vectors
    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        tfidf_matrix = vectorizer.fit_transform([claim] + abstracts)
    except ValueError:
        return []

    # Compare the claim with each abstract
    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    results = []

    for index, score in enumerate(similarity_scores):
        results.append({
            "evidence": abstracts[index],
            "similarity_score": round(float(score), 4)
        })

    # Sort from highest similarity to lowest
    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return results[:top_k]


if __name__ == "__main__":

    claim = "Regular exercise improves sleep quality."

    abstracts = [
        "Physical activity is associated with better sleep quality.",
        "Climate change affects global temperatures.",
        "Regular exercise may improve sleep duration and quality."
    ]

    matches = match_evidence(claim, abstracts)

    for item in matches:
        print("\nEvidence:", item["evidence"])
        print("Similarity:", item["similarity_score"])
