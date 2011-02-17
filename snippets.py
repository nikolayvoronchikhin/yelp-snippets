#!/usr/bin/env python

import re

OPINION_INDICATORS = set("""
    nice good better best beautiful great delicious favorite wonderful friendly 
    bad worst worse ugly horrible disgusting worst mean
    love loved loves like liked likes amaze amazed amazes
    hate hated hates avoid avoided avoids
    """.split())



def highlight_doc(doc, query, opentag='[[HIGHLIGHT]]', 
                  closetag='[[ENDHIGHLIGHT]]', max_chars=float('infinity'), 
                  max_sents=float('infinity')):
    """Return snippets from `doc` with `query` words tagged."""
    # Break document and query into lists of sentences and words.
    sentences = [split_into_words(sent) for sent in split_into_sentences(doc)]
    query = split_into_words(query)

    # Select the best sentences given the constraints.
    snippet_sents = select_snippet_sentences(sentences, query, max_chars, 
                                             max_sents, opentag, closetag)

    snippet_words = []
    for sent in snippet_sents:
        snippet_words += sent

    # Surround spans from `query` in the highlighted snippet with tags.
    highlighted_snippet = insert_highlights(snippet_words, query, opentag, 
                                            closetag)

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
    ranked_sentences = rank_sentences(sentences, query_words)

    char_count = sent_count = 0
    sentences = []
    for sentence in ranked_sentences:
        if char_count > max_chars or sent_count > max_sents:
            break

        else:
            sentences.append(sentence)
            char_count += len(sentence) + len(opentag) + len(closetag)
            sent_count += 1

    return sentences

def rank_sentences(sentences, query_words):
    scores = []
    for sentence in sentences:
        score = score_sentence(sentence, query_words)
        scores.append((score, sentence))

    scores.sort(reverse=True)
    return [score[1] for score in scores]
    


def count_opinion_indicators_in_sentence(sentence):
    return sum(1 for word in OPINION_INDICATORS if word in sentence)

def score_sentence(sentence, query):
    opinion_indicator_count = count_opinion_indicators_in_sentence(sentence)
    query_match_score = compute_query_match_score(sentence, query)
    return opinion_indicator_count + query_match_score
    


def compute_query_match_score(sentence, query):
    """Compute the extent to which the sentence matches the query.

    To obtain a score:
      * Find all subspans in `sentence` that are also in `query`.
      * The score is the sum of the squares of the lengths of each subspan.
    
    Args:
      sentence: List of Strings, where each String is a word.
      query: List of Strings.
    Returns:
      Integer representing the number of partial and whole `query` matches in 
      `sentence`.
    """
    spans = find_query_spans(sentence, query)
    return sum(len(span) ** 2 for span in spans)



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

def insert_highlights(snippet_words, query_words, opentag, closetag):
    spans = dict(find_query_spans(snippet_words, query_words))

    strings = []
    i = 0
    while i < len(snippet_words):
        if spans.has_key(i):
            start, end = i, spans[i]
            strings.append(opentag)
            strings.extend(snippet_words[start: end])
            strings.append(closetag)
            
            i = end
        else:
            strings.append(snippet_words[i])
            i += 1

    return strings 



def find_query_spans(words, query):
    """Find all non-overlapping spans in `words` that are in `query`.
    Args:
      words: List of Strings
      query: List of strings
    Returns:
      List of Integer pairs indicating the start and end indices of all non-
      overlapping query words in `words`. Longer strings are preferred over
      short ones.

    Example:
    >>> words = 'Pizza ? I love deep dish ! Deep dish pizza is great .'.split()
    >>> query = 'deep dish pizza'.split()
    >>> print find_query_spans(words, query)
    [(0, 1), (4, 6), (7, 10)]
    """
    spans = []
    in_span = False

    # Queries are considered case-insensitive.
    words = [word.lower() for word in words]
    query = [query_word.lower() for query_word in query]

    for i, word in enumerate(words):
        if word in query and not in_span:
            # Found beginning of new span
            in_span = True
            span_start = i
        elif word not in query and in_span:
            # Found end of span
            in_span = False
            span_end = i
            spans.append((span_start, span_end))
    return spans

def main():
    doc = """I really love deep dish pizza. They have good salads too. But the 
             dish pizza is incredible. Great pizza."""
    query = 'deep dish pizza'
    highlighted = highlight_doc(doc, query)
    print highlighted

if __name__ == '__main__':
    main()
