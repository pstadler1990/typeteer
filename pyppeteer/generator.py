from pyppeteer.parser import Parser, Node, ShowNode, StatementNode


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

    def generate(self, root: Node):
        return self.visit(root)

    def visit_StatementNode(self, node: StatementNode, parent: Node = None):
        print("visit statement node", node)
        self.visit_ShowNode(node.node, node)
        return

    def visit_ShowNode(self, node: ShowNode, parent: StatementNode = None):
        print('visit show node', node)
        return
