import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.schemas import (
    ChatRequest,
    ChatResponse,
    MemoryStateResponse,
    BehavioralProfileResponse,
)
from backend.app.llm.groq_provider import GroqProvider
from backend.app.memory.memory_manager import MemoryManager
from backend.app.llm.conversation_engine import ConversationEngine
from backend.app.memory.behavioral_profile_builder import (
    build_behavioral_profile,
)
from backend.app.storage.postgres.schema import create_tables

logger = logging.getLogger(__name__)

# Extra allowed browser origins can be supplied without editing code,
# e.g. CORS_ORIGINS="https://my-site.com,https://other.com"
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://human-memory-frontend.onrender.com",
]

EXTRA_CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]


app = FastAPI(
    title="Human-Like Memory API",
    description="API for the Human-Like-Memory Architecture for Intelligent Systems",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEFAULT_CORS_ORIGINS + EXTRA_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PostgreSQL schema before loading the memory system
create_tables()


# Initialize the AI system once when the API starts
llm = GroqProvider()
memory_manager = MemoryManager()

conversation_engine = ConversationEngine(
    llm=llm,
    memory_manager=memory_manager,
)


@app.get("/")
def root():
    return {
        "message": "Human-Like Memory API is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = conversation_engine.respond(
            user_id=request.user_id,
            message=request.message,
        )
    except Exception:
        # Log the full traceback on the server, but return a clean
        # error to the client instead of an unhandled crash.
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="The memory system could not process this message.",
        )

    return ChatResponse(
        response=response,
    )


@app.get(
    "/memory-state/{user_id}",
    response_model=MemoryStateResponse,
)
def memory_state(user_id: str):
    memories = [
        memory
        for memory in memory_manager.memory_store.get_all()
        if (
            memory.user_id == user_id
            and memory.status != "forgotten"
        )
    ]

    return MemoryStateResponse(
        user_id=user_id,
        memories=[
            {
                "id": memory.id,
                "content": memory.content,
                "memory_type": memory.memory_type,
                "status": memory.status,
                "importance": memory.importance,
                "confidence": memory.confidence,
                "strength": memory.strength,
            }
            for memory in memories
        ],
    )


@app.get(
    "/behavioral-profile/{user_id}",
    response_model=BehavioralProfileResponse,
)
def behavioral_profile(user_id: str):
    evidence = [
        item
        for item in memory_manager.behavioral_accumulator.get_all()
        if item.get("user_id") == user_id
    ]

    concepts = sorted(
        {
            item.get("concept")
            for item in evidence
            if item.get("concept")
        }
    )

    profiles = []

    for concept in concepts:
        concept_evidence = (
            memory_manager.behavioral_accumulator.get_by_concept(
                concept,
                user_id=user_id,
            )
        )

        built_profile = build_behavioral_profile(
            concept_evidence
        )

        profiles.append(
            {
                "concept": built_profile["concept"],
                "behavior": built_profile["behavior"],
                "direction": built_profile["direction"],
                "evidence_count": built_profile["evidence_count"],
                "consistency": built_profile["consistency"],
                "confidence": built_profile["confidence"],
            }
        )

    return BehavioralProfileResponse(
        user_id=user_id,
        profiles=profiles,
    )