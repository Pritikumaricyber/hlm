
import numpy as np
from datetime import datetime

from backend.app.embeddings.embedder import generate_embedding
from backend.app.models.memory import Memory


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.
    """

    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) / denominator
    )


def calculate_retrieval_score(
    semantic_similarity: float,
    memory: Memory,
    emotion=None,
) -> float:
    """
    Calculate the final retrieval score.

    Retrieval is influenced by:

    - semantic similarity
    - memory strength
    - importance
    - confidence
    - emotional relevance
    - lifecycle status
    """

    emotion_bonus = 0.0

    if emotion is not None:
        emotion_bonus = (
            emotion.intensity * 0.04
            + abs(emotion.valence) * 0.03
            + emotion.arousal * 0.03
        )

    # BASE RETRIEVAL SCORE

    score = (
        semantic_similarity * 0.45
        + memory.strength * 0.25
        + memory.importance * 0.15
        + memory.confidence * 0.10
        + emotion_bonus
    )

    # MEMORY LIFECYCLE EFFECT

    if memory.status == "dormant":
        score *= 0.70

    elif memory.status == "forgotten":
        score *= 0.10

    return round(
        min(1.0, max(0.0, score)),
        4,
    )


def update_recall_state(
    memory: Memory,
) -> None:
    """
    Update the memory's recall-related signals.

    Every successful retrieval:

    - increases recall_count
    - updates last_recalled
    - strengthens the memory
    - can reactivate a dormant memory
    """

    # 1. INCREASE RECALL COUNT

    memory.recall_count += 1

    # 2. UPDATE LAST RECALL TIME

    memory.last_recalled = datetime.now()

    # 3. STRENGTHEN MEMORY

    recall_strength_bonus = 0.05

    memory.strength = min(
        1.0,
        memory.strength + recall_strength_bonus,
    )

    # 4. REACTIVATE DORMANT MEMORY

    if memory.status == "dormant":
        memory.status = "active"


def retrieve_memories(
    query,
    memories,
    emotion_store=None,
    top_k=5,
    query_embedding=None,
):
    """
    Retrieve the most relevant memories.

    Pipeline:

        Query
          ↓
        Embedding
          ↓
        Lifecycle filtering
          ↓
        Semantic similarity
          ↓
        Retrieval score
          ↓
        Ranking
          ↓
        Recall update
          ↓
        Retrieved memories

    Forgotten memories are excluded from normal retrieval.
    Dormant memories remain retrievable with a penalty.
    """

    # Reuse a supplied query embedding when available.
    # Otherwise, generate one for backward compatibility.

    if query_embedding is None:
        query_embedding = generate_embedding(query)

    results = []

    # 1. CALCULATE RETRIEVAL SCORES

    for memory in memories:

        # FORGOTTEN MEMORIES

        if memory.status == "forgotten":
            continue

        # GENERATE MEMORY EMBEDDING IF NECESSARY

        if memory.embedding is None:
            memory.embedding = generate_embedding(
                memory.content
            )

        # SEMANTIC SIMILARITY

        similarity = cosine_similarity(
            query_embedding,
            memory.embedding,
        )

        # EMOTIONAL RELEVANCE

        emotion = None

        if emotion_store is not None:
            emotions = emotion_store.get_by_memory(
                memory.id
            )

            if emotions:
                emotion = emotions[-1]

        # FINAL RETRIEVAL SCORE

        score = calculate_retrieval_score(
            similarity,
            memory,
            emotion,
        )

        print(
            f"[RETRIEVAL] {memory.content} "
            f"| similarity={similarity:.4f} "
            f"| score={score:.4f} "
            f"| status={memory.status}"
        )

        results.append(
            {
                "memory": memory,
                "semantic_similarity": round(
                    similarity,
                    4,
                ),
                "retrieval_score": score,
            }
        )

    # 2. SORT BY RETRIEVAL SCORE

    results.sort(
        key=lambda item: item["retrieval_score"],
        reverse=True,
    )

    # 3. RELEVANCE FILTER

    MIN_RELEVANCE_SCORE = 0.43

    relevant_results = [
        item
        for item in results
        if item["retrieval_score"] >= MIN_RELEVANCE_SCORE
    ]

    # 4. SELECT TOP MEMORIES

    retrieved_results = relevant_results[:top_k]

    # 5. UPDATE RECALL STATE

    for item in retrieved_results:
        memory = item["memory"]

        update_recall_state(memory)

    return retrieved_results
