#!/usr/bin/env python

"""Example of snippet creation."""


import sys

from snippets import highlight_doc as hd, INFINITY

DATA = [
    # Single Sentence
    ('Queries are case-insensitive.',
     'I like pIzZa.', 
     'PiZzA', 
     INFINITY, INFINITY
    ),
    

    ('The longest span possible is highlighted.',
     'I like pepperoni pizza.', 
     'pepperoni pizza',
     INFINITY, INFINITY
    ),

    ('There can be multiple matches.',
     'My favorite pizza is pepperoni pizza', 
     'pepperoni pizza', 
     INFINITY, INFINITY
    ),

    # Multiple Sentences
    ('Only sentences with query words or "opinion words" are included.',
     "I love their pesto. It's amazing! This sentence is pointless.",
     'pesto',
     INFINITY, INFINITY
    ),

    ('But if there are no matches then all are returned.',
     'They have sushi. They also have Thai food.',
     'burgers',
     INFINITY, INFINITY
    ),

    ('Sentences are broken at punctuation marks.',
     'Pizza. Sushi? Pizza... Sushi!',
     'pizza',
     INFINITY, INFINITY
    ),

    ('But at the moment the sentence breaking is a little stupid!',
     'It cost $9.47.',
     'cost',
     INFINITY, INFINITY
    ),

    ("""You can limit the number of sentences in the snippet. The ones with
     the most query term matches and opinion words are selected. (1 Sent)""",
     'I love sushi. Sushi is my favorite food. Yes, I love sushi!',
     'sushi',
     INFINITY, 1,
    ),

    ("""The order of sentences is preserved and unselected ones are omitted.
     Here the snippet is limited to two sentences and the middle is skipped.""",
     "I love sushi. It's alright. Get me some sushi!",
     'sushi',
     INFINITY, 2
    ),

    ("""Or the number of characters (including tags) can be limited. Here, the
     snippet must be <= 5 characters. Only the last sentence will fit.""",
     "Pizza is my favorite food. I love it. LOL!",
     'pizza',
     5, INFINITY
    ),
    

]

def print_examples(out=sys.stdout):
    """Print examples of the snippet creation to `out`."""
    for (description, doc, query, chars, sents) in DATA:
        snippet = hd(doc, query, chars, sents)
        print >> out, '#### %s ####' % description
        print >> out, 'DOCUMENT: """%s"""' % doc
        print >> out, 'QUERY:    """%s"""' % query
        print >> out, 'SNIPPET:  """%s"""' % snippet
        print >> out, '\n'


if __name__ == '__main__':
    print_examples()

