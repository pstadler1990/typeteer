import argparse
from sys import argv
from pyppeteer.exceptions import InvalidOrNoInputStream
from pyppeteer.generator import VideoGenerator
from pyppeteer.parser import Parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pyppeteer - a simple DSL to create video dialogues')
    parser.add_argument('-f', '--file', help='Input file to parse', required=True)
    parser.add_argument('-d', '--dimensions', help='Video dimensions, e.g., 1920,1080')
    args = vars(parser.parse_args())

    if len(argv) > 1 and args['file']:
        parser = Parser()

        # Load file into string
        with open(args['file'], 'r') as file:
            input_stream = file.read()

            statements = parser.parse(input_stream)
            generator = VideoGenerator()

            try:
                for statement in statements:
                    generator.generate(statement)
            except TypeError as e:
                raise Exception(e)

            # Render and export the final movie
            dims = (1920, 1080)
            if args['dimensions']:
                dims = tuple(args['dimensions'].split(','))
            generator.render(dims)
    else:
        raise InvalidOrNoInputStream('Invalid input stream')
