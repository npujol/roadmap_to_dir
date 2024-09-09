import re


def clean_names(name: str) -> str:
    return re.sub(pattern=r"[^\w\s]", repl="-", string=name)
