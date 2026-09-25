from __future__ import annotations
from graphsag.graph.provenance import ProvenanceGraph,GraphNode,GraphEdge

def build_decision_graph(request, observations, decision):
    g=ProvenanceGraph()
    rid=f'request:{request.request_id}'; did=f'decision:{decision.decision_id}'
    g.add_node(GraphNode(rid,'request',{'principal_id':request.principal_id,'generation':request.generation,'action':request.action}))
    g.add_node(GraphNode(did,'decision',{'outcome':decision.outcome.value,'risk':decision.risk.value,'policy_version':decision.policy_version,'registry_version':decision.registry_version}))
    g.add_edge(GraphEdge(f'{rid}->{did}',rid,'RESULTS_IN',did,{}))
    for obs in observations:
        oid=f'evidence:{obs.digest()}'
        g.add_node(GraphNode(oid,'evidence',{'provider_id':obs.provider_id,'status':obs.status.value,'claim':obs.claim}))
        g.add_edge(GraphEdge(f'{oid}->{did}',oid,'SUPPORTS',did,{}))
    return g
