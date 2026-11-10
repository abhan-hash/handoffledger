"""
HandoffLedger Graph Engine
Builds the entity relationship graph using NetworkX, computes dependency topology,
calculates in-degree centrality, and coordinates SPOK scoring.
"""

from typing import Dict, List, Optional, Sequence
import networkx as nx
from backend.app.models.schemas import (
    GraphNode,
    GraphEdge,
    GraphResponse,
    IngestedChunk,
    ClaimEntry,
    EntityType,
)
from backend.app.services.spok import evaluate_node_spok


class KnowledgeGraphEngine:
    def __init__(self, leaver_name: str = "Alice Maintainer"):
        self.leaver_name = leaver_name
        self.graph = nx.DiGraph()
        self.node_metadata: Dict[str, dict] = {}
        self.node_chunks: Dict[str, List[IngestedChunk]] = {}
        self.node_claims: Dict[str, List[ClaimEntry]] = {}

    def add_entity(
        self,
        node_id: str,
        name: str,
        entity_type: EntityType,
        metadata: Optional[dict] = None,
    ):
        """Adds or updates an entity node in the graph."""
        self.graph.add_node(node_id, name=name, entity_type=entity_type)
        self.node_metadata[node_id] = {
            "name": name,
            "entity_type": entity_type,
            **(metadata or {}),
        }
        if node_id not in self.node_chunks:
            self.node_chunks[node_id] = []
        if node_id not in self.node_claims:
            self.node_claims[node_id] = []

    def add_dependency(self, source_id: str, target_id: str, relation: str = "depends_on", weight: float = 1.0):
        """
        Adds a directed dependency edge: source_id -> target_id.
        In this convention: if service A depends on database B, an edge (A -> B) means B has in-degree from A.
        Therefore in_degree(target_id) counts how many entities depend on target_id.
        """
        if not self.graph.has_node(source_id):
            self.add_entity(source_id, source_id, EntityType.COMPONENT)
        if not self.graph.has_node(target_id):
            self.add_entity(target_id, target_id, EntityType.COMPONENT)
        self.graph.add_edge(source_id, target_id, relation=relation, weight=weight)

    def attach_chunk(self, node_id: str, chunk: IngestedChunk):
        if node_id not in self.node_chunks:
            self.node_chunks[node_id] = []
        self.node_chunks[node_id].append(chunk)

    def attach_claim(self, node_id: str, claim: ClaimEntry):
        if node_id not in self.node_claims:
            self.node_claims[node_id] = []
        self.node_claims[node_id].append(claim)

    def compute_all_spok(
        self,
        min_heatmap_in_degree: int = 2,
    ) -> List[GraphNode]:
        """
        Evaluates SPOK scores and interview priorities for all registered nodes.
        """
        scored_nodes: List[GraphNode] = []

        for node_id in self.graph.nodes:
            meta = self.node_metadata.get(node_id, {})
            name = meta.get("name", node_id)
            entity_type = meta.get("entity_type", EntityType.COMPONENT)
            chunks = self.node_chunks.get(node_id, [])
            claims = self.node_claims.get(node_id, [])

            in_degree = self.graph.in_degree(node_id)

            node_model = evaluate_node_spok(
                node_id=node_id,
                name=name,
                entity_type=entity_type,
                chunks=chunks,
                claims=claims,
                leaver_name=self.leaver_name,
                in_degree=in_degree,
                min_heatmap_in_degree=min_heatmap_in_degree,
            )
            scored_nodes.append(node_model)

        return scored_nodes

    def get_top_interview_nodes(self, limit: int = 10, exclude_peripheral: bool = True) -> List[GraphNode]:
        """
        Returns the top nodes ranked by Interview Priority Index.
        Excludes peripheral low-centrality nodes (in-degree < 2) per the specification.
        """
        all_nodes = self.compute_all_spok()
        candidates = [n for n in all_nodes if not n.is_filtered_from_heatmap] if exclude_peripheral else all_nodes
        if not candidates:
            candidates = all_nodes

        # Sort descending by priority, breaking ties with spok_score
        ranked = sorted(
            candidates,
            key=lambda n: (n.interview_priority, n.spok_score),
            reverse=True,
        )
        return ranked[:limit]

    def export_graph_response(self) -> GraphResponse:
        """Constructs API response model with all nodes and edges."""
        nodes = self.compute_all_spok()
        edges: List[GraphEdge] = []
        for u, v, data in self.graph.edges(data=True):
            edges.append(
                GraphEdge(
                    source_id=u,
                    target_id=v,
                    relation=data.get("relation", "depends_on"),
                    weight=data.get("weight", 1.0),
                )
            )

        unfiltered_count = sum(1 for n in nodes if not n.is_filtered_from_heatmap)
        return GraphResponse(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            unfiltered_heatmap_nodes=unfiltered_count,
        )
