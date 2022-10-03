import re
import nltk
import heapq
import string
from collections import Counter

from typing import *

# tf idf
#https://www.freecodecamp.org/news/how-to-extract-keywords-from-text-with-tf-idf-and-pythons-scikit-learn-b2a0f3d7e667/
#https://www.bogotobogo.com/python/NLTK/tf_idf_with_scikit-learn_NLTK.php
stopwords = nltk.corpus.stopwords.words('portuguese')

def preprocess(_text: str) -> str:
    # Removing special characters and digits
    text = re.sub(r'\s+[^a-zA-Z]', ' ', _text)
    return text


def get_word_frequency(text: str) -> Dict[str, float]:
    """Returns the word frequency inside the given text"""
    word_frequencies = dict(Counter([
        word for word in nltk.word_tokenize(text) if word not in stopwords
    ]))
    #empty dict
    if not word_frequencies: return {}

    maximum_frequncy = max(word_frequencies.values())
    normalized_word_frequencies = {word : word_frequencies[word]/maximum_frequncy for word in word_frequencies}
    return normalized_word_frequencies


def get_senteces_score(text: str, word_frequencies: Dict[str, float]) -> Dict[str, float]:
    """Returns the sentence score given the word frequencies. A sequence score
    is the sum of the frequency of the words contained in the sentence"""
    sentence_list = nltk.sent_tokenize(text)
    sentence_scores = {sent : sum([word_frequencies.get(word, 0)
                            for word in nltk.word_tokenize(sent.lower())]) 
                            for sent in sentence_list}
    return sentence_scores


def get_summary(_text: str, n=10) -> str:
    """Summarizes the given text into n sentences"""
    text = preprocess(_text)
    word_frequencies = get_word_frequency(text)
    sentence_scores = get_senteces_score(text, word_frequencies)
    summary_sentences = heapq.nlargest(n, sentence_scores, key=sentence_scores.get)
    summary_sentences.sort(key = lambda x:text.find(x))
    summary = ' '.join(summary_sentences)
    return summary


def get_ngrams_freq(_text: str, n: int) -> Dict[Any, int]:
    """Returns the frequencies of the ngrams inside the given text. Stop
    words are removed"""
    # remove punctuation
    text = _text.translate(str.maketrans('', '', string.punctuation))
    # count ngrams
    n_grams = list(nltk.ngrams(
        [word for word in nltk.word_tokenize(text) if word not in stopwords], n))
    n_grams_frequencies = dict(Counter(n_grams))
    return n_grams_frequencies