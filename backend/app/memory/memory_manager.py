from backend.app.models.memory import Memory

from backend.app.memory.consolidation_engine import (
    consolidate_memory,
)
from backend.app.memory.decision_engine import (
    make_memory_decision,
)
from backend.app.memory.reflection_engine import (
    reflect,
)
from backend.app.memory.belief_consolidator import (
    BeliefConsolidator,
)

from backend.app.storage.postgres.memory_store import (
    PostgresMemoryStore,
)

from backend.app.storage.postgres.belief_store import (
    PostgresBeliefStore,
)

from backend.app.storage.postgres.evidence_store import (
    PostgresEvidenceStore,
)

from backend.app.storage.postgres.history_store import (
    PostgresHistoryStore,
)

from backend.app.storage.relationship_store import (
    RelationshipStore,
)

from backend.app.storage.emotion_store import (
    EmotionStore,
)

from backend.app.knowledge.knowledge_manager import (
    KnowledgeManager,
)

from backend.app.memory.relationship_engine import (
    detect_relationship,
)

from backend.app.memory.relationship_builder import (
    build_relationship,
)

from backend.app.graph.belief_graph import (
    BeliefGraph,
)

from backend.app.memory.dream_engine import (
    run_dream_cycle,
)

from backend.app.memory.forgetting_manager import (
    ForgettingManager,
)

from backend.app.memory.emotion_detector import (
    detect_emotion,
)

from backend.app.memory.emotion_engine import (
    apply_emotion,
)

from backend.app.memory.retrieval_pipeline import (
    run_retrieval_pipeline,
)
from backend.app.memory.behavioral_evidence_accumulator import (
    BehavioralEvidenceAccumulator,
)
from backend.app.memory.behavioral_inference_builder import (
    build_behavioral_inference,
)
from backend.app.memory.behavioral_profile_builder import (
    build_behavioral_profile,
)
from backend.app.memory.behavioral_profile_reconciliation import (
    reconcile_behavioral_profile,
)

