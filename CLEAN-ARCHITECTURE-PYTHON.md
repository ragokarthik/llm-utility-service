# Clean Architecture in Python: A Practical Guide Using Your Own Codebase

**Audience:** You — a .NET engineer who knows Clean Architecture conceptually but needs to understand how it maps to Python, where it helps, and where it becomes dead weight in a solo AI project.

---

## The Core Idea (60-Second Version)

Clean Architecture is a dependency rule: **inner layers know nothing about outer layers.**

```
┌─────────────────────────────────────────────┐
│              API / Framework Layer           │  ← FastAPI routes, HTTP concerns
│  ┌───────────────────────────────────────┐  │
│  │        Application Layer              │  │  ← Use cases, orchestration
│  │  ┌─────────────────────────────────┐  │  │
│  │  │        Domain Layer             │  │  │  ← Entities, business rules, interfaces
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
│           Infrastructure Layer              │  ← Database, LLM clients, parsers
└─────────────────────────────────────────────┘
```

**The dependency rule:** Arrows point inward. Domain knows nothing about infrastructure. Application knows domain, but not infrastructure specifics. API and infrastructure both depend on inner layers, never the reverse.

**In .NET terms you already understand:**
- Domain = your entity classes and interfaces (no EF Core references, no HttpClient)
- Application = your MediatR handlers / service classes
- Infrastructure = your DbContext, HttpClient wrappers, third-party SDKs
- API = your Controllers

**In Python, the same structure exists but the language fights ceremony harder than C# does.** Python has no compilation step to enforce boundaries. There are no assembly references to prevent a domain class from importing SQLAlchemy. Discipline replaces the compiler.

---

## Your Current Project: What Maps Where

Here is your project's actual structure:

```
app/
├── api/
│   └── routes/
│       └── extract.py          ← API Layer (FastAPI routes)
├── application/
│   └── use_cases/
│       └── extract_data.py     ← Application Layer (orchestration)
├── core/
│   └── config.py               ← Cross-cutting (settings)
├── domain/
│   ├── entities/
│   │   └── extraction.py       ← Domain Layer (data models)
│   └── interfaces/
│       ├── llm_provider.py     ← Domain Layer (port/interface)
│       └── repository.py       ← Domain Layer (port/interface)
└── infrastructure/
    ├── database/
    │   ├── models.py           ← Infrastructure (SQLAlchemy models)
    │   ├── repositories.py     ← Infrastructure (repository impl)
    │   └── session.py          ← Infrastructure (DB connection)
    ├── llm/
    │   └── groq_client.py      ← Infrastructure (LLM adapter)
    └── parsers/
        └── pdf_parser.py       ← Infrastructure (PDF parsing)
```

This maps 1:1 to Clean Architecture. The layers are correct. The dependency direction is correct. Your `ExtractDataUseCase` depends on the `LLMProvider` interface, not on `GroqClient` directly.

**The structure is textbook. That is exactly the problem.**

---

## What Your Code Does Right

### 1. Dependency Inversion on the LLM Provider

Your use case depends on an abstraction:

```python
# application/use_cases/extract_data.py
class ExtractDataUseCase:
    def __init__(self, llm_provider: LLMProvider):  # ← interface, not concrete class
        self.llm_provider = llm_provider
```

And the interface lives in domain:

```python
# domain/interfaces/llm_provider.py
class LLMProvider(ABC):
    @abstractmethod
    async def extract_structured_data(self, prompt: str, schema: dict) -> dict:
        pass
```

**Why this is good:** Tomorrow you can swap Groq for OpenAI or Claude by creating a new class that implements `LLMProvider`. The use case does not change. This is the one abstraction that earns its keep in an AI project, because you *will* switch LLM providers.

### 2. Separation of Parsing from Analysis

PDF parsing (`pdf_parser.py`) is isolated from LLM extraction (`extract_data.py`). You can change how you parse documents without touching the LLM logic. This is correct.

### 3. Domain Entity as a Pydantic Model

```python
# domain/entities/extraction.py
class ExtractionResult(BaseModel):
    document_id: str
    extracted_data: dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    status: str = "pending"
```

Using Pydantic for domain entities is idiomatic Python. You get validation, serialization, and type checking without a separate DTO layer. In .NET you would have a domain entity + a DTO + AutoMapper. In Python, Pydantic *is* all three.

---

## Where Your Code Is Over-Engineered (The Honest Part)

### Problem 1: The Generic Repository Interface Is Dead Weight

```python
# domain/interfaces/repository.py
class Repository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]: ...
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]: ...
    @abstractmethod
    async def create(self, entity: T) -> T: ...
    @abstractmethod
    async def update(self, id: str, entity: T) -> Optional[T]: ...
    @abstractmethod
    async def delete(self, id: str) -> bool: ...
```

