import requests


def search_papers(query, limit=5):
    url = "https://api.crossref.org/works"

    params = {
        "query": query,
        "rows": limit
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    papers = []

    for item in data["message"]["items"]:
        papers.append({
            "title": item.get("title", ["No title"])[0],
            "authors": item.get("author", []),
            "year": item.get("published", {}).get("date-parts", [[None]])[0][0],
            "doi": item.get("DOI", ""),
            "url": item.get("URL", "")
        })

    return papers


if __name__ == "__main__":
    results = search_papers("machine learning")

    for paper in results:
        print("\nTitle:", paper["title"])
        print("Year:", paper["year"])
        print("DOI:", paper["doi"])
        print("URL:", paper["url"])