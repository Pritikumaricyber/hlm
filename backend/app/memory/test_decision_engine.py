from backend.app.models.memory import Memory
from backend.app.memory.consolidation_engine import consolidate_memory
from backend.app.memory.decision_engine import make_memory_decision

old_memories = [

    Memory(
        user_id="user_001",
        content="I use Python for AI.",
        memory_type="fact",
        importance=0.8,
        confidence=0.9,
        strength=0.8,
        emotional_score=0.2,
    ),

    Memory(
        user_id="user_001",
        content="I visited Ranchi yesterday.",
        memory_type="event",
        importance=0.5,
        confidence=0.9,
        strength=0.5,
        emotional_score=0.1,
    ),
]

new_memory = Memory(
    user_id="user_001",
    content="Python is my favorite programming language.",
    memory_type="fact",
    importance=0.8,
    confidence=0.9,
    strength=0.8,
    emotional_score=0.2,
)

consolidation = consolidate_memory(
    new_memory,
    old_memories,
)

decision = make_memory_decision(
    consolidation
)

print("\nMEMORY DECISION\n")

print("Action       :", decision["action"])
print("Relationship :", decision["relationship"])
print(
    "Target       :",
    decision["target"].content if decision["target"] else None,
)
print(
    "Independence :",
    round(decision["independence"], 4)
    if decision["independence"] is not None
    else None,
)