**Why this is wrong for your project:**

- You have exactly one entity (`ExtractionResult`) and one repository (`ExtractionRepository`)
- You will never have a second implementation of this repository (you are not swapping SQLite for MongoDB mid-project)
- The generic CRUD interface forces you to implement 5 methods when your use case only needs `create` and `get_by_id`
- This is a .NET habit (IRepository<T>) that does not pay for itself in a small Python project

**What to do instead:** Delete the generic interface. If you need a repository at all, make it concrete and minimal:

```python
class ExtractionStore:
    def __init__(self, db: Session):
        self.db = db

    async def save(self, result: ExtractionResult) -> ExtractionResult:
        ...

    async def get(self, extraction_id: str) -> ExtractionResult | None:
        ...
```

Two methods. No generics. No ABC. It does what you need.

### Problem 2: The Use Case Class Adds an Unnecessary Layer

```python
# application/use_cases/extract_data.py
class ExtractDataUseCase:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def execute(self, document_content, extraction_schema, document_id):
        prompt = self._build_extraction_prompt(document_content, extraction_schema)
        extracted_data = await self.llm_provider.extract_structured_data(prompt, extraction_schema)
        confidence_score = self._calculate_confidence(extracted_data, extraction_schema)
        return ExtractionResult(...)
```

**What this class actually does:** It builds a prompt, calls the LLM, and wraps the result. That is a function, not a class.

**In Python, prefer functions over single-method classes:**

```python
async def extract_data(
    llm: LLMProvider,
    document_content: str,
    schema: dict[str, Any],
    document_id: str,
) -> ExtractionResult:
    prompt = build_extraction_prompt(document_content, schema)
    extracted_data = await llm.extract_structured_data(prompt, schema)
    confidence = calculate_confidence(extracted_data, schema)
    return ExtractionResult(
        document_id=document_id,
        extracted_data=extracted_data,
        confidence_score=confidence,
        status="completed",
    )
```

Same logic, less boilerplate, easier to test (just call the function with a mock LLM). In .NET, you need classes for DI. In Python, you pass dependencies as arguments.

### Problem 3: Your Route Handler Manually Wires Everything

```python
# api/routes/extract.py
@router.post("/pdf", response_model=ExtractionResult)
async def extract_from_pdf(
    file: UploadFile = File(...),
    llm_provider: GroqClient = Depends(get_llm_provider),  # ← concrete class, not interface
    pdf_parser: PDFParser = Depends(get_pdf_parser),
    db: Session = Depends(get_db)
):
    use_case = ExtractDataUseCase(llm_provider=llm_provider)
    result = await use_case.execute(...)
    repository = ExtractionRepository(db=db)
    stored_result = await repository.create(result)
```

**The irony:** You defined an `LLMProvider` interface in domain, but your route handler directly references `GroqClient`. The abstraction is bypassed at the composition root. You also instantiate `ExtractDataUseCase` and `ExtractionRepository` manually inside the handler, which means the handler knows about every layer.

**In .NET, the DI container handles this.** In Python/FastAPI, the `Depends()` system is your DI container. But you are mixing it with manual wiring.

### Problem 4: Two Models for One Thing

You have:
- `ExtractionResult` (Pydantic, domain layer) — the domain entity
- `ExtractionRecord` (SQLAlchemy, infrastructure layer) — the database model

Plus a `_to_entity` method in the repository that maps between them:

```python
def _to_entity(self, record: ExtractionRecord) -> ExtractionResult:
    return ExtractionResult(
        id=str(record.id),
        document_id=record.document_id,
        ...
    )
```

**In .NET this is normal** (Entity → DTO → ViewModel, with AutoMapper glue). **In Python it is usually unnecessary.** SQLAlchemy 2.0 with Pydantic integration, or using SQLModel (which combines both), eliminates this mapping entirely.

---

## How Clean Architecture Should Look in Python (Pragmatic Version)

### For a Solo AI Project (What You Should Use Now)

```
app/
├── main.py              ← FastAPI app setup
├── config.py            ← Settings
├── models.py            ← Pydantic models (domain + API schemas in one place)
├── db.py                ← Database models + connection (SQLModel or SQLAlchemy)
├── llm.py               ← LLM client (with a Protocol for swappability)
├── parsing.py           ← Document parsing
├── extraction.py        ← Core extraction logic (functions, not classes)
└── routes/
    └── extract.py       ← API endpoints
```

**8 files instead of 17.** Same functionality. Every file has a clear purpose. No empty `__init__.py` ceremony.

**Key differences from your current structure:**
- No `domain/interfaces/` folder — use Python `Protocol` inline where needed
- No `application/use_cases/` — use plain functions
- No separate entity and database model — use SQLModel or a single Pydantic model
- No generic repository — use direct database functions or a minimal store class

