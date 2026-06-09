import pytest
from app.sentiment.nlp import classify_sentiment_udf

def test_classify_sentiment_udf():
    assert classify_sentiment_udf("This is incredible and excellent!") == "positive"
    assert classify_sentiment_udf("What an unacceptable outage.") == "negative"
    assert classify_sentiment_udf("Just a regular post here.") == "neutral"
    assert classify_sentiment_udf("") == "neutral"
