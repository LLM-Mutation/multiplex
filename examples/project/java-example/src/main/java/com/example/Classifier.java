package com.example;

/** Classifies integers by sign. Target of the multiplex example run. */
public class Classifier {

    public String classify(int n) {
        if (n > 0) {
            return "positive";
        } else if (n < 0) {
            return "negative";
        }
        return "zero";
    }
}
