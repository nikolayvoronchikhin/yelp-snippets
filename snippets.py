#!/usr/bin/env python

"""Yelp review snippet creation.

Author: Colin Pollock ~ colin@colinpollock.net

This module's only public function is `highlight_doc`, which takes a document 
and a query and produces a snippet that is composed of sentences from the
document with terms from the query highlighted. The number of characters and
sentences in the snippet can be constrained by passing in integers for the 
optional parameters `max_sents` and `max_chars`.


Example Usage
>>> doc = 'The only good pizza is a pepperoni pizza.'
>>> query = 'pepperoni pizza'
>>> highlighted_snippet = highlight_doc(doc, query)
#TODO
"""

__all__ = ['highlight_doc']


from optparse import OptionParser
import re
import sys


# Words that are likely to be included in opinion-indicating sentences.
OPINION_INDICATORS = set("""
    nice good better best beautiful great delicious favorite wonderful friendly 
    bad worst worse ugly horrible disgusting worst mean
    love loved loves like liked likes amaze amazed amazes
    hate hated hates avoid avoided avoids
    """.split())

PUNCTUATION = set(('.', '?', '!', '...'))

#TODO: pull of RE for sentences/words

OPENTAG, CLOSETAG = '[[HIGHLIGHT]]', '[[ENDHIGHLIGHT]]'

INFINITY = float('infinity')


def highlight_doc(doc, query, max_chars=INFINITY, max_sents=INFINITY):
    """Return snippets from `doc` with `query` words tagged.
    
    Args:
      doc: String that is document to be highlighted.
      query: String of words representing the query terms.
      max_chars: Integer indicating the max number of chars in the snippet.
      max_sents: Integer indicating the max number of sentences in the snippet.
    Returns:
      The most relevant snippet with all query terms highlighted.
    """
    # Break document and query into lists of sentences and words.
    sentences = [_split_into_words(sent) for sent in _split_into_sentences(doc)]
    query = _split_into_words(query)

    # Select the best sentences given the constraints.
    snippet_sents = _select_snippet_sentences(sentences, query, max_chars, 
                                              max_sents)

    snippet_words = []
    for sent in snippet_sents:
        snippet_words += sent

    # Surround spans from `query` in the highlighted snippet with tags.
    highlighted_snippet = _insert_highlights(snippet_words, query)
    

    if not highlighted_snippet:
        return ''
    else:
        return _join_words(highlighted_snippet)
    

def _insert_highlights(snippet_words, query_words):
    """Highlight all query_words in snippet_words.

    Args:
      snippet_words: List of Strings representing a snippet.
      query_words: List of Strings representing query terms.
    Returns:
      List of Strings that are in snippet_words with all words that are in
      query_words surrounded by highlight tags. When a string of query words
      is matched the whole span is enclosed in tags.
    """
    spans = dict(_find_query_spans(snippet_words, query_words))
    strings = []
    i = 0
    while i < len(snippet_words):
        if spans.has_key(i):
            start, end = i, spans[i]
            strings.append(OPENTAG)
            strings.extend(snippet_words[start: end])
            strings.append(CLOSETAG)
            i = end
        else:
            strings.append(snippet_words[i])
            i += 1
    return strings 

#
# Snippet selection
#
def _select_snippet_sentences(sentences, query_words, max_chars, max_sents):
    """Select a relevant sublist of sentences.

    Args:
      sentences: List of Lists of Strings (words) in a review.
      query_words: List of strings representing query terms.
    Returns:
      List of sentences taken from `sentences` not containing more sentences
      than `max_sents` nor more characters than `max_chars`.
    """
    ranked_sentences = _rank_sentences(sentences, query_words)

    char_count = sent_count = 0
    sentences = []
    for sentence in ranked_sentences:
        if char_count > max_chars or sent_count > max_sents:
            break

        else:
            sentences.append(sentence)
            char_count += len(sentence) + len(OPENTAG) + len(CLOSETAG)
            sent_count += 1
    return sentences

def _rank_sentences(sentences, query_words):
    """Compute each sentence's score.

    Args:
      sentences: List of List (sentence) of Strings (words).
      query_words: List of Strings that are words in the input query.
    Returns:
      List of sentences ranked from highest- to lowest-scoring.
      #TODO:List of (sentence, score) pairs.
    """
    scores = []
    for sentence in sentences:
        score = _score_sentence(sentence, query_words)
        scores.append((score, sentence))

    scores.sort(reverse=True)
    return [score[1] for score in scores]
    

def _count_opinion_indicators(sentence):
    """Count the number of words associated with opinions in `sentences`.

    Args:
      sentence: List of Strings representing words.
    Returns:
      Integer that is the number of `OPINION_INDICATORS` found in `sentence`.
    """
    return sum(1 for word in OPINION_INDICATORS if word in sentence)


def _score_sentence(sentence, query_words):
    """Compute score for a sentence wrt `query_words` and `OPINION_INDICATORS`.

    Args:
      sentence: List of Strings (words).
      query_words: List of Strings that are words in the query.
    Returns:
      Integer that is the score.
    """
    opinion_indicator_count = _count_opinion_indicators(sentence)
    query_match_score = _compute_query_match_score(sentence, query_words)
    return opinion_indicator_count + query_match_score
    

