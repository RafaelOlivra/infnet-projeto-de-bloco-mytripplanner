import requests
import os
import bs4
import json
import streamlit as st


class YelpScrapper:
    def __init__(self):
        return None

    @st.cache_data(ttl=86400)
    def get_near_attractions_json(
        _self, city_name: str, state_name: str, start: int = 0, limit: int = 10
    ):
        """
        Retrieves a JSON representation of nearby attractions in a given city and state.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            start (int, optional): The starting index of the attractions to retrieve. Defaults to 0.
            limit (int, optional): The maximum number of attractions to retrieve. Defaults to 10.

        Returns:
            str: A JSON string representing the nearby attractions. If no attractions are found, an empty JSON object is returned.
        """
        search_query = _self._url_encode(f"{city_name}, {state_name}")
        url = f"https://www.yelp.com.br/search?hl=pt_BR&find_desc=&find_loc={search_query}&start={start}&limit={limit}"
        html = _self._fetch_html(url)

        soup = bs4.BeautifulSoup(html, "html.parser")
        attractions = soup.select('li div[data-testid="serp-ia-card"]')
        # attractions = soup.select('a[href^="/biz/"]:has(img)')

        if not attractions:
            return {}

        cards = []
        for attraction in attractions:
            anchor = attraction.select_one('a[href^="/biz/"]:has(img)')
            # Review are inside a font element with text (x reviews)
            reviews = attraction.select("span")
            review_text = ""
            review_stars = -1
            for review in reviews:
                if " reviews)" in review.text:
                    review_text = review.text.replace(" reviews)", "").replace("(", "")
                    review_stars = 0
                    review_stars = float(review.previous_sibling.text)
                    if review_stars > 5 or review_stars < 0:
                        review_stars = -1

            card = {
                "name": anchor.select_one("img")["alt"],
                "url": f"https://www.yelp.com{anchor['href']}",
                "review_count": review_text,
                "review_stars": review_stars,
                "description": "",
                "image": anchor.select_one("img")["src"],
            }
            cards.append(card)
            if len(cards) >= limit:
                break

        # Return the JSON data
        return json.dumps(cards)

    @st.cache_data(ttl=86400)
    def _fetch_html(_self, url: str) -> str:
        """
        Fetches the HTML content from the given URL.

        Args:
            url (str): The URL to fetch the HTML content from.

        Returns:
            str: The HTML content of the response.

        Raises:
            requests.HTTPError: If there is an HTTP error during the request.
        """
        # Apply hardcoded proxy for now
        # TODO: Implement a better way to handle proxies
        proxy_prefix = "http://api.scraperapi.com?api_key=ce1e058f17f38e5a9e49a9ee467375fd&&premium=true&url="
        url = proxy_prefix + url

        response = requests.get(url)
        response.raise_for_status()

        return response.text

    def _url_encode(self, text):
        """
        Encode a text string for use in a URL.

        Args:
        - text (str): The text to encode.

        Returns:
        - str: The URL-encoded text.
        """
        return requests.utils.quote(text)
