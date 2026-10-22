from backend.app.graph.belief_graph import BeliefGraph
from backend.app.graph.graph_retriever import retrieve_related_memories
from backend.app.models.memory import Memory


graph = BeliefGraph()

graph.add_relationship(
    "Python",
    "AI",
    "related",
    0.9
)

graph.add_relationship(
    "Python",
    "FastAPI",
    "used_for",
    0.95
)

graph.add_relationship(
    "AI",
    "Machine Learning",
    "includes",
    0.85
)

graph.add_relationship(
    "Machine Learning",
    "Deep Learning",
    "includes",
    0.8
)


memories = [

    Memory(
        user_id="user1",
        content="I use Python every day."
    ),

    Memory(
        user_id="user1",
        content="I enjoy building AI applications."
    ),

    Memory(
        user_id="user1",
        content="FastAPI makes backend development easier."
    ),

    Memory(
        user_id="user1",
        content="Machine Learning is fascinating."
    ),

    Memory(
        user_id="user1",
        content="I watched a movie yesterday."
    )
]


related = retrieve_related_memories(
    graph=graph,
    memories=memories,
    start_subject="Python",
    max_depth=2
)

print("\n==============================")
print("GRAPH RETRIEVAL")
print("==============================")

for item in related:
    print(item["memory"].content)