def _compute_query_match_score(sentence, query_words):
    """Compute the extent to which `sentence` matches words in `query_words`.

    To obtain a score:
      * Find all subspans in `sentence` that are also in `query_words`.
      * The score is the sum of the squares of the lengths of each non-
        overlapping subspan.
    
    Args:
      sentence: List of Strings, where each String is a word.
      query_words: List of Strings representing words in the query.
    Returns:
      Integer representing the number of partial and whole `query_words` matches
      in `sentence`.
    """
    spans = _find_query_spans(sentence, query_words)
    return sum(len(span) ** 2 for span in spans)


def _find_query_spans(words, query_words):
    """Find all non-overlapping spans in `words` that are in `query_words`.
    Args:
      words: List of Strings
      query_words: List of strings
    Returns:
      List of Integer pairs indicating the start and end indices of all non-
      overlapping `query_words` in `words`. Longer strings are preferred over
      short ones.

    Example:
    >>> words = 'Pizza ? I love deep dish ! Deep dish pizza is great .'.split()
    >>> query_words = 'deep dish pizza'.split()
    >>> print _find_query_spans(words, query_words)
    [(0, 1), (4, 6), (7, 10)]
    """
    spans = []
    in_span = False
    old_query_index = None
    span_start = None

    # Queries are considered case-insensitive.
    words = [word.lower() for word in words]
    query_words = [query_word.lower() for query_word in query_words]

    for i, word in enumerate(words):
        if word in query_words:
            query_index = query_words.index(word)

            if in_span:
                if old_query_index + 1 != query_index:
                    # Found end of span and beginning of new
                    span_end = i
                    spans.append((span_start, span_end))
                    span_start = i
            else:
                # Found beginning of new span
                in_span = True
                span_start = i
            old_query_index = query_index

        elif word not in query_words and in_span:
            # Found end of span
            in_span = False
            span_end = i
            spans.append((span_start, span_end))

    if in_span:
        # Add final span if one ends at the list list item
        spans.append((span_start, len(words)))

    return spans

#
# String breaking and joining
#
def _join_words(words):
    """Join `words` with spaces only where appropriate.
    
    Spaces are omitted:
      * preceding punctuation
      * around highlight tags
      * at the end of the string

    Args:
      words: List of Strings.
    Returns:
      String that is a smart joining of `words`.
    """
    strings = []
    for i, word in enumerate(words[: -1]):
        if i + 1 < len(words) and words[i + 1] in PUNCTUATION:
            strings.append(word)
        elif word == '[[HIGHLIGHT]]':
            strings.append(word)
        elif i + 1 < len(words) and words[i + 1] == '[[ENDHIGHLIGHT]]':
            strings.append(word)
        else:
            strings.append(word + ' ')
    return ''.join(strings) + words[-1]


def _split_into_sentences(doc):
    """Split a document at punctuation boundaries.
    Args:
      doc: String representing a review document.
    Returns:
      List of individual sentences (Strings) in `doc`.
    """
    doc = re.sub(r'\s+', ' ', doc)
    pat = re.compile(r"""([A-Za-z0-9 ,'"@#$%^&*()~=+-]+(\.{3}|[.?!]))""")
    sentences = [sent[0].strip() for sent in pat.findall(doc)]

    # Return the doc itself as the sentence if there are no matches so that
    # a document without punctuation will be considered a single sentence.
    if not sentences:
        return [doc]
    else:
        return sentences


def _split_into_words(sentence):
    """
    Args:
      sentence: String
    Returns:
      List of words and punctuation marks in `sentence`.
    """
    pat = re.compile(r"""
            ['"]?[-A-Za-z0-9@#$%^&*()'~=+_-]+['"]? # letters, optionally quoted
            |
            ,                      # comma
            |
            \.{3}                  # ellipsis
            |
            [.?!]                  # other punctuation
            """, re.VERBOSE)
    return pat.findall(sentence)
    return [sent[0] for sent in pat.findall(sentence)]


def main(args):
    """Command-line interface to snippet maker.
    
    The first positional argument is a document and the second is a query. The
    program prints out a snippet from the document with all occurrences of the
    query enclosed in HIGHLIGHT tags. Both full and query matches are
    highlighted. For example, for the query 'deep dish pizza' occurrences of the    strings 'deep dish pizza', 'deep dish', 'dish pizza', 'deep', 'dish', 
    'pizza' would all be highlighted. In each case, only the longest match
    is highlighted.

    The maximum number of characters or sentences to be included in the snippet
    can be specified using the --chars and --sents options.
    """

    description = 'Command-line interface to the snippet maker.'
    usage = '%prog <DOCUMENT> <QUERY_STRING> [options]'
    parser = OptionParser(usage=usage, description=description)

    parser.add_option('-c', '--chars', dest='max_chars', default=INFINITY,
        help='The maximum number of characters to include in the snippet.')

    parser.add_option('-s', '--sents', dest='max_sents', default=INFINITY,
        help='The maximum number of sentences to include in the snippet.')


    options, args = parser.parse_args(args)

    if len(args) != 2:
        parser.error('Incorrect number of arguments.')
    doc = args[0]
    query = args[1]

    snippet = highlight_doc(doc, query, options.max_chars, options.max_sents)
    print snippet

    return 0


if __name__ == '__main__':
    exit(main(sys.argv[1:]))

