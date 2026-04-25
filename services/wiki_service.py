import urllib.request
import urllib.parse
import json


def get_wiki_info(query: str) -> dict:
    """
    Fetch a Wikipedia summary for a given search query.
    Returns a dict with: title, extract, url, thumbnail.
    Falls back gracefully if nothing is found.
    """
    # Step 1: Search for the best matching page title
    search_url = (
        "https://en.wikipedia.org/w/api.php"
        "?action=query&list=search&format=json"
        "&srsearch=" + urllib.parse.quote(query) +
        "&srlimit=1&utf8=1"
    )
    try:
        with urllib.request.urlopen(search_url, timeout=5) as resp:
            search_data = json.loads(resp.read().decode())
        search_results = search_data.get("query", {}).get("search", [])
        if not search_results:
            return {"title": query, "extract": "", "url": "", "thumbnail": ""}
        best_title = search_results[0]["title"]
    except Exception:
        return {"title": query, "extract": "", "url": "", "thumbnail": ""}

    # Step 2: Fetch the full intro extract + thumbnail for that title
    extract_url = (
        "https://en.wikipedia.org/w/api.php"
        "?action=query&prop=extracts|pageimages|info"
        "&exintro=1&explaintext=1&inprop=url"
        "&format=json&pithumbsize=400"
        "&titles=" + urllib.parse.quote(best_title)
    )
    try:
        with urllib.request.urlopen(extract_url, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))

        extract = page.get("extract", "").strip()
        # Trim to first 3 paragraphs to keep it readable
        paragraphs = [p.strip() for p in extract.split("\n") if p.strip()]
        short_extract = "\n\n".join(paragraphs[:3])

        thumbnail = page.get("thumbnail", {}).get("source", "")
        full_url = page.get("fullurl", f"https://en.wikipedia.org/wiki/{urllib.parse.quote(best_title)}")

        return {
            "title": page.get("title", best_title),
            "extract": short_extract,
            "url": full_url,
            "thumbnail": thumbnail,
        }
    except Exception:
        return {"title": query, "extract": "", "url": "", "thumbnail": ""}


def enrich_objects_with_wiki(objects: list) -> list:
    """
    For each detected object label, fetch its Wikipedia summary.
    Returns a list of dicts: [{label, title, extract, url, thumbnail}, ...]
    """
    seen = set()
    enriched = []
    for obj in objects:
        if obj.lower() in seen:
            continue
        seen.add(obj.lower())
        info = get_wiki_info(obj)
        enriched.append({
            "label": obj,
            **info
        })
    return enriched
