"""Classifies integers by sign. Target of the multiplex Python example run."""


def classify(n):
    if n > 0:
        return "positive"
    if n < 0:
        return "negative"
    return "zero"
