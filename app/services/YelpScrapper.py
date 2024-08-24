
import requests
import os
import bs4
import json
from functools import lru_cache


class YelpScrapper:
    def __init__(self):
        return None

    def get_near_attractions_json(self, city: str, state: str, start: int = 0, limit: int = 10):
        """
        Retrieves a JSON representation of nearby attractions in a given city and state.

        Args:
            city (str): The name of the city.
            state (str): The name of the state.
            start (int, optional): The starting index of the attractions to retrieve. Defaults to 0.
            limit (int, optional): The maximum number of attractions to retrieve. Defaults to 10.

        Returns:
            str: A JSON string representing the nearby attractions. If no attractions are found, an empty JSON object is returned.
        """
        search_query = self.url_encode(f"{city} {state}")
        url = f"https://www.yelp.com.br/search?find_desc=Atra%C3%A7%C3%B5es&find_loc={search_query}&start={start}&limit={limit}"
        html = self.fetch_html(url)

        soup = bs4.BeautifulSoup(html, "html.parser")
        attractions = soup.select('a[href^="/biz/"]:has(img)')

        if not attractions:
            return {}

        cards = []
        for attraction in attractions:
            card = {
                "name": attraction.select_one('img')['alt'],
                "url": f"https://www.yelp.com{attraction['href']}",
                "image": attraction.select_one('img')['src']
            }
            cards.append(card)

        # Return the JSON data
        return json.dumps(cards)

    @lru_cache(maxsize=100)
    def fetch_html(self, url: str) -> str:
        """
        Fetches the HTML content from the given URL.

        Args:
            url (str): The URL to fetch the HTML content from.

        Returns:
            str: The HTML content of the response.

        Raises:
            requests.HTTPError: If there is an HTTP error during the request.
        """

        # Create a temporary directory to store the response
        # TODO: Implement a better way to handle temporary files
        temp_dir = os.path.dirname(__file__)+"/../.temp"

        # Create the directory if it doesn't exist
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Return the cached response if it exists
        if os.path.exists(temp_dir+'/response.html'):
            with open(temp_dir+'/response.html', 'r') as f:
                return f.read()

        # Apply hardcoded proxy for now
        # TODO: Implement a better way to handle proxies
        proxy_prefix = 'http://api.scraperapi.com?api_key=ce1e058f17f38e5a9e49a9ee467375fd&&premium=true&url='
        url = proxy_prefix + url

        response = requests.get(url)
        response.raise_for_status()

        # Save the response to a file for debugging
        with open(temp_dir+'/response.html', 'w') as f:
            f.write(response.text)

        return response.text

    def url_encode(self, text):
        """
        Encode a text string for use in a URL.

        Args:
        - text (str): The text to encode.

        Returns:
        - str: The URL-encoded text.
        """
        return requests.utils.quote(text)
