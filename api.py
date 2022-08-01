# Imports

from serpapi import GoogleSearch
from random import choice, randint
import requests

from config import serp_key, search_tokens

_ACCOUNT_API_BASE_URL = "https://serpapi.com/account?api_key={key}"

_safe_search = "active"

def set_safe_search(flag):
    global _safe_search
    _safe_search = "active" if flag else "off"
    print(f"Safe search now set to {_safe_search}")

def safe_search():
    global _safe_search
    return _safe_search == "active"

def get_random_image():
    global _safe_search
    params = {
        "q": choice(search_tokens()) + " " + str(randint(1, 99999)),
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
    elif not results["images_results"]:
        return None, f"No images found for query {params['q']}"
    
    return results["images_results"][0], ""

def get_image_from_query(query_string):
    global _safe_search
    params = {
        "q": query_string + " " + str(randint(1, 99999)),
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
    elif not results["images_results"]:
        return None, f"No images found for query {query_string}"

    print(f"Searched with query string {params['q']}, got image with url {results['images_results'][0]['original']}")
    
    return results["images_results"][0], ""

def num_requests_remaining():
    response = requests.get(_ACCOUNT_API_BASE_URL.format(key = serp_key()))
    if response.status_code == 200:
        return response.json()["total_searches_left"]
    else:
        print(f"Failed to get response from account API, gave status {response.status_code}")
        return None

