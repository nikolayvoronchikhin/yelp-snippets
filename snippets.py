#!/usr/bin/env python

import re
from pprint import pprint


def highlight_doc(doc, query, opentag='[[HIGHLIGHT]]', closetag='[[ENDTAG]]', 
                  max_chars=float('infinity'), max_sents=float('infinity')):
    """Return snippets from `doc` with `query` words tagged."""
    # Break document and query into lists of sentences and words.
    sentences = [split_into_words(sent) for sent in split_into_sentences(doc)]
    query = split_into_words(query)

    # Select the best sentences given the constraints.
    snippet_sents = select_snippet_sentences(sentences, query, max_chars, 
                                             max_sents, opentag, closetag)

    # Surround spans from `query` in the highlighted snippet with tags.
    highlighted_snippet = insert_highlights(snippet_sents, query)
    if not highlighted_snippet:
        return ''
    else:
        return join_words(highlighted_snippet)
    

def join_words(words):
    """Create a string with spaces between words but not before punctuation."""
    strings = []
    for i, word in enumerate(words[: -1]):
        if i + 1 < len(words) and words[i + 1] in '.?!':
            strings.append(word)
        else:
            strings.append(word + ' ')
    return ''.join(strings) + words[-1]

def select_snippet_sentences(sentences, query_words, max_chars, max_sents,
                             opentag, closetag):
    """
    """
    return sentences


def split_into_sentences(doc):
    doc = re.sub(r'\s+', ' ', doc)
    pat = re.compile(r"""[A-Za-z '"]+[.?!]""")
    sentences = [sent.strip() for sent in pat.findall(doc)]
    return sentences


def split_into_words(sentence):
    """
    Args:
      sentence: String
    Returns:
      List of words and punctuation marks in `sentence`.
    """
    pat = re.compile(r"""   
            ['"]?[-A-Za-z']+['"]?  # letters, optionally quoted
            |
            \.{3}                  # ellipsis
            |
            [.?!]                  # punctuation
            """, re.VERBOSE)
    return pat.findall(sentence)

def insert_highlights(snippet_sents, query_words):
    strings = []
    for sent in snippet_sents:
        for word in sent:
            if word in query_words:
                word = '[%s]' % word
            strings.append(word)
    return strings 


def main():
    doc = """I really love deep dish pizza. They have good salads too. But the 
             deep dish pizza is incredible."""
    query = 'deep dish pizza'
    highlighted = highlight_doc(doc, query)
    print highlighted

if __name__ == '__main__':
    main()
