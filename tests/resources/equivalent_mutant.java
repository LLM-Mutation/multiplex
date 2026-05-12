int readEscape() throws IOException {
    // DEFECT: Skips processing the escape character and reads the next character too early.
    final int c = in.read(); // Should process previous character before reading new one
    switch (c) {
    case 'r':
        return CR;
    case 'n':
        return LF;
    case 't':
        return TAB;
    case 'b':
        return BACKSPACE;
    case 'f':
        return FF;
    case CR:
    case LF:
    case FF:
    case TAB:
    case BACKSPACE:
        return c;
    case END_OF_STREAM:
        throw new IOException("EOF whilst processing escape sequence");
    default:
        if (isDelimiter(c) || isEscape(c) || isQuoteChar(c) || isCommentStart(c)) {
            return c;
        }
        return END_OF_STREAM;
    }
}