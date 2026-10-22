import json
import re

from backend.app.llm.llm_interface import LLMInterface


class MemoryExtractor:
    """
    Extracts potentially durable user memories
    from conversational messages.

    The extractor can identify multiple durable memories
    from a single user message.

    It decides only:
        - whether something should be remembered
        - what memories should be created
        - the type of each memory

    Memory strength, importance, confidence, emotion,
    consolidation, relationships, beliefs, and forgetting
    remain the responsibility of the memory system.
    """

    def __init__(
        self,
        llm: LLMInterface,
    ):
        self.llm = llm

    def extract(
        self,
        message: str,
    ) -> dict:
        """
        Extract one or more durable memories from
        the user's message.
        """

        system_prompt = """
You are a memory extraction component for a
human-like memory architecture.

Your task is to determine whether the user's message
contains durable information about the user that may
be useful in future conversations.

Remember information such as:

- personal facts
- preferences
- interests
- goals
- skills
- ongoing activities
- important experiences
- long-term plans

IMPORTANT:

A single user message may contain MORE THAN ONE
durable piece of information.

You MUST extract all clearly identifiable durable
memories rather than combining unrelated pieces into
one memory.

For example:

"I am learning deep learning because I want to work in AI."

contains TWO pieces of durable information:

1. The user is learning deep learning.
2. The user wants to work in AI.

Return them as two separate memories.

Another example:

"I use Python for AI projects and I want to become
an AI engineer."

contains:

1. The user uses Python for AI projects.
2. The user wants to become an AI engineer.

Do NOT lose the reason, motivation, goal, preference,
or relationship expressed in the user's statement.

However, do NOT invent relationships that were not
stated or strongly implied.

--------------------------------------------------
DO NOT REMEMBER
--------------------------------------------------

Do NOT remember:

- ordinary questions
- greetings
- temporary requests
- general facts that are not about the user
- assistant instructions
- meaningless conversation
- information clearly unrelated to future conversations
- questions asking about information already stored
- questions asking what the assistant remembers
- requests to recall previous information

--------------------------------------------------
IMPORTANT QUESTION RULE
--------------------------------------------------

If the user's message is primarily asking about
previously stored information, it is a retrieval
request, NOT a new memory.

Examples:

"What am I currently learning?"
"What are my interests?"
"What do you know about me?"
"Do you remember that I use Python?"
"What did I tell you about my project?"
"What am I working on?"
"What are my goals?"
"What am I currently learning and why?"

For these messages return:

{
  "should_remember": false,
  "memories": []
}

Do NOT infer memories from the question.

For example:

"What am I currently learning?"

must NOT create:

"The user is currently learning something."

--------------------------------------------------
MEMORY TYPES
--------------------------------------------------

Each memory must have exactly one of these types:

- fact
- preference
- interest
- goal
- event
- skill

Use:

skill:
For abilities, learning activities, technologies,
subjects being learned, or skills being developed.

goal:
For future objectives, ambitions, career goals,
plans, or motivations.

interest:
For things the user enjoys or is interested in.

preference:
For likes, dislikes, choices, or favored options.

event:
For meaningful personal experiences or events.

fact:
For durable personal information that does not
fit the other categories.

--------------------------------------------------
IMPORTANT EXTRACTION RULE
--------------------------------------------------

Preserve the actual meaning of the user's statement.

For example:

"I am learning deep learning because I want to work in AI."

should produce:

{
  "should_remember": true,
  "memories": [
    {
      "memory": "The user is learning deep learning.",
      "memory_type": "skill"
    },
    {
      "memory": "The user wants to work in AI.",
      "memory_type": "goal"
    }
  ]
}

Do NOT return only:

"The user is learning deep learning."

because that loses the user's goal.

Another example:

"I enjoy Python because I use it for my AI projects."

should preserve both durable facts:

- The user enjoys Python.
- The user uses Python for AI projects.

Another example:

"I want to become a software engineer and I am
currently learning React."

should produce:

- The user wants to become a software engineer. → goal
- The user is learning React. → skill

--------------------------------------------------
NO INVENTION
--------------------------------------------------

Never create information that is not explicitly stated
or strongly implied.

Do not infer:

- age
- location
- personality
- career
- preferences
- goals
- emotions
- relationships

unless supported by the user's message.

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON.

The JSON must have exactly these top-level fields:

{
  "should_remember": true or false,
  "memories": [
    {
      "memory": "short factual statement about the user",
      "memory_type": "fact | preference | interest | goal | event | skill"
    }
  ]
}

If nothing should be remembered:

{
  "should_remember": false,
  "memories": []
}

Do not include markdown.
Do not include explanations.
Do not include additional fields.
"""

        response = self.llm.generate(
            prompt=message,
            system_prompt=system_prompt,
        )

        return self._parse_response(response)

    @staticmethod
    def _load_json(
        response,
    ):
        """
        Leniently load a JSON object from an LLM response.

        LLMs frequently wrap JSON in markdown code fences or add a
        short sentence before/after it, even when told not to.
        Returns None when no JSON object can be recovered.
        """

        if not isinstance(response, str):
            return None

        text = response.strip()

        # ```json ... ``` or ``` ... ```
        fenced = re.match(
            r"^```(?:json)?\s*(.*?)\s*```$",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )

        if fenced:
            text = fenced.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Fall back to the first {...} block in the text.
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None

        return None

    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict:
        """
        Parse and validate the LLM JSON response.
        """

        data = MemoryExtractor._load_json(response)

        if not isinstance(data, dict):

            return {
                "should_remember": False,
                "memories": [],
            }

        should_remember = data.get(
            "should_remember",
            False,
        )

        memories = data.get(
            "memories",
            [],
        )

        # -----------------------------------------------------
        # Nothing worth remembering
        # -----------------------------------------------------

        if not should_remember:

            return {
                "should_remember": False,
                "memories": [],
            }

        # -----------------------------------------------------
        # Validate memories list
        # -----------------------------------------------------

        if not isinstance(memories, list):

            return {
                "should_remember": False,
                "memories": [],
            }

        allowed_types = {
            "fact",
            "preference",
            "interest",
            "goal",
            "event",
            "skill",
        }

        validated_memories = []

        for item in memories:

            if not isinstance(item, dict):
                continue

            memory = item.get("memory")
            memory_type = item.get("memory_type")

            if not isinstance(memory, str):
                continue

            memory = memory.strip()

            if not memory:
                continue

            if memory_type not in allowed_types:
                memory_type = "fact"

            validated_memories.append(
                {
                    "memory": memory,
                    "memory_type": memory_type,
                }
            )

        # -----------------------------------------------------
        # Nothing valid survived validation
        # -----------------------------------------------------

        if not validated_memories:

            return {
                "should_remember": False,
                "memories": [],
            }

        return {
            "should_remember": True,
            "memories": validated_memories,
        }

