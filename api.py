# Imports

from serpapi import GoogleSearch
from random import choice, randint, shuffle
import requests

from config import serp_key, search_tokens, write_cache, read_cache

_ACCOUNT_API_BASE_URL = "https://serpapi.com/account?api_key={key}"

# Caches search results to lessen use of the API for similar search terms.
# Addition of safe search parameter should allow cached search results to honor the current safe search flag
# Schema (as JSON):
# {
#   "$SEARCH_TOKEN?$_safe_search": {
#       "used": list[int],
#       "results": list[ImageResults]
#   },
#   ...
# }
_search_cache = read_cache()

_safe_search = "active"

def load_cache():
    global _search_cache

def set_safe_search(flag):
    global _safe_search
    _safe_search = "active" if flag else "off"
    print(f"Safe search now set to {_safe_search}")

def safe_search():
    global _safe_search
    return _safe_search == "active"

def get_random_image():
    global _safe_search
    global _search_cache

    search_token = choice(search_tokens())

    cache_key = f"{search_token}?{_safe_search}"

    if cache_key in _search_cache and len(_search_cache[cache_key]["used"]) < len(_search_cache[cache_key]["results"]):
        # Yes, this is kinda inefficient, no I don't particularly care
        # This list is guaranteed to have at least one element
        available_idxs = [i for i in range(len(_search_cache[cache_key]["results"])) if i not in _search_cache[cache_key]["used"]]
        
        shuffle(available_idxs)

        _search_cache[cache_key]["used"].append(available_idxs[0])

        write_cache(_search_cache)

        print(f"Using cached search results for query {search_token}")

        return _search_cache[cache_key]["results"][available_idxs[0]], ""
    else:
        params = {
            "q": f"{search_token} {str(randint(1, 99999))}",
            "tbm": "isch",
            "ijn": "0",
            "api_key": serp_key(),
            "safe": _safe_search
        }

        print(f"Searching for {params['q']} with safe search {params['safe']}")

        search = GoogleSearch(params)
        results = search.get_dict()

        if not results:
            return None, f"Unable to search for query {params['q']}"
        elif "images_results" not in results:
            return None, f"No images found for query {params['q']}"

        _search_cache[cache_key] = {
            "used": [],
            "results": results["images_results"]
        }

        write_cache(_search_cache)
        
        return results["images_results"][0], ""

def get_image_from_query(query_string):
    global _safe_search
    global _search_cache

    cache_key = f"{query_string}?{_safe_search}"

    if cache_key in _search_cache and len(_search_cache[cache_key]["used"]) < len(_search_cache[cache_key]["results"]):
        # This list is guaranteed to have at least one element
        available_idxs = [i for i in range(len(_search_cache[cache_key]["results"])) if i not in _search_cache[cache_key]["used"]]
        
        shuffle(available_idxs)

        _search_cache[cache_key]["used"].append(available_idxs[0])

        write_cache(_search_cache)

        print(f"Using cached search results for query {query_string}")

        return _search_cache[cache_key]["results"][available_idxs[0]], ""
    else:
        params = {
            "q": f"{query_string} {str(randint(1, 99999))}",
            "tbm": "isch",
            "ijn": "0",
            "api_key": serp_key(),
            "safe": _safe_search
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        print(f"Searching for {params['q']} with safe search {params['safe']}")

        if not results:
            return None, f"Unable to search for query {query_string}"
        elif "images_results" not in results:
            return None, f"No images found for query {query_string}, results gave {results}"

        print(f"Searched with query string {params['q']}, got image with url {results['images_results'][0]['original']}")

        _search_cache[cache_key] = {
            "used": [],
            "results": results["images_results"]
        }

        write_cache(_search_cache)
        
        return results["images_results"][0], ""

def num_requests_remaining():
    response = requests.get(_ACCOUNT_API_BASE_URL.format(key = serp_key()))
    if response.status_code == 200:
        return response.json()["total_searches_left"]
    else:
        print(f"Failed to get response from account API, gave status {response.status_code}")
        return None
