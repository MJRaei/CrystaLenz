import os, requests
from typing import List, Dict, Any

import dotenv

dotenv.load_dotenv()

GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def search_papers(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Search Google Programmable Search (Custom Search JSON API) and return a list of result URLs.

    Args:
        query: The full search query string (e.g., 'graphene MnO2 filetype:pdf').
        max_results: Maximum URLs to return (API returns up to 10 per call; overall cap 100).

    Returns:
        dict with:
          - status: "ok" | "error"
          - query: original query
          - urls: list[str] of result links (unique, trimmed of query params)
          - total: int number of urls returned
          - message: optional error/info message
    """
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_ID:
        return {"status": "error", "query": query,
                "urls": [], "total": 0,
                "message": "Missing GOOGLE_CSE_API_KEY or GOOGLE_CSE_ID env vars."}

    # API only returns up to 10 per call and caps at 100 total. :contentReference[oaicite:1]{index=1}
    max_results = max(1, min(int(max_results), 100))
    url = "https://www.googleapis.com/customsearch/v1"

    all_urls: List[str] = []
    calls_needed = (max_results + 9) // 10

    for i in range(calls_needed):
        start_index = i * 10 + 1
        results_for_call = min(10, max_results - len(all_urls))
        params = {"key": GOOGLE_CSE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query,
                  "num": results_for_call, "start": start_index}
        r = requests.get(url, params=params, timeout=20)
        if r.status_code != 200:
            return {"status": "error", "query": query, "urls": list(dict.fromkeys(all_urls)),
                    "total": len(all_urls),
                    "message": f"HTTP {r.status_code}: {r.text[:300]}"}
        data = r.json()
        items = data.get("items", [])
        batch = [item["link"].split("?")[0] for item in items if "link" in item]
        all_urls.extend(batch)
        if len(all_urls) >= max_results or not items:
            break

    unique_urls = list(dict.fromkeys(all_urls))[:max_results]
    print(f"🔗 Total unique links found: {len(unique_urls)}")
    return {"status": "ok", "query": query, "urls": unique_urls, "total": len(unique_urls)}