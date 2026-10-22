from backend.app.graph.belief_graph import BeliefGraph
from backend.app.graph.graph_traversal import traverse_graph
from backend.app.models.memory import Memory
from backend.app.embeddings.embedder import generate_embedding
from backend.app.memory.retrieval_engine import cosine_similarity


def retrieve_related_memories(
    graph: BeliefGraph,
    memories: list[Memory],
    start_subject: str,
    max_depth: int = 2,
    query_embedding=None,
) -> list[dict]:
    """
    Retrieve memories connected through the relationship graph.

    The natural-language query is first matched against existing
    memory nodes using semantic similarity. The best matching
    memory becomes the starting point for graph traversal.

    This allows conversational queries such as:

        "What are my interests?"

    to activate graph relationships even though the exact query
    does not exist as a graph node.
    """

    # =========================================================
    # STEP 0 : FILTER RETRIEVABLE MEMORIES
    # =========================================================

    retrievable_memories = [
        memory
        for memory in memories
        if memory.status != "forgotten"
    ]

    if not retrievable_memories:
        return []

    # =========================================================
    # STEP 1 : FIND SEMANTICALLY RELEVANT GRAPH START NODE
    # =========================================================

    if query_embedding is None:
    query_embedding = generate_embedding(
        start_subject
    )

    best_memory = None
    best_similarity = 0.0

    for memory in retrievable_memories:

        if memory.embedding is None:
            memory.embedding = generate_embedding(
                memory.content
            )

        similarity = cosine_similarity(
            query_embedding,
            memory.embedding,
        )

        if similarity > best_similarity:

            best_similarity = similarity
            best_memory = memory

    if best_memory is None:
        return []

    # =========================================================
    # STEP 2 : TRAVERSE GRAPH FROM BEST MEMORY
    # =========================================================

    connected_subjects = traverse_graph(
        graph,
        best_memory.content,
        max_depth,
    )

    if not connected_subjects:
        return []

    # =========================================================
    # STEP 3 : FIND MEMORIES MATCHING GRAPH SUBJECTS
    # =========================================================

    connected_lookup = {
        subject.lower(): subject
        for subject in connected_subjects
    }

    related = []

    for memory in retrievable_memories:

        text = memory.content.lower()

        matched_subject = None

        for lowercase_subject in connected_lookup:

            if lowercase_subject in text:

                matched_subject = lowercase_subject
                break

        if matched_subject is None:
            continue

        # =====================================================
        # STEP 4 : FIND RELATIONSHIP STRENGTH
        # =====================================================

        relationship_strength = 0.0
        relationship_type = "related"

        for lowercase_node, original_node in connected_lookup.items():

            relationships = graph.get_relationships(
                original_node
            )

            for edge in relationships:

                target = edge["target"]
                target_lower = target.lower()

                if (
                    lowercase_node in text
                    or target_lower in text
                ):

                    strength = edge.get(
                        "strength",
                        0.0,
                    )

                    if strength > relationship_strength:

                        relationship_strength = strength

                        relationship_type = edge.get(
                            "relationship",
                            "related",
                        )

        # =====================================================
        # STEP 5 : ADD RESULT
        # =====================================================

        related.append(
            {
                "memory": memory,
                "relationship_strength": (
                    relationship_strength
                ),
                "relationship": relationship_type,
            }
        )

    return related
