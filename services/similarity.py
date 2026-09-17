"""Find how closely a short phrase matches somewhere within a longer page of text."""

import difflib
import re

WORD_RE = re.compile(r"\S+")

# using a window sliding approach to find the best match of a phrase within a page of text
# and returning the highest difflib similatity ratio found and the exact text window that contains it

def best_snippet_match(phrase, page_text, window_size = 3, min_shared_words = 2):
    phrase_words = WORD_RE.findall(phrase)
    page_words = WORD_RE.findall(page_text)
    n = len(phrase_words)
    if not page_words or n == 0:
        return 0.0, None

    phrase_word_set = {word.lower() for word in phrase_words}
    phrase_lower = phrase.lower()

    # initializing variables to keep track of the best match found
    best_ratio = 0.0
    best_snippet = None

    min_size = max(1, n - window_size)
    max_size = n + window_size

    # sliding the window
    for size in range(min_size, max_size + 1):
        # last_start is the last index where a window of the current size can start in the page_words list
        last_start = max(0, len(page_words) - size)
        for start in range(0, last_start + 1):
            # checking how many words are shared between the phrase and the current window
            window_words = page_words[start:start + size]
            shared = 0
            for w in window_words:
                if w.lower() in phrase_word_set:
                    shared +=1
            # skipping the windows if they don't share enough words with the phrase
            if shared < min_shared_words:
                continue
            window = " ".join(window_words)
            # choosing the best match based on the highest similarity ratio
            ratio = difflib.SequenceMatcher(None, phrase_lower, window.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_snippet = window

    return best_ratio, best_snippet