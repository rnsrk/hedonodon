from germansentiment import SentimentModel
from pandas import DataFrame
import numpy as np
from scipy.special import softmax
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import spacy
from collections import Counter

# Preprocess text (username and link placeholders)
def preprocess(text:str) -> str:
    """Removes tags and urls from text.

    Parameters
    ------
        text: str
        The raw toot from Mastodon.
    Returns
    ------
        str
        The cleaned text.
    """
    new_text = []

    for t in text.split(" "):
        t = '' if t.startswith('@') and len(t) > 1 else t
        t = '' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


class SentiTooter:
    """Class to analyze the toots.
    """

    def __init__(self):
        """Initilize the sentiment models and labels.
        """
        self.deModel = SentimentModel()
        self.enModelType = f"cardiffnlp/twitter-roberta-base-sentiment"
        self.enModel, self.enTokenizer = self.initModel()
        # https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt
        self.labels = ['negative', 'neutral', 'positive']
        self.sia = SentimentIntensityAnalyzer()

    def analyze(self, language:str, content:str) -> list[str, str, float]:
        """Analyzes the sentiments of the toots.

        Parameters
        ------
            language: str
            The language tag of the toot.
            content: str
            The toot content.
        Returns
        ------
            list[str, str, float]
            A list with the sentiment, analyzer type, and sentiment score.
        """
        match language:
            case 'de':
                sentimentList, probabilitiesList = self.deModel.predict_sentiment([content], output_probabilities=True)
                sentiment = sentimentList[0]
                score = {i[0]: i[1] for i in probabilitiesList[0]}[sentiment]
                return [sentiment, 'germanSentiment', score]
            case 'en':
                text = preprocess(content)
                encoded_input = self.enTokenizer(text, return_tensors='pt')
                output = self.enModel(**encoded_input)
                scores = output[0][0].detach().numpy()
                scores = softmax(scores)
                #print(scores)
                sentimentIndexWithMaxScore = np.argmax(scores)
                sentimentLabel = self.labels[sentimentIndexWithMaxScore]
                sentiment = [sentimentLabel, 'twitter-roberta-base-sentiment', max(scores)]
                #print(sentiment)
                return sentiment
            case _:
                compound = self.sia.polarity_scores(content)['compound']
                #print(self.sia.polarity_scores(content), 'vaderSentiment')
                if compound > (1 / 3):
                    return ['positive', 'vaderSentiment']
                elif compound < (-1 / 3):
                    return ['negative', 'vaderSentiment']
                else:
                    return ['neutral', 'vaderSentiment']


    def initModel(self):
        """Initialize the english models.

        Returns
        ------
            tupel
                The pretrained model and tokenizer.
        """
        # PT
        tokenizer = AutoTokenizer.from_pretrained(self.enModelType)
        tokenizer.save_pretrained(self.enModelType)
        model = AutoModelForSequenceClassification.from_pretrained(self.enModelType)
        model.save_pretrained(self.enModelType)
        return model, tokenizer

def translateToots(yesterdaysToots:DataFrame) -> DataFrame:
    """Translates all toots to english.

    Returns
    ------
        Dataframe
        Containing the english translated toots.
    """
    yesterdaysTootsTranslated = yesterdaysToots
    for index, row in yesterdaysTootsTranslated.iterrows():
        if (row['language'] != 'en'):
            try:
                yesterdaysTootsTranslated.at[index,'toot'] = translateToot(row['language'], row['toot'])
                yesterdaysTootsTranslated.at[index,'language'] = 'en'
            except:
                yesterdaysTootsTranslated.drop(index)
    return yesterdaysTootsTranslated

def translateToot(language:str, toot:str) -> str:
    """Translate a toot in english.

    Parameters
    ------
        language:str
        The language of the toot.
        toot: str
        The toot content.

    Returns
    ------
        str
        The in english translated toot.
    """
    content = preprocess(toot)
    return GoogleTranslator(source=language, target='en').translate(content)

def countWords(concatedToots: str, number: int) -> list:
    """Counts the word frequencies in all toots of a given sentiment.

    Parameters
    ------
        concatedToots: str
        All toots from a sentiment.
        number: int
        Number of words to calculate word frequencies.

    Returns
    ------
        list
        List containing tuple of word and word frequency.
    """
    nlp = spacy.load('en_core_web_lg')
    doc = nlp(concatedToots)

    # noun tokens that arent stop words or punctuations
    nouns = [token.text
            for token in doc
            if (not token.is_stop and
                not token.is_punct and
                token.pos_ == "NOUN")]

    # five most common noun tokens
    noun_freq = Counter(nouns)
    return noun_freq.most_common(number)

def createWordFrequenciesPerSentiment(translatedToots:DataFrame) -> str:
    """Count all word frequencies of all toots per sentiment.

    Paramters
    ------
        translatedToots: DataFrame
        The dataframe with all toots in english.

    Returns
    ------
        str
        Containing words and wourd counts per sentiment.
    """
    sentimentList = []
    for sentiment in ['positive', 'neutral', 'negative']:
        tootsSeries = translatedToots[translatedToots['sentiment'] == sentiment].toot
        wordFrequencies = countWords(tootsSeries.str.cat(sep=' '), 5)
        FrequenciesList = []
        for Frequencies in wordFrequencies:
             FrequenciesList.append(str(Frequencies[0]) + ' (' + str(Frequencies[1]) + ')')
        list2String = ', '.join(FrequenciesList)
        sentimentString = sentiment + ': ' + list2String
        sentimentList.append(sentimentString)
    wordFrequenciessPerSentiments = '\n'.join(sentimentList)
    return wordFrequenciessPerSentiments