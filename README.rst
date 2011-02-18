YELP REVIEW SNIPPET MAKER
=========================

Quickstart
----------
Run examples.py to see some output from snippets.highlight_doc. 
    python examples.py


You can also use the main program in snippets.py:
    python snipetmaker.py 'I love pizza.' 'pizza'


If you want to use the snippet maker from within Python you'll want to use 
snippets.highlight_doc. Its required arguments are:
  1. The document to be snippified.
  2. The query string to be highlighted.

Its optional arguments are:
  3. The maximum number of characters to include in the snippet, including tags.
  4. The maximum number of sentences to include in the snippet.

The default values for both are INFINITY.


Snippet Rationale
---------------------------
It looks like the Yelp review snippets are generally made by finding a query 
word and including part of the string surrounding it. I thought it could be
interesting to try to take sentence structure into account. 

A potential benefit of using sentence structure is that snippets won't include 
fragments like "Crust ties the entire pizza together and if".  They'll be 
coherent for the most part and as grammatical as the original reviews.
  
Since there may be a need for snippets of different lengths I added parameters
to snippets.highlight_doc that make it possible to construct snippets less than
a certain number of characters or sentences. This could be useful, for example,
on the main search results page where not all sentences containing the query
string could fit.

A natural question is which sentences to include. The most obviously important
feature in the decision is the presence of query terms. Any word from a query
appearing in a sentence increases its score, but longer strings of query words
do so exponentially. Consider this document/query pair:
   *I like pizza. Pizza with pepperoni. I ordered a pepperoni pizza.*
   *pepperoni pizza*
The word "pizza" in the first sentence earns it 1 point. The second sentence
contains two query words so it gets 1+1=2 points. The third sentence also
contains two query words, but they appear in the same order found in the query.
This earns the third sentence 2^2=4 points. So in general, for each span of
query terms in a sentence, the sentence gets the sum of the squares of the
lengths of all query spans in it.

In addition to the number of query matches, a sentence's score also depends on
the presence of opinion-indicating words like "love", "amazing", "disgusting",
etc.. A point is added to a sentence's score for each of these words that it
contains. 

This single keyword based approach is really simplstic. At first I thought it
would be fun to really go all out here by thinking about what makes a good
review sentence. In addition to opinion words it's possible that reviewers tend
to use certain particular stylistic or linguistic features. Some of those 
regularities could be captured with regular expressions, but it'd probably help
to have a good POS tagger and possibly some sort of parser. So I thought I'd 
wait until later and see how much NLTK would help here. 

If I had actual resources and really needed something cool I would probably get
people to score the relevance of each sentence in a review and then try to find
a correlation between the scores and sentence features like position, length,
the presence of certain words and parts of speech, and lots of other cool stuff
that's in the literature.



Code Improvements
------------
* At some point I was going to refactor the code into a few classes but I ended
  up liking the all-function module. It's a little inefficient though right now
  because I end up rebuilding some datastructures that I could just save as a
  class attribute. Of course I could just memoize the functions.

* There are a few unit tests that are failing and both are related to splitting
  text. The doc=>sentences and sentence=>words splitters both break when the
  text contains a decimal, as in "I paid $9.47.". I'm past the deadline I set
  to send this in though.  I would guess that this would be fairly
  straightforward to fix this, but the regular expressions would have to get a
  bit uglier.

* And speaking of regular expressions, the ones I have for words and sentences
  are pretty ugly. I created most of my unit tests by just thinking of example
  sentences and documents. If I were to look through more actual reviews from 
  Yelp I'm sure I would find a lot more weird cases I'd want to cover.

