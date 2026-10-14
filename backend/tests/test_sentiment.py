from app.intelligence.sentiment_analyzer import (
    BaselineSentimentAnalyzer,
    SentimentResult,
    get_sentiment_analyzer,
)


def test_positive_sentiment():
    analyzer = get_sentiment_analyzer()
    result = analyzer.analyze("The checkout process is amazing, super fast and truly flawless!")
    assert result.sentiment == "positive"
    assert result.confidence_score > 0.60
    assert result.compound_score > 0.20


def test_negative_sentiment():
    analyzer = get_sentiment_analyzer()
    result = analyzer.analyze("Terrible customer service, awful response time and broken app!")
    assert result.sentiment == "negative"
    assert result.confidence_score > 0.60
    assert result.compound_score < -0.20


def test_neutral_sentiment():
    analyzer = get_sentiment_analyzer()
    result = analyzer.analyze("The package was delivered on Tuesday afternoon.")
    assert result.sentiment == "neutral"
    assert 0.0 <= result.confidence_score <= 1.0


def test_negation_inversion():
    analyzer = get_sentiment_analyzer()
    # "good" is positive, but "not good" should be negative or neutral/low
    result_neg = analyzer.analyze("The overall experience was not good at all.")
    assert result_neg.sentiment == "negative"
    assert result_neg.compound_score < 0.0


def test_empty_or_whitespace_input():
    analyzer = get_sentiment_analyzer()
    res_empty = analyzer.analyze("")
    assert res_empty.sentiment == "neutral"
    assert res_empty.confidence_score == 0.50

    res_none = analyzer.analyze(None)
    assert res_none.sentiment == "neutral"
    assert res_none.confidence_score == 0.50


def test_output_schema_and_bounds():
    analyzer = get_sentiment_analyzer()
    result = analyzer.analyze("Decent software with reliable uptime.")
    assert isinstance(result, SentimentResult)
    assert result.sentiment in ["positive", "negative", "neutral"]
    assert 0.0 <= result.confidence_score <= 1.0
    assert -1.0 <= result.compound_score <= 1.0
    assert isinstance(result.details, dict)
