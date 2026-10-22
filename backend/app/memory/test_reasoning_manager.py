from backend.app.models.belief import Belief
from backend.app.models.memory import Memory

from backend.app.memory.reasoning_manager import (
    ReasoningManager,
)


manager = ReasoningManager()


belief = Belief(
    user_id="user_001",
    subject="Programming",
    belief="User prefers Python.",
    confidence=0.75,
)


supporting_memory = Memory(
    user_id="user_001",
    content="Python is my favorite language.",
    memory_type="fact",
    importance=0.9,
    confidence=0.9,
    strength=0.8,
)


conflicting_memory = Memory(
    user_id="user_001",
    content="I don't like Python.",
    memory_type="fact",
    importance=0.9,
    confidence=0.9,
    strength=0.9,
)


print("\n==============================")
print("REASONING MANAGER")
print("==============================\n")


print("INITIAL BELIEF")
print("Belief     :", belief.belief)
print("Confidence :", belief.confidence)
print("State      :", belief.state)


print("\n------------------------------")
print("SUPPORTING EVIDENCE")
print("------------------------------")

result = manager.process_reasoning(
    belief,
    supporting_memory,
)

print("Action     :", result["action"])
print("Confidence :", result["new_confidence"])
print("State      :", result["state"])


print("\n------------------------------")
print("CONFLICTING EVIDENCE")
print("------------------------------")

result = manager.process_reasoning(
    belief,
    conflicting_memory,
)

print("Action     :", result["action"])
print("Confidence :", result["new_confidence"])
print("State      :", result["state"])