# Changelog

All notable changes to the **Human-Like-Memory AI Model** project are documented in this file.

---

## v2.1.1 - Stability and isolation fixes

### Fixed
- Per-user isolation: relationship building, graph rebuild and adaptive forgetting no longer touch other users' memories
- Memory extractor now accepts JSON wrapped in markdown code fences or extra text, and tolerates empty (`None`) model output
- Groq client returns an empty string instead of `None` when the model returns no content
- `/chat` returns a clean HTTP 500 and logs the traceback instead of crashing; empty `user_id`/`message` are rejected
- CORS origins can be extended through the `CORS_ORIGINS` environment variable
- Frontend header shows the real backend status (checking / ready / offline)
- Stale tests updated to the current API (`decision_engine`, `graph_retriever`, `reasoning_manager`, `reflection_engine`)

### Added
- `.env.example`, expanded `README.md`, `backend/__init__.py`

---

## v2.1.0 – Emotion-Aware Dream Replay

### Added
- Dream priority calculation for memory replay
- Emotion-aware memory replay during dream cycles
- Integration of `EmotionStore` with the Dream Engine
- Emotion-aware replay support in the Replay Engine
- Emotion-aware dream processing in `MemoryManager`
- Dream priority tests
- Emotion-aware replay tests

### Improved
- Dream replay now prioritizes memories using:
  - Memory strength
  - Memory importance
  - Emotional significance
  - Emotional intensity
- High-intensity emotional memories can receive higher replay priority
- Dream cycles now use emotional context when selecting memories for replay

---

## v2.0.0 – Emotion-Aware Memory Processing

### Added
- Emotion model
- Rule-based emotion detector
- Emotion store
- Emotion engine
- Emotion-aware retrieval
- Emotion integration into `MemoryManager`
- Emotion detector tests
- Emotion engine tests
- Emotion store tests
- Emotion model tests

### Improved
- Retrieval now considers emotional intensity, valence, and arousal
- Memory importance is dynamically adjusted based on detected emotions
- High-arousal memories decay more slowly
- Memory pipeline now performs emotion detection before retrieval

### Architecture

    Memory
        ↓
    Emotion Detection
        ↓
    Emotion Engine
        ↓
    Emotion Store
        ↓
    Retrieval
        ↓
    Consolidation
        ↓
    Decision
        ↓
    Knowledge
        ↓
    Reasoning
        ↓
    Reflection
        ↓
    Dream Learning
        ↓
    Adaptive Forgetting

---

## v1.9.0 – Adaptive Forgetting & Memory Lifecycle

**Date:** August 2026

### Added
- Retention Calculator
- Memory Decay Engine
- Forgetting Engine
- Forgetting Manager
- Adaptive forgetting integrated into Memory Manager
- Unit tests for forgetting modules

### Improved
- Memory lifecycle now supports:
  - Active memories
  - Dormant memories
  - Forgotten memories
- Human-like forgetting based on:
  - Importance
  - Emotional significance
  - Recall frequency
  - Memory age
  - Memory strength

---

## v1.8.0 – Hybrid Retrieval Pipeline

### Added
- Retrieval Pipeline
- Graph Retrieval
- Vector Retrieval Integration
- Duplicate retrieval filtering
- Retrieval ranking

### Improved
- Combined semantic search with graph-based search
- Hybrid retrieval now combines vector similarity and memory relationships

---

## v1.7.0 – Semantic Learning

### Added
- Pattern Miner
- Concept Clusterer
- Semantic Generalizer
- Generalization Engine
- Semantic Learning Pipeline

### Improved
- Automatic abstraction of repeated concepts into semantic beliefs
- Repeated memory patterns can be generalized into higher-level knowledge

---

## v1.6.0 – Cognitive Reasoning

### Added
- Belief Conflict Detector
- Confidence Calibrator
- Belief Reasoner
- Reasoning Manager

### Improved
- Dynamic belief confidence adjustment
- Cognitive reasoning support
- Belief-based reasoning over new memories

---

## v1.5.0 – Dream Learning

### Added
- Dream Engine
- Dream Replay
- Dream-Based Knowledge Learning

### Improved
- Offline learning through simulated dream cycles
- Strong memories can be replayed during dream processing

---

## v1.4.0 – Reflection System

### Added
- Reflection Engine
- Automatic belief generation

### Improved
- Long-term knowledge formation from memories
- Reflection can derive higher-level beliefs from stored memories

---

## v1.3.0 – Relationship Memory

### Added
- Relationship Detection
- Relationship Builder
- Relationship Store
- Belief Graph
- Graph Retriever

### Improved
- Connected memories through relationship graphs
- Graph-based memory relationships

---

## v1.2.0 – Knowledge Layer

### Added
- Belief Store
- Evidence Store
- History Store
- Knowledge Manager

### Improved
- Knowledge evolution from memories
- Evidence-based belief management
- Historical tracking of knowledge changes

---

## v1.1.0 – Memory Consolidation

### Added
- Consolidation Engine
- Decision Engine

### Improved
- Intelligent memory merging
- Memory conflict resolution
- Decisions based on relationships between memories

---

## v1.0.0 – Initial Human-Like Memory System

### Added
- Memory Model
- Memory Store
- Embedding Generation
- Retrieval Engine
- Basic Memory Manager
- Vector-based semantic retrieval

### Initial Architecture

    Memory
        ↓
    Embedding
        ↓
    Semantic Retrieval
        ↓
    Memory Manager