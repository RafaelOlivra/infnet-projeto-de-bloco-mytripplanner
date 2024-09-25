import re


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
