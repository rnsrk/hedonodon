from germansentiment import SentimentModel
import numpy as np
from scipy.special import softmax
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []

    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


class SentiTooter:
    """"""

    def __init__(self):
        self.deModel = SentimentModel()
        self.enModelType = f"cardiffnlp/twitter-roberta-base-sentiment"
        self.enModel, self.enTokenizer = self.initModel()
        # https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt
        self.labels = ['negative', 'neutral', 'positive']
        self.sia = SentimentIntensityAnalyzer()

    def analyze(self, language, content):
        match language:
            case 'de':
                sentiment = self.deModel.predict_sentiment([content])
                sentiment.append('germanSentiment')
                return sentiment
            case 'en':
                text = preprocess(content)
                encoded_input = self.enTokenizer(text, return_tensors='pt')
                output = self.enModel(**encoded_input)
                scores = output[0][0].detach().numpy()
                scores = softmax(scores)
                sentimentIndexWithMaxScore = np.argmax(scores)
                sentimentLabel = self.labels[sentimentIndexWithMaxScore]
                sentiment = [sentimentLabel, 'twitter-roberta-base-sentiment']
                return sentiment
            case _:
                compound = self.sia.polarity_scores(content)['compound']
                if compound > (1 / 3):
                    return ['positive', 'vaderSentiment']
                elif compound < (-1 / 3):
                    return ['negative', 'vaderSentiment']
                else:
                    return ['neutral', 'vaderSentiment']



    def initModel(self):
        # PT
        tokenizer = AutoTokenizer.from_pretrained(self.enModelType)
        tokenizer.save_pretrained(self.enModelType)
        model = AutoModelForSequenceClassification.from_pretrained(self.enModelType)
        model.save_pretrained(self.enModelType)
        return model, tokenizer

    # # TF
    # model = TFAutoModelForSequenceClassification.from_pretrained(MODEL)
    # model.save_pretrained(MODEL)

    # text = "Good night 😊"
    # encoded_input = tokenizer(text, return_tensors='tf')
    # output = model(encoded_input)
    # scores = output[0][0].numpy()
    # scores = softmax(scores)
