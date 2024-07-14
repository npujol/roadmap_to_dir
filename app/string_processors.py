import re


# NOTE: some roadmaps have unexpected characters in their urls, so we skip them
def clean_url_strings(string: str) -> str:
    return re.sub(pattern=r"[^a-zA-Z0-9-]", repl="-", string=string.lower())
