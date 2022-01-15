from pyppeteer.parser import Parser, Node, ShowNode, StatementNode
from pyppeteer.movie import Movie


class NodeVisitor:
    def visit(self, node: Node, parent: Node = None):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node, parent)

    def _generic_visit(self, node: Node, parent: Node = None):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class VideoGenerator(NodeVisitor):
    def __init__(self):
        self.symbols = {0: []}
        self.parser = Parser()
        self.movie = Movie()

    def render(self):
        self.movie.render_final_clip()

    def generate(self, root: Node):
        return self.visit(root)

    def visit_StatementNode(self, node: StatementNode, parent: Node = None):
        print("visit statement node", node)
        self.visit_ShowNode(node.node, node)
        return

    def visit_ShowNode(self, node: ShowNode, parent: StatementNode = None):
        print('visit show node', node)
        if node.args['duration']:
            duration = node.args['duration']
        else:
            duration = 1
        self.movie.movie_add_image_clip(node.args['file'], duration)
        return
