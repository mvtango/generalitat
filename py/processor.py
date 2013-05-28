class GenericProcessor(object):

    def __init__(self):
      self.handlers = [] # List of pairs (regexp, handler)

    def register(self):
        """Declare a function as handler for a regular expression."""
        def gethandler(f):
            self.handlers.append(f)
            return f
        return gethandler

    def process(self, o):
        """Process a file line by line and execute all handlers by registered regular expressions"""
        for handler in self.handlers:
                o = handler(o)
        return o
