ANSWER_PROMPT = """You are answering questions using ONLY the provided document chunks.

Document Chunks:
{chunks}

Question: {question}

Rules:
1. Use ONLY information from the chunks above
2. If the chunks don't contain the answer, say "I cannot find that information in the documents"
3. Attribute each factual statement to its source by referencing the chunk_id in your wording where natural
4. Keep your answer concise and factual
5. Think step-by-step internally but DO NOT reveal your internal reasoning.

Answer:"""


CITATION_PROMPT = """Extract citations for each factual claim in this answer.

Answer: {answer}

Available Chunks:
{chunks}

For each factual statement in the answer:
1. Find the single best chunk it came from
2. Quote the most relevant sentence(s)
3. Note the chunk_id
4. Provide a confidence score from 0.0 to 1.0 based on how directly the quote supports the claim

Return ONLY a valid JSON array (no prose):
[
  {
    "claim": "statement from answer",
    "source_chunk_id": "chunk_123",
    "quote": "exact quote from chunk",
    "confidence": 0.82
  }
]

Citations:"""


REASONING_SUMMARY_PROMPT = """Produce a brief, high-level summary (1-2 sentences) of how the answer was derived from the provided chunks without exposing chain-of-thought.

Question: {question}
Answer: {answer}
Chunks: {chunks}

Constraints:
- Do not reveal internal step-by-step reasoning.
- Mention which chunk_ids were most influential if helpful.
"""


