from pyppeteer.parser import Parser, Node, MethodCallNode, StatementNode
from pyppeteer.exceptions import GenerateInvalidSequence, GenerateSymbolAlreadyExists, GenerateSymbolNotFound, \
    GenerateSymbolMethodNotFound
from pyppeteer.symbols import symbols


class NodeVisitor:
    def visit(self, node: Node, parent: Node = None):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node, parent)

    def _generic_visit(self, node: Node, parent: Node = None):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class FilterLayerGenerator(NodeVisitor):
    def __init__(self):
        self.symbols = symbols.SYMBOLS
        self._cur_node_id = 0
        self._in_stream = ''
        self.parser = Parser()

    def render(self, dimensions: [tuple[int, int]]):
        """
        For each root_node_n node, create a VideoClip and combine them using concatenate clip
        :return:
        """
        pass

    def generate(self, root: Node):
        return self.visit(root)

    def visit_StatementNode(self, node: StatementNode, parent: Node = None):
        print("visit statement node", node)
        if type(node.node) == MethodCallNode:
            self.visit_MethodCallNode(node.node, node)
        else:
            raise GenerateInvalidSequence('Invalid node ' + node.node)

        self._cur_node_id += 1
        return

    def visit_MethodCallNode(self, node: MethodCallNode, parent: StatementNode = None):
        print('visit method call node', node)

        module_name = node.args.get('module', None)
        references_id = node.args.get('method', None)
        args = node.args.get('args', [])

        in_stream = self._in_stream

        if references_id:
            module_dict = self.symbols.get(module_name, None)
            if module_dict:
                try:
                    reference_obj = next(x for x in module_dict if x[0] == references_id)
                    # Call method name by reference_id
                    self._in_stream = reference_obj[1](in_stream, dict(args))
                except StopIteration:
                    raise GenerateSymbolMethodNotFound('Module ' + module_name + ' has no method ' + references_id)
            else:
                raise GenerateSymbolNotFound('Module ' + module_name + ' not found!')

        return
