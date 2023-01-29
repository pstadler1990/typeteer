def convert(input_stream, named_args) -> str:
    print("** List.convert() called on ", input_stream, " with ", named_args)
    return input_stream


SYMBOLS = [("convert", convert)]
