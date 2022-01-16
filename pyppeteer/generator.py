from pyppeteer.parser import Parser, Node, ShowNode, StatementNode
from pyppeteer.movie import Movie, movie_add_image_clip
from pyppeteer.exceptions import GenerateInvalidSequence
from anytree import Node as TreeNode, findall, RenderTree, PreOrderIter


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
        self._cur_node_id = 0
        self.tree: TreeNode = TreeNode("Root", start_time=9999, duration=9999)
        self.parser = Parser()
        self.movie = Movie()

    def render(self):
        """
        For each root_node_n node, create a VideoClip and combine them using concatenate clip
        :return:
        """
        print(RenderTree(self.tree))
        root_nodes = findall(self.tree, filter_=lambda n: not n.is_root and not n.is_leaf)

        for root in root_nodes:
            root_clips = []
            for child in root.children:
                file = child.obj.args['file']
                duration = child.duration
                start_time = child.start_time
                position = child.obj.args.get('coordinates', (0, 0))
                movie_add_image_clip(file, duration, start_time, root_clips, position)
            # Finally, create composite video clip from root_clips
            self.movie.movie_create_composite_clip(root_clips)

        # alle Zeitmarker enthält; am Ende des gesamten VideoGenerators wird dann diese Liste abgearbeitet und daraus
        # die Clips erstellt (composite or concatenate)
        # Der Playback-Tree erzeugt einen Baum, bei dem jeder Clip der ein "after" keyword hat, als Child des Parents ist
        # Für jeden Eintrag kann dann genau der time mark vorberechnet werden
        # Node('/Root', duration=9999, start_time=9999)
        # ├── Node('/Root/root_node_0', duration=10.0, start_time=0.0)
        # │   ├── Node('/Root/root_node_0/show_node_0', duration=10.0, start_time=0.0)
        # │   ├── Node('/Root/root_node_0/show_node_1', duration=2.0, start_time=0.0)
        # │   └── Node('/Root/root_node_0/show_node_2', duration=3.0, start_time=1.0)
        # └── Node('/Root/root_node_3', duration=5.0, start_time=11.0)
        # └── Node('/Root/root_node_3/show_node_3', duration=5.0, start_time=11.0)
        self.movie.render_final_clip()

    def generate(self, root: Node):
        return self.visit(root)

    def visit_StatementNode(self, node: StatementNode, parent: Node = None):
        print("visit statement node", node)
        if type(node.node) == ShowNode:
            self.visit_ShowNode(node.node, node)
        else:
            raise GenerateInvalidSequence('Invalid node ' + node.node)

        self._cur_node_id += 1
        return

    def visit_ShowNode(self, node: ShowNode, parent: StatementNode = None):
        print('visit show node', node)
        start_time = parent.time_mark
        duration = node.args.get('duration', 1)  # 1s is default duration

        # Look through root nodes if entry exists, where this nodes start time and duration fits
        nodes = findall(self.tree, filter_=lambda n: start_time < n.start_time + n.duration and not n.is_leaf and not n.is_root)
        if not len(nodes):
            # If none, add a new root branch and this add this node as a child
            this_root_node = TreeNode('root_node_%d' % self._cur_node_id, parent=self.tree, start_time=start_time, duration=duration)
            TreeNode('show_node_%d' % self._cur_node_id, parent=this_root_node, start_time=start_time, duration=duration, obj=node)
        else:
            # If any, append this as a child of this root node
            TreeNode('show_node_%d' % self._cur_node_id, parent=nodes[0], start_time=start_time, duration=duration, obj=node)
        return
