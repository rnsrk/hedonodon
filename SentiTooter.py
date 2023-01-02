from math import sqrt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

class SentiTooter():
    """"""
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()


    def analyze(self, toot):
        compound = self.sia.polarity_scores(toot.content)['compound']
        if (compound > (1/3)):
            return ['positive', compound]
        elif (compound < (-1/3)):
            return ['negative', compound]
        else:
            return ['neutral', compound]

