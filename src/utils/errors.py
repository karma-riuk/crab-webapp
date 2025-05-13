class InvalidJsonFormatError(Exception):
    def __init__(self, message='JSON must be an object mapping strings to strings'):
        super().__init__(message)
        self.name = 'InvalidJsonFormatError'
