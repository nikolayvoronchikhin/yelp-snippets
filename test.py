
"""Tests for Yelp snippet creation.

These tests are meant to be run using nosetests.
"""


import snippets

class TestFullMatch(object):
    def test_(self):
        doc = query = 'pepperoni pizza'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == '[[HIGHLIGHT]]pepperoni pizza[[ENDHIGHLIGHT]]'


class TestSingleSentence(object):
    def test_single_word_query(self):
        doc = 'I really love deep dish pizza.'
        query = 'pizza'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == 'I really love deep dish [[HIGHLIGHT]]pizza[[ENDHIGHLIGHT]].'


    def test_multi_word_query(self):
        doc = 'I really love deep dish pizza.'
        query = 'deep dish pizza'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == 'I really love [[HIGHLIGHT]]deep dish pizza[[ENDHIGHLIGHT]].'

    def test_multiple_query_matches_1(self):
        doc = 'Their specialty pizza is deep dish pizza.'
        query = 'deep dish pizza'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == 'Their specialty [[HIGHLIGHT]]pizza[[ENDHIGHLIGHT]] is [[HIGHLIGHT]]deep dish pizza[[ENDHIGHLIGHT]].'

    def test_multiple_query_matches_2(self):
        doc = 'pizza pepperoni olive pizza olive pizza'
        query = 'pepperoni olive pizza'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == '[[HIGHLIGHT]]pizza[[ENDHIGHLIGHT]] [[HIGHLIGHT]]pepperoni olive pizza[[ENDHIGHLIGHT]] [[HIGHLIGHT]]olive pizza[[ENDHIGHLIGHT]]'


class TestCaseSensitivity(object):
    def test_mixed_doc(self):
        doc = 'Pepperoni Pizza is good pizza.'
        query = 'pepperoni pizza'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == '[[HIGHLIGHT]]Pepperoni Pizza[[ENDHIGHLIGHT]] is good [[HIGHLIGHT]]pizza[[ENDHIGHLIGHT]].'

    def test_mixed_query(self):
        doc = 'pepperoni pizza is good pizza.'
        query = 'pEppeRonI pIzZa'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == '[[HIGHLIGHT]]pepperoni pizza[[ENDHIGHLIGHT]] is good [[HIGHLIGHT]]pizza[[ENDHIGHLIGHT]].'

    def test_mixed_both(self):
        doc = 'pEpPeRoNi PiZzA'
        query = 'PePpErOnI pIzZa'
        snippet = snippets.highlight_doc(doc, query)
        assert snippet == '[[HIGHLIGHT]]pEpPeRoNi PiZzA[[ENDHIGHLIGHT]]'


class TestMaxChars(object):
    def test_no_tags(self):
        doc = 'I love pepperoni pizza. LOL!'
        query = 'pizza'
        snippet = snippets.highlight_doc(doc, query, max_chars=10)
        assert snippet == 'LOL!'

    def test_with_tags(self):
        doc = 'I love pepperoni pizza. Pizza!'
        query = 'pizza'
        snippet = snippets.highlight_doc(doc, query, max_chars=35)
        assert snippet == '[[HIGHLIGHT]]Pizza[[ENDHIGHLIGHT]]!'


class TestMaxSents(object):
    def test_one(self):
        doc = 'I love pepperoni. Pepperoni. Pepperoni.'
        query = 'pepperoni'
        snippet = snippets.highlight_doc(doc, query, max_sents=1)
        assert snippet.count('.') == 1

    def test_two(self):
        doc = 'I love pepperoni. Pepperoni. Pepperoni.'
        query = 'pepperoni'
        snippet = snippets.highlight_doc(doc, query, max_sents=2)
        assert snippet.count('.') == 2


class TestMaxCharsAndSents(object):
    def test(self):
        doc = 'Dog! Cat! The sentence with rat is too long.'
        query = 'rat'
        snippet = snippets.highlight_doc(doc, query, max_chars=10, max_sents=1)
        assert snippet in 'Dog!', 'Cat!'


#
# Testing "private" functions
#
class TestFindQuerySpans(object):
    def test_single_1(self):
        words = query = 'pizza'.split()
        spans = snippets._find_query_spans(words, query)
        assert spans == [(0, 1)]

    def test_single_2(self):
        words = 'Pizza is great .'.split()
        query = 'pizza'.split()
        spans = snippets._find_query_spans(words, query)
        assert spans == [(0, 1)]

    def test_multiple(self):
        words = """My favorite pizza is deep dish . Deep dish pizza is hella
                   sick pizza bro .""".split()
        query = 'deep dish pizza'.split()
        spans = snippets._find_query_spans(words, query)
        assert spans == [(2, 3), (4, 6), (7, 10), (13, 14)]

    def test_overlap(self):
        words = 'pizza pepperoni pizza'.split()
        query = 'pepperoni pizza'.split()
        spans = snippets._find_query_spans(words, query)
        assert spans == [(0, 1), (1, 3)]


    def test_full(self):
        words = 'Pizza ? I love deep dish ! Deep dish pizza is great .'.split()
        query = 'deep dish pizza'.split()
        spans = snippets._find_query_spans(words, query)
        assert spans == [(0, 1), (4, 6), (7, 10)]


