"""
Key word matching class for question matching
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import string
from fuzzywuzzy import fuzz as fw
import re



# set xlsx file path with names
path = 'sp500.xlsx'

def lower(string):
    return string.lower()

def remove_punctuation(s):
    s = ''.join([i for i in s if i not in frozenset(string.punctuation)])
    return s


def to_words(review_text):

    letters_only = remove_punctuation(review_text)
    words = letters_only.lower().split()                             

    stops = set(stopwords.words("english"))

    meaningful_words = [w for w in words if not w in stops]   
    
    letters = list(string.ascii_lowercase)
    words_without_letters = [w for w in meaningful_words if not w in letters]   
    
    return( " ".join( words_without_letters )) 

def manual_removes(terms):
    remove_terms = terms

    remove_terms.remove('a')
    remove_terms.remove('co')
    remove_terms.append('data')
    remove_terms.append('price')
    remove_terms.append('ge')
    remove_terms.remove('brands')
    remove_terms.remove('of')

    return remove_terms

def clean_names(data):
    """ data is sp500_names df """
    df_names = data.copy()

    split_names = pd.Series(sum([x.split(' ') for x in df_names['name']], []))
    
    freq = 3
    term_count = split_names.value_counts()
    remove_terms = list(term_count.loc[term_count>freq].index.values)
    remove_terms = manual_removes(remove_terms)

    clean_names = []
    for x in df_names['name']:
        new_x = x
        for y in remove_terms:
            new_x = new_x.replace(y, '')
        clean_names.append(new_x.strip())
    df_names['clean_name'] = clean_names

    return df_names

def extract_names(path):
    sp500_data = pd.read_excel(path, header=None)
    sp500_names = pd.DataFrame()
    sp500_names['ticker'] = sp500_data.iloc[:,0]
    sp500_names['name'] = sp500_data.iloc[:,1]
    sp500_names['name'] = sp500_names['name'].apply(lower)
    clean_df = clean_names(sp500_names)

    return clean_df

class KeyMatch:

    def __init__(self, alpha):

        self.names = extract_names(path)
        self.a = alpha # name vs ticker weighting


    def extract_field(self, text, data):
        """ Get general field: metric or name, to_words(text) input """
        a = self.a
        words = text.split(' ')
        max_scores = []
        tickers = []
        max_scores2 = []
        for w in words:
            scores = 0
            ticker = ''
            for i, row in data.iterrows():
                nms = re.findall(r"[\w']+", row['clean_name'])
                fuzzs = []
                try:
                    for nm in nms:
                        fuzz = fw.ratio(nm, w)
                        fuzzs.append(fuzz)
                    if scores <= max(fuzzs):
                        scores = max(fuzzs)
                        ticker = row['ticker']
                except:
                    continue
            max_scores.append(scores)
            tickers.append(ticker)
        for tk in tickers:
            scores2 = 0
            for w in words:
                fuzz2 = fw.ratio(tk.lower(), w)
                if fuzz2 == 100:
                    return tk
                if scores2 <= fuzz2:
                    scores2 = fuzz2
            max_scores2.append(scores2)
        avg_score = a*np.array(max_scores) + (1.0-a)*np.array(max_scores2)
        df = pd.DataFrame()
        df['ticker'] = tickers
        df['name_score'] = max_scores
        df['ticker_score'] = max_scores2
        df['avg_score'] = avg_score
        self.name_analysis = df 
        return tickers[np.argmax(self.name_analysis['avg_score'])]       

    def get_name(self, text):
        """
        Inputs: string sentence with removed stopwords
        
        Returns: company ticker
        
        Selects ticker that has max average match of all words in the input with the
        company names and company tickers. If there is a perfect match return the ticker
        directly and stop.
        """
        tk = self.extract_field(to_words(text), self.names)
        return tk

    def nm_analysis(self, text):
        """
        Inputs: string sentence with removed stopwords
        
        Prints: company ticker + df with likely choices
        """

        tk = self.extract_field(to_words(text), self.names)
        print('Predicted Ticker: ' + tk)
        print(self.name_analysis.sort_values('avg_score', ascending=False))


