# AI Career Roadmap: From Enterprise .NET Engineer to AI Systems Architect

**Profile:** 13 years C#/.NET/Azure/Angular | Backend & Enterprise Systems | Exploring GenAI/LLMs | 4 hrs/day available

---

## 1. Diagnosis: Your Biggest Weaknesses and Blind Spots

### You are a strong backend engineer trapped in an enterprise comfort zone.

**Hard truths:**

- **You have zero public proof of AI competence.** Thirteen years of .NET experience is invisible to the AI ecosystem. Nobody hiring for AI architect roles or co-founding AI companies cares about your Azure App Service deployments. You need artifacts — shipped products, open-source contributions, or published technical writing that demonstrate you can build AI systems that work in production.

- **Your Python is likely shallow.** The entire AI/ML ecosystem runs on Python. Not "I can write a for loop" Python — production Python. FastAPI, async patterns, proper packaging, type hints, testing with pytest, dependency management. Your `app/` directory here shows you are learning, but the gap between "tutorial clean architecture" and "production AI service" is large.

- **You are likely confusing "exploring" with "building."** Reading about LangChain, watching RAG tutorials, running Jupyter notebooks — none of this counts. The only thing that counts is a deployed system that solves a real problem for real users. If you cannot point to one right now, you have been exploring, not building.

- **You lack ML fundamentals.** You do not need a PhD, but you need to understand embeddings, vector similarity, tokenization, prompt engineering at a mechanical level, fine-tuning tradeoffs, and evaluation metrics. Without this, you will build brittle systems that fail in production and you will not know why.

- **Your architecture instincts may be working against you.** Enterprise .NET developers over-engineer by default. Clean Architecture, CQRS, DDD layers — these patterns are valuable in large teams with long-lived codebases. For an AI product built by one person in 90 days, they are deadweight. Ship first, refactor later.

- **You have no distribution strategy.** Building something is 30% of the work. Getting it in front of users is 70%. If your plan is "build it and post on LinkedIn," that is not a plan.

### Blind spots:

| Blind Spot | Why It Matters |
|---|---|
| You probably underestimate how fast the AI space moves | Frameworks you learn today may be deprecated in 6 months. Build on primitives, not abstractions. |
| You may be romanticizing the "architect" title | Architecture roles in AI companies require hands-on ML/infra experience, not just system design diagrams. |
| You likely overvalue your enterprise experience | Startups and AI companies optimize for speed and iteration, not governance and process. |
| You may not realize how crowded the "learning AI" space is | Thousands of senior devs are making the same transition. You need differentiation. |

---

## 2. Where You Are Wasting Time

### Time sinks to eliminate immediately:

1. **Tutorial hell with multiple frameworks.** If you have touched LangChain, LlamaIndex, Semantic Kernel, AutoGen, and CrewAI in the last 3 months, you have learned nothing deeply. Pick one. Stick with it.

2. **Over-architecting hobby projects.** Your repo shows Clean Architecture with domain/application/infrastructure layers for what appears to be a document extraction API. For a solo learning project, this structure adds ceremony without value. A flat FastAPI app with 3 files would ship faster and teach you more about the AI parts.

3. **Reading about AI instead of building with AI.** Every hour spent reading a "State of AI" report or watching a conference talk is an hour not spent writing code that calls an LLM, processes the output, and handles the failure cases.

4. **Trying to learn everything.** You do not need to understand transformer architecture from scratch. You do not need to train models. You need to build applications that use models effectively. Stay at the application layer.

5. **Maintaining Angular skills.** Unless your current job requires it, stop investing in Angular. Frontend frameworks are not your competitive advantage. Use something minimal (Next.js, Streamlit, or even a CLI) for your AI projects.

6. **LinkedIn content that is not backed by shipped work.** Posting "Day 14 of my AI journey" with a screenshot of a tutorial is negative signal. Post only when you have something real to show.

---

## 3. What to STOP Doing Immediately

| STOP | WHY |
|---|---|
| Stop starting new tutorial projects | You have enough foundational knowledge. Build one real thing. |
| Stop abstracting before you have a working prototype | No interfaces, no repositories, no dependency injection until v1 works end-to-end. |
| Stop splitting time across multiple AI topics | No computer vision, no reinforcement learning, no agent frameworks. Pick one vertical. |
| Stop comparing yourself to ML researchers | You are not competing with them. You are competing with other application engineers. |
| Stop planning in private | If nobody can see your work, it does not exist. Push to GitHub daily. Ship publicly. |
| Stop treating your 4 hours as "not enough" | 4 focused hours per day is 120 hours per month. That is more than enough to ship a real product. Most people waste 4 hours on setup and context-switching. |
| Stop using C# for AI projects | The ecosystem is Python. Accept the tax. Pay it now. Every day you delay this makes the transition harder. |

