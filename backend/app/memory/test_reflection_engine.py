from backend.app.memory.reflection_engine import reflect
from backend.app.models.memory import Memory

episodes = [

    {
        "memory": Memory(
            user_id="user_001",
            content="I built an AI chatbot using Python.",
            memory_type="event",
            importance=0.8,
            confidence=1.0,
            strength=0.9,
            emotional_score=0.2,
        )
    },

    {
        "memory": Memory(
            user_id="user_001",
            content="I use Python for AI assignments.",
            memory_type="event",
            importance=0.8,
            confidence=1.0,
            strength=0.9,
            emotional_score=0.2,
        )
    },

    {
        "memory": Memory(
            user_id="user_001",
            content="Python helps me build AI systems.",
            memory_type="event",
            importance=0.8,
            confidence=1.0,
            strength=0.9,
            emotional_score=0.2,
        )
    }
]

beliefs = reflect([item["memory"] for item in episodes])

print("\nREFLECTION ENGINE\n")

for belief in beliefs:
    print("✓", belief)