from typing import Dict, List, Optional, NamedTuple
from enum import Enum
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChunkType(Enum):
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMMEDIATE_CODE = "immediate_code"

class ChunkNode(NamedTuple):
    id: str
    type: ChunkType
    file_path: str
    start_line: int
    end_line: int
    content: str
    children: List[str] = []
    imports: List[str] = []

class ChunkGraph:
    def __init__(self):
        self.nodes: Dict[str, ChunkNode] = {}
        self.edges: Dict[str, List[str]] = {}
        self.root_id: Optional[str] = None

    def add_node(self, node: ChunkNode) -> None:
        self.nodes[node.id] = node
        if node.type == ChunkType.FILE and self.root_id is None:
            self.root_id = node.id

    def add_edge(self, parent_id: str, child_id: str) -> None:
        if parent_id not in self.edges:
            self.edges[parent_id] = []
        self.edges[parent_id].append(child_id)

    def generate_summary(self) -> Dict:
        if not self.nodes:
            return {"error": "No nodes in the graph"}
        
        node_types = Counter(node.type for node in self.nodes.values())
        return {
            'total_nodes': len(self.nodes),
            'node_types': {chunk_type.value: node_types[chunk_type] for chunk_type in ChunkType},
            'avg_children': sum(len(children) for children in self.edges.values()) / len(self.nodes),
            'max_depth': self._get_max_depth(),
        }

    def _get_max_depth(self) -> int:
        def depth(node_id: str) -> int:
            return 1 + max((depth(child) for child in self.edges.get(node_id, [])), default=0)
        return depth(self.root_id) if self.root_id else 0

    def to_dict(self) -> Dict:
    #     id: str
    # type: ChunkType
    # file_path: str
    # start_line: int
    # end_line: int
    # content: str
    # children: List[str] = []
    # imports: List[str] = []
        return {
            node_id: {
                'id': node.id,
                'type': node.type.value,
                'file_path': node.file_path,
                'start_line': node.start_line,
                'end_line': node.end_line,
                'content': node.content,
                'children': self.edges.get(node_id, []),
                'imports': node.imports
            }
            for node_id, node in self.nodes.items()
        }