---

## 4. Your ONE Focused Direction for the Next 90 Days

### Build and ship an **AI-powered document intelligence platform** for a specific industry vertical.

**Why this direction:**

- It directly leverages your 13 years of enterprise backend experience (data pipelines, APIs, reliability)
- It sits at the intersection of LLMs and real business problems (not a toy)
- Document processing is a $30B+ market with massive inefficiency
- It requires production-grade engineering (your strength) not research (your weakness)
- It has clear monetization paths (B2B SaaS, consulting, or acqui-hire signal)
- Your existing repo already shows you are moving in this direction — now go all the way

**Why NOT other directions:**

| Alternative | Why Not |
|---|---|
| AI agents / autonomous systems | Too speculative, too crowded with hype, hard to monetize in 90 days |
| Fine-tuning / training models | Requires ML depth you do not have and compute you cannot afford |
| General chatbot / copilot | Commodity. Every framework has a chatbot template. Zero differentiation. |
| AI consulting | You have no portfolio yet. Build the portfolio first. |

---

## 5. Exactly What to Build

### Product: **ContractLens** — AI-Powered Contract Analysis Platform

An API-first platform that ingests contracts (PDF, DOCX, scanned images), extracts structured data, identifies risks and obligations, compares against templates, and surfaces actionable insights.

**Why contracts specifically:**

- Every company has contracts. Legal teams are drowning in them.
- Extraction + classification + risk scoring = a well-scoped LLM application problem
- The tolerance for "good enough" AI is higher in document analysis than in, say, medical diagnosis
- You can start with a single contract type (e.g., NDAs or SaaS vendor agreements) and expand
- It is a real product that real companies will pay for

### Technical Architecture (keep it simple):

