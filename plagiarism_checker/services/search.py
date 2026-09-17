import os
import requests

#search interface to work with different search providers
class SearchProvider:
    def search(self, query, num_results = 5):
        raise NotImplementedError

class SearXNGSearchProvider(SearchProvider):
    def __init__(self, host=None):
        self.host = (host or os.environ.get("SEARXNG_HOST", "http://localhost:8080")).rstrip("/")
        self.endpoint = f"{self.host}/search"

    def search(self, query, num_results=5):
        # request parameters for SearXNG API
        params = {
            "q": query,
            "format": "json",
            "pageno": 1,
        }

        # extracting the relevant information from the SearXNG API response
        response = requests.get(self.endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", [])[:num_results]:
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                #"snippet": item.get("content")
            })

        return results