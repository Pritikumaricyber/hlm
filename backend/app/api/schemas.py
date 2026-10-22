from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str


class MemoryStateItem(BaseModel):
    id: str
    content: str
    memory_type: str
    status: str
    importance: float
    confidence: float
    strength: float


class MemoryStateResponse(BaseModel):
    user_id: str
    memories: list[MemoryStateItem]

class BehavioralProfileItem(BaseModel):
    concept: str
    behavior: str | None
    direction: str | None
    evidence_count: int
    consistency: float
    confidence: float


class BehavioralProfileResponse(BaseModel):
    user_id: str
    profiles: list[BehavioralProfileItem]    