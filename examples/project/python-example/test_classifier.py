from classifier import classify


def test_classifies_positive():
    assert classify(5) == "positive"


def test_classifies_negative():
    assert classify(-5) == "negative"


def test_classifies_zero():
    assert classify(0) == "zero"