### For a Growing Team Project (When You Need More Structure)

```
app/
├── main.py
├── config.py
├── domain/
│   ├── models.py        ← Pydantic domain models
│   └── protocols.py     ← Protocol definitions (Python's structural typing)
├── services/
│   ├── extraction.py    ← Business logic as functions or thin service classes
│   └── analysis.py
├── infrastructure/
│   ├── db.py            ← Database setup + models
│   ├── llm/
│   │   ├── base.py      ← LLM Protocol
│   │   ├── openai.py    ← OpenAI implementation
│   │   └── groq.py      ← Groq implementation
│   └── parsers/
│       └── pdf.py
└── api/
    └── routes/
        └── extract.py
```

**The key insight:** You graduate to more structure when you have a reason — multiple LLM providers, multiple developers, or multiple bounded contexts. Not before.

---

## Python-Specific Patterns That Replace .NET Patterns

### Replace ABC Interfaces with Protocol (Structural Typing)

**.NET habit:**
```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def extract_structured_data(self, prompt: str, schema: dict) -> dict:
        pass
```

**Python way:**
```python
from typing import Protocol

class LLMProvider(Protocol):
    async def extract_structured_data(self, prompt: str, schema: dict) -> dict: ...
```

**Why Protocol is better:** Any class that has a method with that signature *automatically* satisfies the protocol. No inheritance required. No `(LLMProvider)` in the class definition. This is duck typing with type checker support. Your `GroqClient` would satisfy `LLMProvider` without explicitly inheriting from it.

### Replace DI Container with FastAPI Depends + Closures

**.NET habit:** Register services in a container, inject via constructor.

**Python/FastAPI way:**
```python
def get_llm() -> LLMProvider:
    return GroqClient(api_key=settings.GROQ_API_KEY)

@router.post("/extract")
async def extract(
    file: UploadFile,
    llm: LLMProvider = Depends(get_llm),
):
    ...
```

For testing, override the dependency:
```python
app.dependency_overrides[get_llm] = lambda: MockLLMClient()
```

### Replace Repository Pattern with Simple Functions

**.NET habit:** `IRepository<T>` → `Repository<T>` → `SpecificRepository`.

**Python way:**
```python
async def save_extraction(db: Session, result: ExtractionResult) -> ExtractionResult:
    record = ExtractionRecord(**result.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return ExtractionResult.model_validate(record)
```

Just a function. No class needed unless you have complex state to manage.

### Replace MediatR / CQRS with Plain Functions

**.NET habit:** `IRequest<T>` → `IRequestHandler<TRequest, TResponse>` → MediatR pipeline.

**Python way:**
```python
async def extract_data(llm: LLMProvider, content: str, schema: dict) -> ExtractionResult:
    ...
```

Call it directly. No mediator. No pipeline. If you need cross-cutting concerns (logging, timing), use decorators:

```python
import functools
import time

def timed(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

@timed
async def extract_data(llm: LLMProvider, content: str, schema: dict) -> ExtractionResult:
    ...
```

---

## When Clean Architecture IS Worth It in Python

| Situation | Use Clean Architecture? | Why |
|---|---|---|
| Solo project, 1-3 months | No | Ship speed matters more than boundary enforcement |
| Team of 3+, shared codebase | Yes, lightweight version | Prevents developers from coupling everything to everything |
| Multiple LLM providers needed | Yes, for the LLM layer only | The Protocol/interface for LLM providers earns its keep |
| Multiple database backends | Rarely | You almost never switch databases. YAGNI. |
| Microservice with clear domain | Yes | Bounded context maps naturally to Clean Architecture |
| CLI tool or script | Absolutely not | Functions in a single file. Done. |

---

## The Refactoring You Should Do This Week

Take your current 17-file structure and collapse it to this:

```
app/
├── main.py              ← Keep as-is, simplify
├── config.py            ← Keep as-is
├── models.py            ← Merge ExtractionResult + ExtractionRecord (use SQLModel)
├── llm.py               ← GroqClient + LLMProvider Protocol in one file
├── parsing.py           ← PDFParser, simplified
├── extraction.py        ← extract_data() function (not a class)
├── db.py                ← Session + save/get functions (not a repository class)
└── routes/
    └── extract.py       ← Simplified, uses Depends properly
```

**Time to do this refactor:** One focused session. The behavior does not change. The code gets easier to read, modify, and extend.

**Then** you are in a clean position to start building ContractLens features on top of a structure that helps instead of hinders.

---

## The Rule for Your Situation

> Add architectural layers when the pain of not having them exceeds the pain of maintaining them.

Right now, the pain of maintaining 17 files with interfaces, generics, and manual mapping exceeds the pain of a simpler structure. Start flat. Add layers when complexity demands it — not before.
