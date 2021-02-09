import re
import nltk
import heapq
from typing import Dict
from collections import Counter

def preprocess(_text: str) -> str:
    # Removing special characters and digits
    text = re.sub(r'\s+[^a-zA-Z]', ' ', _text)
    return text

def get_word_frequency(text: str) -> Dict[str, float]:
    stopwords = nltk.corpus.stopwords.words('portuguese')

    word_frequencies = dict(Counter([
        word for word in nltk.word_tokenize(text) if word not in stopwords
    ]))
    
    maximum_frequncy = max(word_frequencies.values())
    normalized_word_frequencies = {word : word_frequencies[word]/maximum_frequncy for word in word_frequencies}
    return normalized_word_frequencies

def get_senteces_score(text: str, word_frequencies: Dict[str, float]) -> Dict[str, float]:
    sentence_list = nltk.sent_tokenize(text)
    sentence_scores = {sent : sum([word_frequencies.get(word, 0)
                            for word in nltk.word_tokenize(sent.lower())]) 
                            for sent in sentence_list}
    return sentence_scores

def get_summary(_text: str, n=10):
    text = preprocess(_text)
    word_frequencies = get_word_frequency(text)
    sentence_scores = get_senteces_score(text, word_frequencies)
    summary_sentences = heapq.nlargest(n, sentence_scores, key=sentence_scores.get)
    summary_sentences.sort(key = lambda x:text.find(x))
    summary = ' '.join(summary_sentences)
    return summary