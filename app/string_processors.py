import re


def clean_url_strings(string: str) -> str:
    # Convert to lowercase, remove leading/trailing spaces, and replace non-alphanumeric
    # characters with dashes
    cleaned_string = re.sub(r"[^a-zA-Z0-9-]+", "-", string.lower().strip())

    # Replace multiple consecutive dashes with a single dash, and remove any
    # leading/trailing dashes
    return re.sub(r"^-+|-+$", "", re.sub(r"-{2,}", "-", cleaned_string))