#
# Testing "private" string-utility functions
#
class TestSplitIntoSentences(object):
    def test_single_period(self):
        doc = 'That sure is a nice hat.'
        assert len(snippets._split_into_sentences(doc)) == 1
        
    def test_single_with_comma(self):
        doc = 'I like apples, oranges, and peas.'
        sentences = snippets._split_into_sentences(doc) 
        assert sentences == ['I like apples, oranges, and peas.']

    def test_single_questionmark(self):
        doc = 'You like my hat?'
        sentences = snippets._split_into_sentences(doc) 
        assert sentences == ['You like my hat?']

    def test_single_exclamationmark(self):
        doc = 'Of course I do!'
        sentences = snippets._split_into_sentences(doc) 
        assert sentences == ['Of course I do!']

    def test_single_ellipsis(self):
        doc = 'The food was alright...'
        sentences = snippets._split_into_sentences(doc) 
        assert sentences == ['The food was alright...']

    def test_double_period(self):
        doc = 'I am tired. Go away.'
        sentences = snippets._split_into_sentences(doc) 
        assert sentences == ['I am tired.', 'Go away.']

    def test_double_marks(self):
        doc = 'I am tired! Would you leave?'
        sentences = snippets._split_into_sentences(doc) 
        assert sentences == ['I am tired!', 'Would you leave?']

    def test_double_ellipsis(self):
        doc = 'Well whatever... Yeah whatever...'
        sentences = snippets._split_into_sentences(doc) 
        print sentences
        assert sentences == ['Well whatever...', 'Yeah whatever...']

    def test_double_period(self):
        doc = 'I am tired. Go away.'
        sentences = snippets._split_into_sentences(doc) 
        assert sentences == ['I am tired.', 'Go away.']

    def test_dollar_sign(self):
        doc = 'I paid $2.34 for it.'
        sentences = snippets._split_into_sentences(doc)
        print sentences
        assert sentences == ['I paid $2.34 for it.']

    def test_no_punctuation(self):
        doc = 'I want some Thai food'
        sentences = snippets._split_into_sentences(doc)
        assert sentences == ['I want some Thai food']


class TestSplitIntoWords(object):
    def test_lowercase_period(self):
        sentence = 'i am not a frog.'
        words = snippets._split_into_words(sentence)
        assert words == ['i', 'am', 'not', 'a', 'frog', '.']

    def test_mixedcase_period(self):
        sentence = 'I am NOT a frog.'
        words = snippets._split_into_words(sentence)
        assert words == ['I', 'am', 'NOT', 'a', 'frog', '.']

    def test_commas(self):
        sentence = 'Comma, comma, comma.'
        words = snippets._split_into_words(sentence)
        assert words == ['Comma', ',', 'comma', ',', 'comma', '.']

    def test_exclamationmark(self):
        sentence = 'You are SO a frog!'
        words = snippets._split_into_words(sentence)
        assert words == ['You', 'are', 'SO', 'a', 'frog', '!']

    def test_questionmark(self):
        sentence = 'Why am I a frog?'
        words = snippets._split_into_words(sentence)
        assert words == ['Why', 'am', 'I', 'a', 'frog', '?']

    def test_ellipsis(self):
        sentence = 'The food was horrible...'
        words = snippets._split_into_words(sentence)
        assert words == ['The', 'food', 'was', 'horrible', '...']

    def test_numbers_own_word(self):
        sentence = 'There are 4 lights.'
        words = snippets._split_into_words(sentence)
        assert words == ['There', 'are', '4', 'lights', '.']

    def test_numbers_part_word(self):
        sentence = 'I am word47word.'
        words = snippets._split_into_words(sentence)
        assert words == ['I', 'am', 'word47word', '.']

    def test_dollar_in_word(self):
        sentence = 'It was $10.'
        words = snippets._split_into_words(sentence)
        assert words == ['It', 'was', '$10', '.']

    def test_dollar_own_word_1(self):
        sentence = 'That place was $.'
        words = snippets._split_into_words(sentence)
        assert words == ['That', 'place', 'was', '$', '.']

    def test_dollar_own_word_2(self):
        sentence = 'That place was $$.'
        words = snippets._split_into_words(sentence)
        assert words == ['That', 'place', 'was', '$$', '.']

    def test_price_1(self):
        sentence = 'It costs $47.'
        words = snippets._split_into_words(sentence)
        assert words == ['It', 'costs', '$47', '.']

    def test_price_2(self):
        sentence = 'It costs $9.47.'
        words = snippets._split_into_words(sentence)
        assert words == ['It', 'costs', '$9.47', '.']

    def test_price_3(self):
        sentence = 'It costs .47.'
        words = snippets._split_into_words(sentence)
        assert words == ['It', 'costs', '.47', '.']


class TestJoinWords(object):
    def test_simple(self):
        words = ['How', 'are', 'you']
        joined = snippets._join_words(words)
        assert joined == 'How are you'

    def test_question(self):
        words = ['how', 'are', 'you', '?']
        joined = snippets._join_words(words)
        assert joined == 'how are you?'

    def test_exclamation(self):
        words = ['Go', 'away', '!']
        joined = snippets._join_words(words)
        assert joined == "Go away!"

    def test_multiple_marks(self):
        words = ['Go', 'away', '!', 'I', "don't", 'like', 'you', '.']
        joined = snippets._join_words(words)
        assert joined == "Go away! I don't like you."


    def test_mixed(self):
        words = ['I', 'paid', '$24', '.', 'So', 'there', '!']
        joined = snippets._join_words(words)
        assert joined == 'I paid $24. So there!'

    def test_ellipsis(self):
        words = ['Whatever', '...', 'Hey', 'there', '.']
        joined = snippets._join_words(words)
        assert joined == 'Whatever... Hey there.'


