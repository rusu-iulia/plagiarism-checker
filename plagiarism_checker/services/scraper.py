"""Fetch a URL and extract just its main body."""

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 PlagiarismChecker/1.0"
    )
}

# ignoring tags that are never part of the readable article body
NOISE_TAGS = ["script", "style", "nav", "header", "footer", "form", "noscript", "aside", "svg"]

MIN_WORDS_PER_PARAGRAPH = 4 # anything shorter are probably filler words

def fetch_and_clean(url, timeout=10):
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # using only the content-type header is not enough, some sites return text/html but the body is actually JSON or XML
    content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type and not response.text.strip().startswith("<"):
            return None

    # parsing the HTML and removing the noise tags
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(NOISE_TAGS):
        tag.decompose()

    # using the semantic containers when present, otherwise falling back to the body tag or the whole document
    main = soup.find("article") or soup.find("main") or soup.body or soup

    # extracting the text from paragraphs and list items, filtering out short ones
    paragraphs = [element.get_text(" ", strip=True) for element in main.find_all(["p", "li"])]
    paragraphs = [p for p in paragraphs if len(p.split()) >= MIN_WORDS_PER_PARAGRAPH]

    # returning the cleaned text as a single string
    return "\n".join(paragraphs) if paragraphs else None