```
┌──────────────────────────────────────────────────────────┐
│                    ContractLens                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Ingestion Layer                                         │
│  ├── PDF parsing (PyMuPDF / pdfplumber)                  │
│  ├── DOCX parsing (python-docx)                          │
│  ├── OCR fallback (Tesseract or cloud OCR)               │
│  └── Text chunking + preprocessing                       │
│                                                          │
│  Analysis Layer                                          │
│  ├── LLM extraction (structured output via OpenAI/Claude)│
│  ├── Clause classification                               │
│  ├── Risk scoring (rule-based + LLM hybrid)              │
│  ├── Obligation extraction with dates                    │
│  └── Template comparison / deviation detection           │
│                                                          │
│  Storage Layer                                           │
│  ├── PostgreSQL (structured metadata)                    │
│  ├── Vector store (pgvector) for semantic search         │
│  └── Blob storage for original documents                 │
│                                                          │
│  API Layer                                               │
│  ├── FastAPI REST endpoints                              │
│  ├── Webhook notifications                               │
│  └── Simple dashboard (Streamlit or Next.js)             │
│                                                          │
│  Infrastructure                                          │
│  ├── Docker Compose for local dev                        │
│  ├── Cloud deployment (Railway / Fly.io / Azure)         │
│  └── CI/CD with GitHub Actions                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Core Features (MVP — ship in 6 weeks, iterate for 6 weeks):

1. **Upload a contract** (PDF/DOCX) via API or UI
2. **Extract key fields**: parties, effective date, termination date, governing law, payment terms, renewal terms
3. **Classify clauses**: indemnification, limitation of liability, confidentiality, IP assignment, non-compete, termination
4. **Score risk**: flag unusual or aggressive clauses against a baseline
5. **Compare contracts**: semantic diff between two contracts or against a template
6. **Search across contracts**: "Show me all contracts with auto-renewal clauses expiring in Q2"
7. **Export structured data**: JSON, CSV, or webhook to downstream systems

### What makes this a real product vs. a demo:

- Handles messy real-world PDFs (scanned, multi-column, headers/footers)
- Has proper error handling when LLM extraction fails or hallucinates
- Includes confidence scores on extractions
- Supports batch processing (not just one document at a time)
- Has an evaluation suite that measures extraction accuracy against labeled data
- Costs are tracked per document (you know your unit economics)

---

## 6. Strict Execution Roadmap (12 Weeks)

### Phase 1: Foundation (Weeks 1-2)

**Week 1: Document Ingestion Pipeline**

- [ ] Set up project: FastAPI, PostgreSQL, Docker Compose — flat structure, no over-engineering
- [ ] Build PDF parser that handles real-world contracts (not just clean PDFs)
- [ ] Build DOCX parser
- [ ] Implement text chunking strategy (by section/clause, not fixed-size)
- [ ] Write 10 integration tests with real contract samples
- [ ] **Deliverable:** API endpoint that accepts a document and returns raw extracted text, chunked by section

**Week 2: LLM Extraction Core**

- [ ] Implement structured extraction using OpenAI/Claude function calling or structured outputs
- [ ] Extract: parties, dates, governing law, payment terms from NDA contracts
- [ ] Build prompt templates with few-shot examples
- [ ] Implement retry logic and fallback for LLM failures
- [ ] Add confidence scoring (LLM self-assessment + heuristic validation)
- [ ] **Deliverable:** API endpoint that accepts a contract and returns structured JSON with all key fields

### Phase 2: Intelligence Layer (Weeks 3-4)

**Week 3: Clause Classification + Risk Scoring**

- [ ] Build clause classifier (LLM-based with structured taxonomy)
- [ ] Implement risk scoring: rule-based baseline + LLM assessment
- [ ] Create a "baseline contract" template for NDAs
- [ ] Flag deviations from baseline with severity levels
- [ ] **Deliverable:** Risk report endpoint that returns classified clauses with risk scores

**Week 4: Vector Search + Comparison**

- [ ] Set up pgvector, embed all extracted clauses
- [ ] Build semantic search across contract corpus
- [ ] Implement contract-to-contract comparison (semantic diff)
- [ ] Implement contract-to-template comparison
- [ ] **Deliverable:** Search and comparison endpoints working end-to-end

### Phase 3: Production Hardening (Weeks 5-6)

**Week 5: Reliability + Evaluation**

- [ ] Build evaluation dataset: 20+ real or synthetic contracts with ground truth labels
- [ ] Implement automated accuracy measurement (extraction accuracy, classification F1)
- [ ] Add structured logging and cost tracking per document
- [ ] Handle edge cases: scanned PDFs (OCR), multi-language, malformed documents
- [ ] **Deliverable:** Evaluation suite that runs on CI and reports accuracy metrics

**Week 6: MVP Ship**

- [ ] Build minimal UI (Streamlit dashboard or simple Next.js frontend)
- [ ] Deploy to cloud (Railway, Fly.io, or Azure Container Apps)
- [ ] Write API documentation
- [ ] Create demo video (2 minutes, no fluff)
- [ ] **Deliverable:** Live, deployed product with public URL and demo video

### Phase 4: Traction (Weeks 7-9)

**Week 7: Get 5 Real Users**

- [ ] Identify 10 target users (legal ops, startup founders, procurement teams)
- [ ] Cold outreach: offer free analysis of their contracts
- [ ] Collect feedback on extraction accuracy and missing features
- [ ] **Deliverable:** 5 people have used the product on their real contracts

**Week 8: Iterate on Feedback**

- [ ] Fix top 3 issues from user feedback
- [ ] Add most-requested feature
- [ ] Improve extraction accuracy based on real failure cases
- [ ] **Deliverable:** V1.1 deployed with user-driven improvements

**Week 9: Expand Contract Types**

- [ ] Add support for SaaS agreements or employment contracts
- [ ] Generalize extraction templates
- [ ] Build self-serve onboarding flow
- [ ] **Deliverable:** Platform handles 2-3 contract types reliably

### Phase 5: Leverage (Weeks 10-12)

**Week 10: Technical Content**

- [ ] Write a deep technical blog post: "How I Built a Contract Analysis Platform with LLMs — Architecture, Failures, and Lessons"
- [ ] Include real metrics: accuracy numbers, cost per document, latency
- [ ] Post on Hacker News, Reddit r/MachineLearning, and relevant communities
- [ ] **Deliverable:** Published technical post with real numbers

**Week 11: Open-Source the Core**

- [ ] Extract the document extraction + LLM analysis pipeline as an open-source library
- [ ] Write proper README with quickstart, examples, and benchmarks
- [ ] Submit to relevant awesome-lists and community channels
- [ ] **Deliverable:** Open-source repo with clean documentation and working examples

**Week 12: Position for Next Move**

- [ ] Update resume/portfolio with ContractLens as the centerpiece
- [ ] Reach out to 5 companies building in the document AI space
- [ ] Evaluate: continue building (founder path) or leverage for AI architect role
- [ ] **Deliverable:** Clear next-step decision backed by 12 weeks of real evidence

---

## 7. Real Progress vs. Fake Progress

### Real Progress:

| Signal | What It Looks Like |
|---|---|
| Deployed product | A URL someone can visit and use today |
| Measurable accuracy | "Our NDA extraction hits 87% field-level accuracy across 50 test contracts" |
| Real users | People outside your network have used it on their own documents |
| Revenue or waitlist | Someone offered to pay, or signed up without you asking |
| Technical depth | You can explain why your chunking strategy works better than naive fixed-size splits |
| Cost awareness | "Each contract costs $0.12 to analyze — $0.08 in LLM calls, $0.03 in compute, $0.01 in storage" |
| Failure documentation | You can list the top 5 ways your system fails and what you are doing about each one |

### Fake Progress:

| Signal | What It Looks Like |
|---|---|
| Framework tourism | "I evaluated LangChain, LlamaIndex, and Haystack this week" |
| Architecture without code | "I designed the microservices architecture for the platform" |
| Tutorial completion | "I finished the RAG course on DeepLearning.AI" |
| Clean code without users | Beautiful abstractions that nobody has ever run on real data |
| LinkedIn posts without links | "Excited to share my AI journey!" with no link to anything |
| Reading papers | "I read the Attention Is All You Need paper" — this is not your job |
| Local demos | "It works on my machine with this sample PDF" — ship it or it does not count |
| Multiple half-built projects | 5 repos with READMEs and no deployed products |

### The Acid Test:

> Can you send someone a link right now where they can upload a contract and get a useful analysis back?
>
> If no, you have not made real progress yet.

---

## 8. Delusions and Unrealistic Expectations — Called Out

### Delusion: "I need to learn ML fundamentals before I can build AI products."

**Reality:** You are building applications, not models. You need to understand how to use models effectively — prompt engineering, structured outputs, evaluation, error handling. This is engineering, not research. Learn by building, not by taking courses.

### Delusion: "My 13 years of enterprise experience will naturally transfer."

**Reality:** About 30% transfers — the parts about reliability, testing, API design, and system thinking. The other 70% (enterprise patterns, heavy abstraction, governance-first thinking, waterfall-adjacent planning) will actively slow you down. You need to unlearn as much as you learn.

### Delusion: "I can transition gradually while keeping my current role comfortable."

**Reality:** If your current role does not involve AI, every day you spend there without building AI products outside of it is a day your market value in AI remains at zero. Your 4 hours per day is your real career. Treat it that way. Your day job is funding your transition, nothing more.

### Delusion: "The architect title will come from experience and certifications."

**Reality:** In the AI space, architect credibility comes from one thing: having built systems that work in production. Not Azure certifications. Not system design interview prep. Not blog posts about Clean Architecture. Build something, deploy it, get users, measure it, and talk about it publicly with real numbers.

### Delusion: "I need to be unique or find an untapped niche."

**Reality:** You do not need a novel idea. You need a well-executed implementation of a known problem. Contract analysis is not new. But most existing solutions are either expensive enterprise software or flimsy demos. A well-engineered, affordable, API-first solution built by someone who understands both enterprise needs and modern AI capabilities — that is your wedge.

### Delusion: "4 hours a day is not enough."

**Reality:** 4 focused hours is more than most people get in an 8-hour workday after meetings, Slack, and context-switching. The constraint is not time — it is focus. If you spend your 4 hours writing code, pushing commits, and shipping features, you will outpace people with twice the time who spend it on planning and learning.

### Delusion: "I should keep my options open."

**Reality:** Keeping options open is how you end up with nothing. Commit to one product, one stack, one market for 90 days. If it fails, you will have learned more in those 90 days than in a year of exploring. And you will have something to show for it.

---

## Summary: Your Marching Orders

1. **This week:** Tear down your current over-architected project. Start fresh with a flat FastAPI app. Get a contract PDF to structured JSON in 3 days.
2. **This month:** Ship a working extraction + risk analysis pipeline. Deploy it. Put a URL on the internet.
3. **This quarter:** Get 5 real users. Measure accuracy. Write about it publicly. Make a decision about your next move based on evidence, not aspiration.

**The only metric that matters at the end of 90 days:**

> How many real contracts has your system analyzed for real users, and what was the measured accuracy?

Everything else is noise.
