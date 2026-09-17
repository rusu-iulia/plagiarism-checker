"""Picking random word-phrases out of a document's text, for use as search queries."""
import random
import re

# regex to match words
WORD_RE = re.compile(r"\S+")

def extract_random_phrases(text, num_phrases = 8, min_words = 5, max_words = 10, seed = None):
    words = WORD_RE.findall(text)
    if not words:
        return []
    # for short documents, the whole text is just one phrase
    if len(words) <= max_words:
        return [" ".join(words)]

    # random number generator that will be used to pick a random start index and phrase length
    random_gen = random.Random(seed)
    phrases = []
    # keeping track of the start indices of the chosen phrases to avoid overlap
    used_starts = set()
    # attempts counter to avoid infinite loops in case of very short documents
    attempts = 0
    max_attempts = num_phrases * 15

    while len(phrases) < num_phrases and attempts < max_attempts:
        attempts += 1
        phrase_length = random_gen.randint(min_words, max_words)
        max_start = len(words) - phrase_length
        if max_start < 0:
            continue
        
        start = random_gen.randint(0, max_start)
        if start in used_starts:
            continue
        used_starts.add(start)
        phrases.append(" ".join(words[start:start + phrase_length]))

    return phrases