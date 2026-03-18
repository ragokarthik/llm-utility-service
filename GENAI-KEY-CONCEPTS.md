# GenAI Key Concepts: What Actually Matters for Application Engineers

**Context:** You are not becoming an ML researcher. You are an application engineer who needs to use LLMs effectively in production systems. This guide covers only what you need to know to build, ship, and debug real AI-powered products. Everything else is noise.

---

## Tier 1: Non-Negotiable Fundamentals

These are concepts you must understand mechanically — not just "I've heard of it" but "I can explain the tradeoffs and debug when it breaks."

---

### 1. Tokens and Tokenization

What LLMs actually process. Not words, not characters — tokens.

- A token is roughly 3-4 characters in English. "contractual" is 3 tokens. "NDA" might be 1.
- Every API call has a **context window** measured in tokens (e.g., GPT-4o: 128K tokens, Claude 3.5: 200K tokens).
- You are billed per token (input + output separately).
- **Why it matters to you:** When your contract analysis chokes on a 200-page PDF, it is because you blew the context window. You need to chunk intelligently, not dump the whole document.

**What to know cold:**
- How to count tokens before sending a request (`tiktoken` for OpenAI)
- Input vs. output token pricing differences
- Context window limits for models you use
- What happens when you exceed the limit (truncation, errors, degraded output)

---

### 2. Prompt Engineering (The Mechanical Kind)

Not "write a good prompt." The actual engineering patterns that determine output quality.

**System prompt vs. user prompt vs. assistant prefill:**
- System prompt: Sets behavior, persona, constraints. Processed differently by the model.
- User prompt: The actual request. This is where your document content goes.
- Assistant prefill: You can start the assistant's response to force a format (e.g., start with `{` to force JSON).

**Few-shot prompting:**
- Include 2-5 examples of input/output pairs in your prompt
- The single most effective technique for improving extraction accuracy
- For ContractLens: include examples of contract clauses and their expected structured output

**Chain-of-thought (CoT):**
- Ask the model to reason step-by-step before giving a final answer
- Critical for complex extraction: "First identify the clause type, then extract the key terms, then assess risk"
- Increases token usage (cost) but dramatically improves accuracy on complex tasks

**Structured output forcing:**
- OpenAI function calling / tool use
- JSON mode (`response_format: { type: "json_object" }`)
- Pydantic models with `instructor` library
- **This is your most important prompt engineering skill.** Every extraction task in ContractLens needs structured, typed output.

**What to know cold:**
- How to write a system prompt that constrains output format reliably
- How to construct few-shot examples that cover edge cases
- How to use function calling / tool use to get typed responses
- How to handle refusals and off-topic responses

---

### 3. Embeddings and Vector Similarity

How machines understand "meaning" and find similar content.

- An **embedding** is a numerical representation of text — a list of 768-3072 floating point numbers (a vector).
- Similar meanings produce vectors that are close together in space.
- **Cosine similarity** measures how close two vectors are (-1 to 1, higher = more similar).
- Embedding models are different from generation models: `text-embedding-3-small` (OpenAI), `voyage-3` (Voyage AI).

**How this applies to ContractLens:**
- Embed every clause in every contract
- "Find all indemnification clauses" = embed the query, find nearest vectors
- "Compare contract A to contract B" = compare clause embeddings pairwise
- Store embeddings in **pgvector** (PostgreSQL extension) — you already know Postgres

**What to know cold:**
- Difference between embedding models and generation models
- How to choose embedding dimensions (cost vs. quality tradeoff)
- How cosine similarity works (and when it fails)
- How to create and query a vector index in pgvector
- Chunking strategy matters more than embedding model choice

---

### 4. Retrieval-Augmented Generation (RAG)

The core pattern for building LLM applications that use your own data. This is the backbone of ContractLens.

**The pattern:**
```
User query → Embed query → Search vector store → Retrieve relevant chunks
→ Inject chunks into prompt → LLM generates answer grounded in your data
```

**Why it exists:** LLMs do not know your contracts. You cannot fine-tune a model every time a new contract is uploaded. Instead, you retrieve relevant content at query time and include it in the prompt.

**RAG components you must build:**
1. **Document loader** — parse PDF/DOCX into text
2. **Chunker** — split text into meaningful segments (by clause, by section — not arbitrary 500-char blocks)
3. **Embedder** — convert chunks to vectors
4. **Vector store** — pgvector, Pinecone, Weaviate, Qdrant (pgvector is fine for your scale)
5. **Retriever** — query that returns top-K relevant chunks
6. **Generator** — LLM call that synthesizes an answer from retrieved chunks

**What separates good RAG from bad RAG:**

| Factor | Bad RAG | Good RAG |
|---|---|---|
| Chunking | Fixed 500 chars | Semantic sections, clause boundaries |
| Retrieval | Top-3 by cosine only | Hybrid: vector + keyword (BM25) |
| Context | Dump all chunks into prompt | Re-rank, filter, deduplicate |
| Grounding | Hope the LLM uses the context | Cite specific chunks, verify claims |
| Evaluation | "It looks right" | Measured precision/recall against labeled data |

