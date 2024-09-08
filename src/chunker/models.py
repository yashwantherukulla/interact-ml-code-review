#models.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class ChunkType(Enum):
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMMEDIATE_CODE = "immediate_code"

@dataclass
class ChunkNode:
    id: str
    type: ChunkType
    # name: str
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

    def generate_summary(self):
        summary = {
            'total_nodes': len(self.nodes),
            'node_types': {chunk_type.value: 0 for chunk_type in ChunkType},
            'avg_children': sum(len(node.children) for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0,
            'max_depth': self._get_max_depth(),
            # 'most_related': max((len(node.related_chunks), node.name) for node in self.nodes.values()) if self.nodes else (0, None)
        }
        for node in self.nodes.values():
            summary['node_types'][node.type.value] += 1
        return summary

    def _get_max_depth(self):
        def depth(node):
            if not node.children:
                return 1
            return 1 + max(depth(child) for child in node.children)
        return depth(self.root) if self.root else 0

    def export_to_json(self, file_path: str):
        import json

        def node_to_dict(node):
            return {
                'id': node.id,
                'type': node.type.value,
                # 'name': node.name,
                'file_path': node.file_path,
                'start_line': node.start_line,
                'end_line': node.end_line,
                'children': [child.id for child in node.children],
                'related_chunks': [related.id for related in node.related_chunks],
                'imports': node.imports
            }

        graph_dict = {node_id: node_to_dict(node) for node_id, node in self.nodes.items()}

        with open(file_path, 'w') as f:
            json.dump(graph_dict, f, indent=2)