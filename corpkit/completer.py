class Completer(object):
    """
    Tab completion for interpreter
    """

    def __init__(self, words):
        self.words = words
        self.prefix = None

    def complete(self, prefix, index):
        """
        Add paths etc to this
        """
        if prefix != self.prefix:
            # we have a new prefix!
            # find all words that start with this prefix
            self.matching_words = [
                w for w in self.words if w.startswith(prefix)
                ]
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None