class MemoryManager:
    """
    Main controller of the Human-Like Memory system.

    Coordinates the complete memory pipeline:

    1. Emotion detection
    2. Hybrid memory retrieval
    3. Memory consolidation
    4. Memory decision
    5. Memory storage
    6. Relationship construction
    7. Knowledge / belief processing
    8. Reflection
    9. Dream cycle
    10. Adaptive forgetting
    """

    def __init__(self):

        # =====================================================
        # STORES
        # =====================================================

        self.memory_store = PostgresMemoryStore()

        self.belief_store = PostgresBeliefStore()

        self.belief_consolidator = BeliefConsolidator(
            belief_store=self.belief_store,
            similarity_threshold=0.70,
        )

        self.evidence_store = PostgresEvidenceStore()

        self.history_store = PostgresHistoryStore()

        self.relationship_store = RelationshipStore()

        self.emotion_store = EmotionStore()

        # =====================================================
        # BELIEF GRAPH
        # =====================================================

        self.graph = BeliefGraph()

        # =====================================================
        # KNOWLEDGE MANAGER
        # =====================================================

        self.knowledge_manager = KnowledgeManager(
            belief_store=self.belief_store,
            evidence_store=self.evidence_store,
            history_store=self.history_store,
            belief_consolidator=self.belief_consolidator,
        )
        # =====================================================
        # BEHAVIORAL MEMORY
        # =====================================================

        self.behavioral_accumulator = BehavioralEvidenceAccumulator()

        self.rebuild_behavioral_memory()

        # =====================================================
        # FORGETTING
        # =====================================================

        self.forgetting_manager = ForgettingManager()

        # =====================================================
        # REBUILD GRAPH FROM EXISTING DATABASE MEMORIES
        # =====================================================

        self.rebuild_memory_graph()

    def rebuild_behavioral_memory(self):
        """
        Rebuild behavioral observations from persistent memories.
        PostgreSQL memories remain the source of truth.
        The behavioral accumulator is reconstructed at startup.
        """

        memories = self.memory_store.get_all()

        rebuilt_count = 0

        for memory in memories:
            if memory.status == "forgotten":
                continue

            behavioral_inference = build_behavioral_inference(
                memory.content
            )
            if behavioral_inference is None:
                continue
            behavioral_inference["user_id"] = memory.user_id
            added = self.behavioral_accumulator.add(
                behavioral_inference
            )
            if added:
                rebuilt_count += 1
        print(
            f"Behavioral memory rebuilt: "
            f"{rebuilt_count} observations"
        )    



    # =========================================================
    # BUILD GRAPH FROM EXISTING MEMORIES
    # =========================================================

    def rebuild_memory_graph(self) -> None:
        """
        Build the relationship graph from memories already
        stored in PostgreSQL.
        """

        memories = [
            memory
            for memory in self.memory_store.get_all()
            if memory.status != "forgotten"
        ]

        for index, memory_a in enumerate(memories):

            for memory_b in memories[index + 1:]:

                # Never link memories that belong to different users.
                if memory_a.user_id != memory_b.user_id:
                    continue

                relationship_type, strength = detect_relationship(
                    memory_a,
                    memory_b,
                )

                if relationship_type != "related":
                    continue

                # A -> B
                self.graph.add_relationship(
                    memory_a.content,
                    memory_b.content,
                    relationship_type,
                    strength,
                )

                # B -> A
                self.graph.add_relationship(
                    memory_b.content,
                    memory_a.content,
                    relationship_type,
                    strength,
                )

    def retrieve_relevant_memories(
            self,
            user_id: str,
            query: str,
            top_k: int = 5,
            ):
        """
        Retrieve memories relevant to the current conversation.
        Uses the existing hybrid retrieval pipeline:
        vector retrieval + relationship graph retrieval."""
        memories = [
            memory
            for memory in self.memory_store.get_all()
            if (
                memory.user_id == user_id
                and memory.status != "forgotten"
            )
        ]
        retrieved = run_retrieval_pipeline(
            query=query,
            memories=memories,
            graph=self.graph,
            )
        return [
            item["memory"]
            for item in retrieved[:top_k]
            ]            

    # =========================================================
    # PROCESS MEMORY
    # =========================================================
    
    def process_memory(
        self,
        new_memory: Memory,
    ):

        # =====================================================
        # STEP 1 : EMOTION DETECTION
        # =====================================================

        emotion = detect_emotion(
            user_id=new_memory.user_id,
            memory_id=new_memory.id,
            text=new_memory.content,
        )

        self.emotion_store.add(
            emotion
        )

        new_memory = apply_emotion(
            new_memory,
            emotion,
        )

        print(
            f"Emotion: {emotion.emotion}"
        )

        print(
            f"Intensity: {emotion.intensity}"
        )

        print(
            f"Valence: {emotion.valence}"
        )

        print(
            f"Arousal: {emotion.arousal}"
        )

        # =====================================================
        # STEP 2 : HYBRID RETRIEVAL
        # =====================================================

        available_memories = [
            memory
            for memory in self.memory_store.get_all()
            if (
                memory.user_id == new_memory.user_id
                and memory.status != "forgotten"
           )
        ]

        retrieved = run_retrieval_pipeline(
            query=new_memory.content,
            memories=available_memories,
            graph=self.graph,
        )

        # =====================================================
        # STEP 3 : MEMORY CONSOLIDATION
        # =====================================================

        consolidation = consolidate_memory(
            new_memory,
            [
                item["memory"]
                for item in retrieved
            ],
        )

        # =====================================================
        # STEP 4 : MEMORY DECISION
        # =====================================================

        decision = make_memory_decision(
            consolidation
        )

        # =====================================================
        # STEP 5 : APPLY MEMORY DECISION
        # =====================================================

        action = decision["action"]

        behavioral_inference = build_behavioral_inference(
            new_memory.content
        )
        if behavioral_inference is not None:
            behavioral_inference["user_id"] = new_memory.user_id
            added = self.behavioral_accumulator.add(
                behavioral_inference
    )
            if added:
                print(
                    f"Behavioral observation detected: "
                    f"{behavioral_inference['inference']}"
                )
                behavioral_evidence = (
                    self.behavioral_accumulator.get_by_concept(
                        behavioral_inference["concept"],
                        user_id=new_memory.user_id,
                    )
                )
                behavioral_profile = build_behavioral_profile(
                    behavioral_evidence
                )
                print(
                    f"Behavioral profile updated: "
                    f"{behavioral_profile}"
                )
            else:
                print(
                    "Duplicate behavioral observation ignored."
                )

                     # =====================================================
        # STEP 5.5 : PERSIST EXPLICIT PREFERENCE CHANGE
        # =====================================================

        if (
            behavioral_inference is not None
            and behavioral_inference.get("preference_change")
            is not None
        ):
            preference_change = (
                behavioral_inference["preference_change"]
            )

            new_preference = (
                preference_change["new_preference"]
            )

            superseded_concept = (
                preference_change["superseded_preference"]
            )

            existing_memories = (
                self.memory_store.get_all()
            )

            for existing_memory in existing_memories:

                if (
                    existing_memory.user_id
                    == new_memory.user_id
                    and existing_memory.memory_type
                    == "preference"
                    and superseded_concept
                    in existing_memory.content.lower()
                    and new_preference
                    not in existing_memory.content.lower()
                ):
                    existing_memory.status = "dormant"

                    self.memory_store.update(
                        existing_memory
                    )

                    print(
                        f"Preference superseded: "
                        f"{existing_memory.content}"
                    )

            # Reactivate an existing exact preference memory
            # instead of creating a duplicate.
            matching_memory = None

            for existing_memory in existing_memories:

                if (
                    existing_memory.user_id
                    == new_memory.user_id
                    and existing_memory.content.lower()
                    == new_memory.content.lower()
                ):
                    matching_memory = existing_memory
                    break

            if matching_memory is not None:

                matching_memory.status = "active"

                self.memory_store.update(
                    matching_memory
                )

                print(
                    f"Preference reactivated: "
                    f"{matching_memory.content}"
                )

                action = "ignore"

            else:

                new_memory.status = "active"
                action = "store_new"

        if action == "store_new":
            print(
                f"BEFORE STORE: "
                f"{new_memory.content} | "
                f"status={new_memory.status} | "
                f"id={new_memory.id}"
         )
            self.memory_store.add(
                new_memory
                )
            stored_memory = self.memory_store.get_by_id(
                new_memory.id
            )
            print(
                f"AFTER STORE: "
                f"{stored_memory.content if stored_memory else 'NOT FOUND'} | "
                f"status="
                f"{stored_memory.status if stored_memory else 'N/A'} | "
                f"id={new_memory.id}"
            )
        elif action == "ignore":
            print(
                f"Duplicate memory ignored: "
                f"{new_memory.content}"
            )
            return {
                "retrieved": retrieved,
                "consolidation": consolidation,
                "decision": decision,
            }

        elif action == "update_memory":
            target_memory = decision["target"]
            if target_memory is not None:
                print(
                    f"Memory refinement detected: "
                    f"{new_memory.content}"
                    )

        # Preserve the original memory identity.
        # We are refining the existing memory rather
        # than creating a completely new memory.
                target_memory.content = new_memory.content

        # Update the memory type if the new information
        # provides a more specific classification.
                target_memory.memory_type = (
                    new_memory.memory_type
                    )

        # Keep the stronger importance value.
                target_memory.importance = max(
                    target_memory.importance,
                    new_memory.importance,
                    )

        # Keep the stronger confidence value.
                target_memory.confidence = max(
                    target_memory.confidence,
                    new_memory.confidence,
                    )

        # Preserve the stronger emotional signal.
                target_memory.emotional_score = max(
                    target_memory.emotional_score,
                    new_memory.emotional_score,
                    )

        # Refinement means the memory has been accessed
        # and updated, so strengthen it slightly.
                target_memory.strength = min(
                    1.0,
                    max(
                        target_memory.strength,
                        new_memory.strength,
                    ),
                )

        # The refined memory is active again.
                target_memory.status = "active"

        # The old embedding no longer represents the
        # memory content, so regenerate it.
                from backend.app.embeddings.embedder import (
                    generate_embedding,
                    )

                target_memory.embedding = generate_embedding(
                    target_memory.content
                    ).tolist()

        # Save the refined memory.
                self.memory_store.update(
                    target_memory
                    )
                print(
                    f"Memory updated: "
                    f"{target_memory.content}"
                    )

        elif action == "strengthen_belief":

            print(
                f"Supporting memory detected: "
                f"{new_memory.content}"
            )

        elif action == "revise_belief":

            print(
                f"Contradicting memory detected: "
                f"{new_memory.content}"
            )
        
        # =====================================================
        # STEP 6 : BUILD MEMORY RELATIONSHIPS
        # =====================================================

        for existing_memory in self.memory_store.get_all():

            if existing_memory.id == new_memory.id:
                continue

            # Memories of other users must never be linked together.
            if existing_memory.user_id != new_memory.user_id:
                continue

            if existing_memory.status == "forgotten":
                continue

            relationship_type, strength = detect_relationship(
                new_memory,
                existing_memory,
            )

            if relationship_type != "related":
                continue

            relationship = build_relationship(
                new_memory,
                existing_memory,
                relationship_type,
                strength,
            )

            self.relationship_store.add(
                relationship
            )

            self.graph.add_relationship(
                new_memory.content,
                existing_memory.content,
                relationship_type,
                strength,
            )

            self.graph.add_relationship(
                existing_memory.content,
                new_memory.content,
                relationship_type,
                strength,
            )

            print(
                f"Relationship created "
                f"({relationship_type}, "
                f"{strength:.2f})"
            )

        # =====================================================
        # STEP 7 : KNOWLEDGE PROCESSING
        # =====================================================

        knowledge_result = self.knowledge_manager.process_knowledge(
            new_memory,
            decision,
            )
                # =====================================================
        # STEP 7.5 : BEHAVIORAL PROFILE RECONCILIATION
        # =====================================================

        if behavioral_inference is not None:

            behavioral_evidence = (
                self.behavioral_accumulator.get_by_concept(
                    behavioral_inference["concept"],
                    user_id=new_memory.user_id,
                )
            )

            behavioral_profile = build_behavioral_profile(
                behavioral_evidence
            )

            belief = knowledge_result.get("belief")

            if belief is not None:

                reconciled_belief = (
                    reconcile_behavioral_profile(
                        belief,
                        behavioral_profile,
                    )
                )

                self.belief_store.update(
                    reconciled_belief
                )

                print(
                    f"Behavioral belief reconciliation: "
                    f"confidence="
                    f"{reconciled_belief.confidence:.4f}"
                )

        # =====================================================
        # STEP 8 : REFLECTION
        # =====================================================

        new_beliefs = reflect(
            self.memory_store.get_all(),
            user_id=new_memory.user_id,
        )

        for belief in new_beliefs:
            existing_belief, similarity = (
                self.belief_store.find_similar_belief(
                belief.belief,
                belief.user_id,
                threshold=0.70,
            )
        )
            if existing_belief is not None:
                if existing_belief.state in {
                    "contested",
                    "superseded",
                    }:
                    print(
                        f"Reflection skipped reinforcement of "
                        f"{existing_belief.state} belief: "
                        f"{existing_belief.belief}"
                    )
                    continue
                result = self.belief_consolidator.consolidate(
                    belief
                )
                if result["action"] == "created":
                    print(
                        "Reflection learned:",
                        result["belief"].belief,
                      )
                else:
                    print(
                        f"Reflection reinforced existing belief: "
                        f"{result['belief'].belief} "
                        f"(similarity="
                        f"{result['similarity']:.4f})"
                    )

        # =====================================================
        # STEP 9 : DREAM CYCLE
        # =====================================================

        if self.memory_store.count() >= 5:

            dream_beliefs = run_dream_cycle(
                self.memory_store.get_all(),
                user_id=new_memory.user_id,
                emotion_store=self.emotion_store,
            )

            self.knowledge_manager.store_dream_beliefs(
                dream_beliefs
            )
        # =====================================================
        # STEP 10 : ADAPTIVE FORGETTING
        # =====================================================

        for memory in self.memory_store.get_all():

            # Only decay/forget the memories of the user who is
            # currently talking. Other users' memories must not
            # change because someone else sent a message.
            if memory.user_id != new_memory.user_id:
                continue

            # Protect the newly learned memory from being
            # forgotten in the same processing cycle.
            if memory.id == new_memory.id:
                continue

            updated = self.forgetting_manager.process_memory(
                memory
            )

            self.memory_store.update(
                updated
            )

            print(
                f"Forgetting: "
                f"{updated.content} "
                f"-> {updated.status}"
            )

        # =====================================================
        # RETURN PIPELINE RESULT
        # =====================================================

        return {
            "retrieved": retrieved,
            "consolidation": consolidation,
            "decision": decision,
        }

        