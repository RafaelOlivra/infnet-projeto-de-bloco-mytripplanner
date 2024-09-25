import re


class Utils:
    def __init__(self):
        pass

    def slugify(self, string: str) -> str:
        # Convert to lowercase and replace spaces with hyphens
        slug = string.lower().replace(" ", "-")

        # Replace special characters with their closest ASCII equivalent
        slug = re.sub(r'[àáâãäå]', 'a', slug)
        slug = re.sub(r'[èéêë]', 'e', slug)
        slug = re.sub(r'[ìíîï]', 'i', slug)
        slug = re.sub(r'[òóôõö]', 'o', slug)
        slug = re.sub(r'[ùúûü]', 'u', slug)
        slug = re.sub(r'[ñ]', 'n', slug)
        slug = re.sub(r'[ç]', 'c', slug)

        # Remove any characters that are not alphanumeric or hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)

        # Ensure that consecutive hyphens are reduced to a single hyphen
        slug = re.sub(r'-+', '-', slug)

        # Strip hyphens from the beginning and end
        return slug.strip('-')
