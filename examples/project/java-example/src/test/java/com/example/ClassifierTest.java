package com.example;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class ClassifierTest {

    private final Classifier classifier = new Classifier();

    @Test
    void classifiesPositive() {
        assertEquals("positive", classifier.classify(5));
    }

    @Test
    void classifiesNegative() {
        assertEquals("negative", classifier.classify(-5));
    }

    @Test
    void classifiesZero() {
        assertEquals("zero", classifier.classify(0));
    }
}
