class ScanWrongTokenException(Exception):
    pass


class ParseSyntaxException(Exception):
    pass


class InvalidOrNoInputStream(Exception):
    pass


class GenerateInvalidSequence(Exception):
    pass


class GenerateSymbolAlreadyExists(Exception):
    pass


class GenerateSymbolNotFound(Exception):
    pass


class GenerateSymbolMethodNotFound(Exception):
    pass
