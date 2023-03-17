# Hedonodon
## Prerequisites
Install the dependencies with `python -m pip install -r requirements.txt`.
Install SpaCys nlp model with `python -m spacy download en_core_web_lg`.
If the automatic download of the twitter-roberta-base-sentiment model and tokenizer fail, go to the model pages on hugging face (see models section) and download the to the respective folder (cardiffnlp/twitter-roberta-base-sentiment).

## Purpose
Hedonodon fetch toots from fedihum.org and calculates the sentiments, sentiment mean and word frequencies of each day, and creates fancy diagrams from the data.

## Motivation
This tool was created to understand how sentiment analyses and nlp methods works, so it may lacks of proper use of models etc...

## Models
It uses "germansentiment"](https://huggingface.co/oliverguhr/german-sentiment-bert) for german toots, []"twitter-roberta-base-sentiment"](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment) for
english toots, and ["vaderSentiment"](https://pypi.org/project/vaderSentiment/)  for other languages.
For the word counts I translate the toots to english with the GoogleTranslator from [deep_translater](https://pypi.org/project/deep-translator/) first and then use SpaCys nlp model ["en_core_web_lg"](https://spacy.io/models/en/) to calculate the word frequencies.

## Weaknesses
Since some moduls do not return sentiment compounds I have to use the nominal sentiment values (positive, neutral, negative) to calculate the mean of the day, which is statisticaly not okay (;-_-).