import requests
import bs4
import streamlit as st

from services.AppData import AppData
from services.Logger import SimpleLogger
from lib.Utils import Utils

from models.Attraction import AttractionModel


class YelpAttractionsScrapper:
    def __init__(self):
        return None

    @st.cache_data(ttl=86400, show_spinner=False)
    def get_near_attractions(
        _self,
        city_name: str,
        state_name: str,
        start: int = 0,
        limit: int = 18,
        recursive: bool = True,
    ) -> list[AttractionModel]:
        """
        Retrieves a JSON representation of nearby attractions in a given city and state.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            start (int, optional): The starting index of the attractions to retrieve. Defaults to 0 (Yelp outputs 10 cards for each page).
            limit (int, optional): The maximum number of attractions to retrieve. Defaults to 50.
            recursive (bool, optional): Whether to recursively fetch more attractions if the limit is not reached. Defaults to True.

        Returns:
            list[Attraction]: A list of Attraction objects.
        """
        search_query = Utils.url_encode(f"{city_name}, {state_name}")
        url = f"https://www.yelp.com.br/search?hl=pt_BR&find_desc=&find_loc={search_query}&start={start}"
        html = _self._fetch_html(url)

        soup = bs4.BeautifulSoup(html, "html.parser")
        attractions = soup.select('li div[data-testid="serp-ia-card"]')
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
                    review_count = int(review_text)
                    review_stars = 0
                    review_stars = float(review.previous_sibling.text)
                    if review_stars > 5 or review_stars < 0:
                        review_stars = -1

            # Create an Attraction object
            card = AttractionModel(
                **{
                    "name": anchor.select_one("img")["alt"],
                    "city_name": city_name,
                    "state_name": state_name,
                    "url": f"https://www.yelp.com{anchor['href']}",
                    "review_count": review_count,
                    "review_stars": review_stars,
                    "description": "",
                    "image": anchor.select_one("img")["src"],
                }
            )

            cards.append(card)

            # We used this in case the limit is less than what the page has
            if len(cards) >= limit:
                break

        SimpleLogger().log_info(
            f"Found {len(cards)} attractions in {city_name}, {state_name}"
        )

        # Handle limit, by calling the function recursively to get more cards
        while recursive and len(cards) < limit:
            _limit = limit - len(cards)
            _start = start + 10
            _cards = _self.get_near_attractions(
                city_name=city_name,
                state_name=state_name,
                start=_start,
                limit=_limit,
                recursive=False,
            )
            if _cards:
                cards.extend(_cards)
            else:
                break

        # Return the cards
        return cards

    # --------------------------
    # Utils
    # --------------------------
    @st.cache_data(ttl=86400, show_spinner=False)
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

        # api_key = AppData().get_api_key("scraperapi")
        # proxy_prefix = f"http://api.scraperapi.com?api_key={api_key}&premium=true&url="

        api_key = AppData().get_api_key("rfproxy")
        proxy_prefix = f"https://pr.rafaeloliveira.design/?api_key={api_key}&url="

        SimpleLogger().log_info(f"Fetching HTML content from: {url}")

        url = proxy_prefix + url

        response = requests.get(url)
        response.raise_for_status()

        return response.text
