from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json

@dataclass(frozen=True)
class GraphNode:
    node_id: str; node_type: str; attributes: dict

@dataclass(frozen=True)
class GraphEdge:
    edge_id: str; src: str; relation: str; dst: str; attributes: dict

class ProvenanceGraph:
    def __init__(self): self.nodes={}; self.edges={}
    def add_node(self,node):
        existing=self.nodes.get(node.node_id)
        if existing and existing != node: raise ValueError('NODE_ID_COLLISION')
        self.nodes[node.node_id]=node
    def add_edge(self,edge):
        if edge.src not in self.nodes or edge.dst not in self.nodes: raise ValueError('EDGE_ENDPOINT_MISSING')
        existing=self.edges.get(edge.edge_id)
        if existing and existing != edge: raise ValueError('EDGE_ID_COLLISION')
        self.edges[edge.edge_id]=edge
    def neighbors(self,node_id,relation=None):
        return [e.dst for e in self.edges.values() if e.src==node_id and (relation is None or e.relation==relation)]
    def digest(self):
        payload={'nodes':[asdict(x) for x in sorted(self.nodes.values(),key=lambda n:n.node_id)],'edges':[asdict(x) for x in sorted(self.edges.values(),key=lambda e:e.edge_id)]}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
