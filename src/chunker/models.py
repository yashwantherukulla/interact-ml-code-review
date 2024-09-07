from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt

class ChunkType(Enum):
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"

@dataclass
class ChunkNode:
    id: str
    type: ChunkType
    name: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    ast_node: Dict[str, Any]
    parent: Optional['ChunkNode'] = None
    children: List['ChunkNode'] = field(default_factory=list)
    related_chunks: List['ChunkNode'] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)

@dataclass
class ChunkGraph:
    nodes: Dict[str, ChunkNode] = field(default_factory=dict)
    root: Optional[ChunkNode] = None

    def add_node(self, node: ChunkNode):
        self.nodes[node.id] = node
        if node.type == ChunkType.FILE and self.root is None:
            self.root = node

    def add_edge(self, parent_id: str, child_id: str):
        parent = self.nodes[parent_id]
        child = self.nodes[child_id]
        parent.children.append(child)
        child.parent = parent

    def add_related(self, node_id: str, related_id: str):
        node = self.nodes[node_id]
        related = self.nodes[related_id]
        if related not in node.related_chunks:
            node.related_chunks.append(related)

    def visualize_graph(self):
        G = nx.DiGraph()

        for node in self.nodes:
            G.add_node(node.id, lable=node.name, type=node.type)
            for child_id in self.edges.get(node.id, []):
                G.add_edge(node.id, child_id)
        
        pos = nx.spring_layout(G)
        labels = {node.id: node.name for node in self.nodes}
        node_colors = [self._get_node_color(node.type) for node in self.nodes]

        nx.draw(G, pos, labels=labels, node_colors=node_colors, with_labels=True, node_size=3000, font_size=10, font_color='white')
        plt.show()

    def _get_node_color(self, node_type: ChunkType) -> str:
        color_mapping = {
            ChunkType.FILE: 'blue',
            ChunkType.CLASS: 'green',
            ChunkType.FUNCTION: 'red',
        }
        return color_mapping.get(node_type, 'black')