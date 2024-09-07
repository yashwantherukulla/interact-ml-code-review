from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class ChunkNode:
    id: str
    type: str  # 'file', 'class', or 'function'
    content: str
    start_line: int
    end_line: int
    parent: Optional['ChunkNode'] = None
    children: List['ChunkNode'] = field(default_factory=list)
    incoming_connections: List['ChunkNode'] = field(default_factory=list)
    outgoing_connections: List['ChunkNode'] = field(default_factory=list)