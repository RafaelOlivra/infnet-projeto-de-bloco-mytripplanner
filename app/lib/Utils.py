import re
import requests
import json

from datetime import datetime, date

from services.AppData import AppData


class Utils:
    @staticmethod
    def slugify(string: str) -> str:
        """
        Convert a given string to a URL-friendly 'slug'.

        Steps:
        - Convert to lowercase and replace spaces with hyphens.
        - Replace accented characters with ASCII equivalents.
        - Remove non-alphanumeric characters, keeping only letters, numbers, and hyphens.
        - Remove leading/trailing hyphens and reduce multiple hyphens to one.

        Args:
            string (str): Input string to be slugified.

        Returns:
            str: Slugified version of the input string.
        """
        # Convert to lowercase and replace spaces with hyphens
        slug = string.lower().replace(" ", "-")

        # Replace accented characters with their ASCII equivalents
        accents_mapping = {
            r"[àáâãäå]": "a",
            r"[èéêë]": "e",
            r"[ìíîï]": "i",
            r"[òóôõö]": "o",
            r"[ùúûü]": "u",
            r"[ñ]": "n",
            r"[ç]": "c",
        }
        for pattern, replacement in accents_mapping.items():
            slug = re.sub(pattern, replacement, slug)

        # Remove any characters that are not alphanumeric or hyphens
        slug = re.sub(r"[^a-z0-9-]", "", slug)

        # Reduce consecutive hyphens to a single hyphen
        slug = re.sub(r"-+", "-", slug)

        # Strip hyphens from the beginning and end of the string
        return slug.strip("-")

    @staticmethod
    def is_json(data: str) -> bool:
        """
        Check if a given string is valid JSON.

        Args:
        - data (str): The string to check.

        Returns:
        - bool: True if the string is valid JSON, False otherwise.
        """
        try:
            json.loads(data)
            return True
        except ValueError:
            return False

    @staticmethod
    def url_encode(text: str) -> str:
        """
        Encode a text string for use in a URL.

        Args:
        - text (str): The text to encode.

        Returns:
        - str: The URL-encoded text.

        Raises:
        - ValueError: If the input is not a string.
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        return requests.utils.quote(text)

    @staticmethod
    def to_date_string(date: datetime | str, format="") -> str:
        # Convert string to datetime object from isoformat
        if isinstance(date, str):
            date = datetime.fromisoformat(date)

        if format == "display":
            return str(date.strftime(AppData().get_config("datetime_display_format")))
        else:
            # Return isoformat by default
            return date.isoformat()

    @staticmethod
    def to_datetime(_date) -> datetime:
        """
        Convert a date string to a datetime object.
        """
        # Attempt to convert from isoformat
        try:
            # If we have a string we convert it to a datetime object
            if isinstance(_date, str):
                _date = datetime.fromisoformat(_date)

            # If we have a date object we convert it to a datetime object
            if isinstance(_date, date):
                _date = datetime.combine(_date, datetime.min.time())

        # Attempt to convert from display format
        except ValueError:
            _date = datetime.strptime(
                _date, AppData().get_config(f"datetime_display_format")
            )

        return _date
