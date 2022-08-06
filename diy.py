# System imports
import os
import requests
import traceback
from random import choice, randint, shuffle

# Imports for Google-Image-Scraper
from scraperlib.GoogleImageScraper import GoogleImageScraper as Scraper
from scraperlib.patch import webdriver_executable

# Imports from here
from config import search_tokens

webdriver_path = os.path.normpath(os.path.join(os.getcwd(), "scraperlib", 'webdriver', webdriver_executable()))
image_path = os.path.normpath(os.path.join(os.getcwd(), "scraperlib", 'photos'))

def get_random_image():
    global webdriver_path
    global image_path
    # Shouldn't need caching, since we're not exercising an API that I'm rate-limited on
    search_token = f"{choice(search_tokens())} {randint(1, 99999)}"

    try:
        return Scraper(
            webdriver_path, image_path, search_token, 1, True
        ).find_image_urls()[0], ""
    except Exception:
        return None, str(traceback.format_exc())

def get_image_from_query(query_string):
    global webdriver_path
    global image_path

    # Shouldn't need caching, since we're not exercising an API that I'm rate-limited on
    search_token = f"{query_string} {randint(1, 99999)}"

    try:
        return Scraper(
            webdriver_path, image_path, search_token, 1, True
        ).find_image_urls()[0], ""
    except Exception:
        return None, str(traceback.format_exc())

    
