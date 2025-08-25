# PROMPTS - LangGraph Hybrid RAG with Citations

## Answer Generation Prompt
```python
ANSWER_PROMPT = """You are answering questions using ONLY the provided document chunks.

Document Chunks:
{chunks}

Question: {question}

Rules:
1. Use ONLY information from the chunks above
2. If the chunks don't contain the answer, say "I cannot find that information in the documents"
3. Attribute each factual statement to its source by referencing the chunk_id in your wording where natural
4. Keep your answer concise and factual

Answer:"""
```

## Citation Extraction Prompt
```python
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
```

## Chunk Relevance Scoring
```python
RELEVANCE_PROMPT = """Score how relevant this chunk is to the question.

Question: {question}
Chunk: {chunk_text}

Score from 0.0 to 1.0:
- 1.0 = Directly answers the question
- 0.7-0.9 = Contains relevant information
- 0.4-0.6 = Somewhat related
- 0.0-0.3 = Not relevant

Return only the numerical score:"""
```

## No Results Message
```python
NO_RESULTS_TEMPLATE = """I cannot find information about "{question}" in the available documents. 

The documents I have access to include:
{available_docs}

Please rephrase your question or ask about topics covered in these documents."""
```

## Simple Test Prompts
Use these to verify the system works:

```python
TEST_QUERIES = [
    "What is the main topic of the document?",
    "List the key points mentioned",
    "What specific steps are described?",
    "Find information about [specific term]"
]
```