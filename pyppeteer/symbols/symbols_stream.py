def load(input_stream, named_args) -> str:
    print("** Stream.load() called on ", input_stream, " with ", named_args)

    if named_args.get('raw'):
        return named_args['raw']
    else:
        if named_args.get('file'):
            with open(named_args['file'], 'r') as file:
                return file.read()

    return input_stream


def select(input_stream, named_args) -> str:
    print("** Stream.select() called on ", input_stream, " with ", named_args)

    if input_stream:
        if named_args.get('from'):
            from_statement = int(named_args['from'])
        else:
            from_statement = None

        if named_args.get('to'):
            to_statement = int(named_args['to'])
        else:
            to_statement = None

        if from_statement and to_statement:
            return input_stream[from_statement:to_statement]
        elif from_statement and not to_statement:
            return input_stream[from_statement:]
        elif to_statement and not from_statement:
            return input_stream[:to_statement]
        else:
            return input_stream


SYMBOLS = [("load", load),
           ("select", select)]