**What to know cold:**
- How to implement the full RAG pipeline from scratch (not just a LangChain one-liner)
- Chunking strategies and their tradeoffs
- Hybrid search (vector + keyword)
- How to evaluate RAG quality (faithfulness, relevance, completeness)

---

### 5. Structured Data Extraction

The specific LLM capability you will use the most in ContractLens. This is where you turn unstructured contract text into typed, validated data.

**The pattern:**
```
Contract text → LLM with schema definition → Validated structured output
```

**Tools and approaches (pick one):**
- **`instructor` library** (recommended) — wraps OpenAI/Anthropic calls with Pydantic validation and automatic retries
- **OpenAI function calling** — define a JSON schema, model fills it in
- **Anthropic tool use** — similar to function calling

**Example (what your code will look like):**
```python
from pydantic import BaseModel
from instructor import from_openai
from openai import OpenAI

class ContractMetadata(BaseModel):
    parties: list[str]
    effective_date: str | None
    termination_date: str | None
    governing_law: str | None
    contract_type: str
    auto_renewal: bool
    confidence: float

client = from_openai(OpenAI())
result = client.chat.completions.create(
    model="gpt-4o",
    response_model=ContractMetadata,
    messages=[
        {"role": "system", "content": "Extract contract metadata..."},
        {"role": "user", "content": contract_text}
    ]
)
```

**What to know cold:**
- Pydantic model design for LLM outputs
- How to handle partial extractions (some fields missing)
- Retry strategies when validation fails
- Confidence scoring (model self-assessment + heuristic checks)
- Cost per extraction (token counting)

---

## Tier 2: Production-Critical Concepts

These separate toy demos from production systems. You need these by week 5.

---

### 6. LLM Evaluation and Testing

You cannot improve what you cannot measure.

**Types of evaluation:**
- **Extraction accuracy:** Does the model extract "Acme Corp" as a party when the contract says "Acme Corporation, Inc."? Measure field-by-field against ground truth.
- **Classification accuracy:** Does it correctly label a clause as "indemnification" vs. "limitation of liability"? Measure precision, recall, F1 per class.
- **Faithfulness:** Does the generated summary contain only information from the source document? (Catches hallucination.)
- **Relevance:** Does the RAG pipeline retrieve the right chunks for a given query?

**How to build an evaluation pipeline:**
1. Create a labeled dataset: 20-50 contracts with manually annotated fields and clause labels
2. Run your extraction pipeline on each contract
3. Compare outputs to ground truth, compute metrics
4. Run this on every code change (CI integration)

