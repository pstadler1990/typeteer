from sys import argv
from pyppeteer.parser import Parser
from pyppeteer.generator import VideoGenerator
from pyppeteer.exceptions import InvalidOrNoInputStream

if __name__ == '__main__':
    if len(argv) > 1:
        parser = Parser()

        statements = parser.parse(argv[1])
        generator = VideoGenerator()

        for statement in statements:
            generator.generate(statement)

        # Render and export the final movie
        generator.render()
    else:
        raise InvalidOrNoInputStream('Invalid input stream')
