# Define a `ReturnException` class that's an exception.
class ReturnException(Exception):
    def __init__(self, value):
        super().__init__("Return")
        self.value = value