**What to know cold:**
- Precision, recall, F1 score — what they mean and when each matters
- How to build a labeled dataset efficiently (start with synthetic, validate with real)
- LLM-as-judge pattern (use a stronger model to evaluate a weaker model's output)
- Regression testing: catch when a prompt change breaks previously correct extractions

---

### 7. Cost Management and Model Selection

LLM APIs are priced per token. This is your largest variable cost.

**Current model landscape (what matters for your use case):**

| Model | Strengths | Cost (input/output per 1M tokens) | Use When |
|---|---|---|---|
| GPT-4o | Best structured extraction, function calling | ~$2.50 / $10.00 | Complex extraction, risk analysis |
| GPT-4o-mini | Good quality, much cheaper | ~$0.15 / $0.60 | Clause classification, simple extraction |
| Claude 3.5 Sonnet | Strong reasoning, long context | ~$3.00 / $15.00 | Document comparison, complex analysis |
| Claude 3.5 Haiku | Fast, cheap | ~$0.25 / $1.25 | High-volume classification |

**Cost optimization strategies:**
- Use cheap models for simple tasks (classification), expensive models for complex tasks (risk analysis)
- Cache results aggressively — the same clause structure does not need re-analysis
- Batch similar requests
- Minimize prompt size: do not include instructions the model already follows

**What to know cold:**
- How to calculate cost per document before you ship
- When to use a smaller model vs. a larger one
- Caching strategies for LLM responses
- How to set up billing alerts so you do not get a surprise $500 bill

---

### 8. Chunking Strategies

The most underrated skill in building LLM applications. Bad chunking ruins everything downstream.

**Why it matters:** If you split a contract clause across two chunks, the LLM sees an incomplete thought. Your extraction fails. Your embedding is noisy. Your search returns garbage.

**Strategies (from simplest to most effective):**

| Strategy | How | When |
|---|---|---|
| Fixed-size | Split every N characters | Never for contracts |
| Recursive character | Split by paragraphs, then sentences | Baseline approach |
| Section-based | Split by headings (Section 1, Article II) | Good for well-structured contracts |
| Semantic | Group sentences by topic similarity | Best quality, more complex to build |
| Hybrid | Section-based + semantic within sections | What you should target for ContractLens |

**Overlap:** Always include 1-2 sentences of overlap between chunks. A clause that starts at the end of chunk N should also appear at the start of chunk N+1.

**Metadata:** Every chunk should carry metadata: source document, section title, page number, chunk index. This is critical for citation and debugging.

---

### 9. Hallucination Detection and Grounding

LLMs will confidently fabricate contract terms that do not exist. In a legal context, this is not just a bug — it is a liability.

**Types of hallucination in document extraction:**
- **Fabricated fields:** Model invents a termination date that is not in the contract
- **Conflated information:** Model mixes terms from two different clauses
- **Over-inference:** Model concludes "auto-renewal" from ambiguous language

**Mitigation strategies:**
- **Source citation:** Force the model to quote the exact text it extracted from
- **Confidence thresholds:** If the model's self-assessed confidence is below 0.7, flag for human review
- **Cross-validation:** Extract twice with different prompts, compare results
- **Rule-based validation:** If the extracted date is before 1990 or after 2050, something is wrong
- **Retrieval grounding:** Only let the model answer from retrieved chunks, not its training data

**What to know cold:**
- How to design prompts that minimize hallucination (cite sources, constrain to provided text)
- How to implement confidence scoring that actually correlates with accuracy
- When to flag for human review vs. auto-accept

---

## Tier 3: Concepts to Learn as You Need Them

Do not study these upfront. Encounter them through building.

---

### 10. Fine-Tuning (When Prompting Is Not Enough)

- Fine-tuning = training a model on your specific data to improve performance on your specific task
- **When to consider it:** Your extraction accuracy plateaus despite prompt optimization, and you have 500+ labeled examples
- **When NOT to consider it:** You have fewer than 200 labeled examples, or prompt engineering has not been fully optimized yet
- Start with prompt engineering. Move to fine-tuning only when you hit a measurable wall.
- OpenAI fine-tuning API is the easiest path. Do not try to fine-tune open-source models until you have exhausted API options.

### 11. Agents and Tool Use

- An "agent" is an LLM that can take actions: call APIs, query databases, run code
- **Relevant to ContractLens later:** An agent that can search your contract database, compare clauses, and generate a summary report autonomously
- Do not build agents in your MVP. Build deterministic pipelines first. Add agency later when you understand the failure modes.

### 12. Guardrails and Output Validation

- Runtime validation of LLM outputs beyond basic type checking
- Content filtering, PII detection, format enforcement
- Libraries: `guardrails-ai`, `nemoguardrails`
- Important for production but not for MVP. Add when you have real users.

### 13. Observability and Tracing

- Track every LLM call: input, output, latency, tokens, cost
- Tools: `langfuse`, `langsmith`, `phoenix` (Arize)
- Critical for debugging production issues: "Why did extraction fail for this contract?"
- Add in week 5-6, not day 1.

### 14. Multi-Modal Inputs

- Models that process images alongside text (GPT-4o, Claude 3.5 Sonnet)
- **Relevant to ContractLens:** Processing scanned contracts by sending page images directly to a vision model instead of relying on OCR
- This is increasingly the better approach for scanned documents. Keep it in mind for v2.

---

## Concepts You Should NOT Spend Time On

| Concept | Why Not |
|---|---|
| Transformer architecture internals | You are using models, not building them |
| Attention mechanisms (Q/K/V) | Same reason |
| Training from scratch | You do not have the data, compute, or need |
| RLHF / reward modeling | This is model training, not application building |
| Diffusion models / image generation | Not relevant to your product |
| Speech-to-text / TTS | Not relevant to your product |
| Reinforcement learning | Different field entirely |
| Neural network fundamentals | Helpful for intuition, but not blocking your progress |
| Academic papers | Read blog posts and documentation instead. Papers are for researchers. |

---

## Practical Learning Path (Mapped to Your Roadmap)

| Week | Concepts to Apply | How You Learn Them |
|---|---|---|
| 1 | Tokens, chunking strategies | Build the document ingestion pipeline. Count tokens. Hit the context limit. Fix it. |
| 2 | Prompt engineering, structured extraction | Build the extraction pipeline. Use `instructor`. Iterate on prompts until accuracy is acceptable. |
| 3 | Few-shot prompting, chain-of-thought | Improve extraction accuracy. Add clause classification. |
| 4 | Embeddings, vector similarity, RAG | Build the search pipeline. Implement pgvector. Query it. |
| 5 | Evaluation, hallucination detection | Build the test suite. Measure accuracy. Find and fix hallucinations. |
| 6 | Cost management, model selection | Optimize: swap expensive calls for cheaper models where quality holds. Calculate unit economics. |
| 7-12 | Fine-tuning (if needed), agents (if needed), observability | Encounter these through real user feedback and production issues. |

---

## The Rule

> Learn a concept only when your current build requires it. If you cannot point to a specific line of code that needs this knowledge, you do not need it yet.

Every hour spent "learning GenAI concepts" without writing code is an hour wasted. Open your editor, not your browser.
