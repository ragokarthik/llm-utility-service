# Day 1: Exactly What To Do (4 Hours)

**Goal by end of day:** A running FastAPI app that accepts a PDF, extracts raw text, sends it to an LLM, and returns structured JSON with contract parties, dates, and contract type. Deployed locally. Tested with one real contract.

No architecture. No abstractions. No planning. Just working code.

---

## Hour 1: Project Setup + PDF Parsing (0:00 - 1:00)

### Step 1: Create a fresh project (10 min)

```bash
mkdir contractlens && cd contractlens
python -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

pip install fastapi uvicorn python-multipart pymupdf openai pydantic python-dotenv

pip freeze > requirements.txt
```

Create exactly 3 files:

```
contractlens/
├── .env
├── main.py
├── requirements.txt
```

That is the entire project structure for today.

### Step 2: Set up your LLM key (2 min)

**.env file:**
```
OPENAI_API_KEY=sk-your-key-here
```

If you do not have an OpenAI key, get one at platform.openai.com. Cost for today: under $0.50. If you prefer Groq (free tier), substitute — but OpenAI's structured output is more reliable for extraction.

### Step 3: Build the PDF parser + first endpoint (48 min)

**main.py — write this, do not copy-paste. Typing it forces you to understand every line:**

```python
import fitz
import json
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from fastapi import FastAPI, UploadFile, File, HTTPException

load_dotenv()

app = FastAPI(title="ContractLens")
client = OpenAI()


# --- Models ---

class ContractMetadata(BaseModel):
    parties: list[str] = Field(description="All named parties in the contract")
    effective_date: str | None = Field(description="Contract start date")
    termination_date: str | None = Field(description="Contract end date or expiry")
    contract_type: str = Field(description="Type: NDA, SaaS Agreement, Employment, etc.")
    governing_law: str | None = Field(description="Jurisdiction / governing law")
    confidence: float = Field(ge=0.0, le=1.0, description="How confident the extraction is")


class ExtractionResponse(BaseModel):
    filename: str
    page_count: int
    extracted: ContractMetadata
    raw_text_preview: str


# --- PDF Parsing ---

def parse_pdf(content: bytes) -> tuple[str, int]:
    doc = fitz.open(stream=content, filetype="pdf")
    pages = [page.get_text() for page in doc]
    page_count = len(pages)
    doc.close()
    text = "\n\n".join(pages)
    if not text.strip():
        raise ValueError("PDF has no extractable text (might be scanned/image-based)")
    return text, page_count


# --- LLM Extraction ---

SYSTEM_PROMPT = """You are a contract analysis assistant. Extract metadata from the provided contract text.

Rules:
- Extract ONLY information explicitly stated in the text
- If a field is not found, return null
- For parties, include the full legal entity names
- For dates, use ISO format (YYYY-MM-DD) when possible
- Set confidence between 0 and 1 based on how clearly the information was stated
- If the document is not a contract, set confidence to 0 and contract_type to "Not a contract"
"""


def extract_metadata(text: str) -> ContractMetadata:
    truncated = text[:12000]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Extract contract metadata as JSON matching this schema:\n"
                f"{json.dumps(ContractMetadata.model_json_schema(), indent=2)}\n\n"
                f"Contract text:\n{truncated}",
            },
        ],
    )

    raw = json.loads(response.choices[0].message.content)
    return ContractMetadata(**raw)


# --- API ---

@app.post("/analyze", response_model=ExtractionResponse)
async def analyze_contract(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    content = await file.read()

    try:
        text, page_count = parse_pdf(content)
    except ValueError as e:
        raise HTTPException(422, str(e))

    extracted = extract_metadata(text)

    return ExtractionResponse(
        filename=file.filename,
        page_count=page_count,
        extracted=extracted,
        raw_text_preview=text[:500],
    )


@app.get("/health")
async def health():
    return {"status": "running"}
```

### Step 4: Run it (1 min)

```bash
uvicorn main:app --reload
```

Open http://localhost:8000/docs — you should see Swagger UI with one POST endpoint.

**Checkpoint:** If the server starts, Hour 1 is done. If it does not, fix the error before moving on.

---

## Hour 2: Test With a Real Contract (1:00 - 2:00)

### Step 5: Get a real contract PDF (10 min)

You need an actual contract, not a toy document. Options:

1. **Best:** Use an NDA or contract from your own files (redact sensitive info if needed)
2. **Good:** Search "sample NDA PDF" or "sample SaaS agreement PDF" — download one from a legal template site
3. **Acceptable:** Go to SEC EDGAR (sec.gov/cgi-bin/browse-edgar), search any public company, find a filed contract (exhibit 10.x)

Download one PDF. Name it `test_contract.pdf`.

### Step 6: Test via Swagger UI (5 min)

1. Go to http://localhost:8000/docs
2. Click the POST /analyze endpoint
3. Click "Try it out"
4. Upload your `test_contract.pdf`
5. Hit Execute

**Read the response carefully.** Check every field:
- Are the parties correct? Are the full legal names extracted?
- Are the dates right? Compare with the actual document.
- Is the contract type accurate?
- What is the confidence score?

**Write down what it got wrong.** This is your first data point.

### Step 7: Test with 2 more contracts (20 min)

Find 2 more contract PDFs (different types if possible — one NDA, one service agreement). Run each through the endpoint. For each one, note:

- Fields extracted correctly: ___
- Fields extracted incorrectly: ___
- Fields it missed: ___
- Confidence score vs. actual accuracy: ___

### Step 8: Fix the prompt based on failures (25 min)

Your first extraction will have errors. Common ones:

**Problem: Parties are incomplete or wrong**
- Fix: Add a few-shot example to the system prompt showing how you want parties extracted

**Problem: Dates are in the wrong format**
- Fix: Add explicit format instructions and an example

**Problem: Contract type is too vague ("Agreement")**
- Fix: Add an enum of acceptable types to the prompt

**Problem: Confidence is always 0.9+ even when extraction is wrong**
- Fix: Add calibration instructions: "Set confidence to 0.5 if any field required interpretation"

Each fix is a prompt edit, not a code change. Edit `SYSTEM_PROMPT`, re-test, compare. This is the prompt engineering loop. Get comfortable with it — this is how you will spend 40% of your time on this project.

---

## Hour 3: Add Clause Extraction (2:00 - 3:00)

### Step 9: Add a second extraction model (15 min)

Add this to `main.py`:

```python
class Clause(BaseModel):
    clause_type: str = Field(description="Type: indemnification, confidentiality, termination, non-compete, limitation of liability, IP assignment, payment, other")
    summary: str = Field(description="One-sentence summary of what this clause says")
    risk_level: str = Field(description="low, medium, or high")
    exact_quote: str = Field(description="The exact text from the contract for this clause")


class DetailedAnalysis(BaseModel):
    metadata: ContractMetadata
    clauses: list[Clause]
    overall_risk: str = Field(description="low, medium, or high — overall contract risk assessment")
    key_concerns: list[str] = Field(description="Top concerns a lawyer should review")
```

### Step 10: Add detailed analysis endpoint (20 min)

```python
CLAUSE_PROMPT = """You are a contract analysis assistant. Analyze the provided contract.

1. Extract contract metadata (parties, dates, type, governing law)
2. Identify and classify each significant clause
3. Assess risk for each clause and overall
4. List key concerns

Rules:
- For each clause, quote the EXACT text from the contract
- Risk levels: low (standard/favorable), medium (unusual but acceptable), high (aggressive/unfavorable)
- Only flag genuine concerns, not boilerplate
"""


def analyze_contract_detailed(text: str) -> DetailedAnalysis:
    truncated = text[:12000]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": CLAUSE_PROMPT},
            {
                "role": "user",
                "content": f"Analyze this contract. Return JSON matching this schema:\n"
                f"{json.dumps(DetailedAnalysis.model_json_schema(), indent=2)}\n\n"
                f"Contract text:\n{truncated}",
            },
        ],
    )

    raw = json.loads(response.choices[0].message.content)
    return DetailedAnalysis(**raw)


@app.post("/analyze/detailed", response_model=DetailedAnalysis)
async def analyze_contract_full(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    content = await file.read()

    try:
        text, page_count = parse_pdf(content)
    except ValueError as e:
        raise HTTPException(422, str(e))

    return analyze_contract_detailed(text)
```

### Step 11: Test detailed analysis (25 min)

Upload the same 3 contracts to `/analyze/detailed`. For each one:

- Count how many clauses it found
- Check if `exact_quote` actually appears in the document (this catches hallucination)
- Check if risk levels make sense
- Read the `key_concerns` — are they real concerns or generic filler?

**This is your first hallucination detection exercise.** If `exact_quote` does not appear in the source text, the model fabricated it. Note which clauses hallucinate and how often.

---

## Hour 4: Push to GitHub + Track Results (3:00 - 4:00)

### Step 12: Initialize git and push (10 min)

```bash
echo "venv/\n.env\n__pycache__/\n*.pyc" > .gitignore
git init
git add .
git commit -m "Day 1: contract analysis API with metadata extraction and clause analysis"
git remote add origin <your-repo-url>
git push -u origin main
```

**Your code is now public. This is accountability.**

### Step 13: Create a test results log (20 min)

Create `EVAL.md` in your repo:

```markdown
# Extraction Evaluation Log

## Day 1 Results

### Contract 1: [filename]
- Type: [NDA / SaaS Agreement / etc.]
- Pages: [X]

**Metadata Extraction:**
| Field | Expected | Got | Correct? |
|---|---|---|---|
| Parties | [manual] | [extracted] | Y/N |
| Effective date | [manual] | [extracted] | Y/N |
| Termination date | [manual] | [extracted] | Y/N |
| Contract type | [manual] | [extracted] | Y/N |
| Governing law | [manual] | [extracted] | Y/N |

**Accuracy: X/5 fields correct**

**Clause Analysis:**
- Total clauses found: [X]
- Clauses with accurate exact_quote: [X/total]
- Hallucinated quotes: [X/total]
- Risk assessments that seem reasonable: [X/total]

### Contract 2: [repeat]
### Contract 3: [repeat]

## Day 1 Summary
- Metadata accuracy: X/15 fields across 3 contracts
- Hallucination rate: X%
- Top failure modes: [list]
- Prompt changes made: [list]
```

Fill this in with your actual results. Commit it.

### Step 14: Identify tomorrow's work (10 min)

Based on today's results, write down exactly 3 things to fix tomorrow:

1. The worst extraction failure — what specific prompt change would fix it?
2. The worst hallucination — what grounding technique would prevent it?
3. The biggest missing feature — what would make this more useful?

Write these in `EVAL.md` under a "Day 2 Priorities" section. Commit and push.

### Step 15: Verify your day (5 min)

Run this checklist:

- [ ] FastAPI server starts and serves Swagger docs
- [ ] `/analyze` endpoint returns structured metadata from a PDF
- [ ] `/analyze/detailed` endpoint returns clause-level analysis
- [ ] Tested with 3 real contract PDFs
- [ ] Accuracy measured and logged in EVAL.md
- [ ] Code pushed to GitHub
- [ ] Tomorrow's priorities are written down

**If all 7 boxes are checked, Day 1 is done. You have shipped more in 4 hours than most people ship in a week of "learning AI."**

---

## What You Did NOT Do Today (Intentionally)

| Skipped | Why |
|---|---|
| Database | You do not need persistence on Day 1 |
| Docker | Local dev is fine for now |
| Clean Architecture layers | A single file works. Add structure when it hurts. |
| Authentication | No users yet |
| Error handling beyond basics | Get the happy path working first |
| Tests | Your EVAL.md is your test suite for now |
| Frontend | Swagger UI is your frontend for now |
| Multiple LLM providers | One provider. Working. That is enough. |

## What You DID Do Today

- Built a working contract analysis API
- Tested it on real documents
- Measured extraction accuracy with real numbers
- Identified specific failure modes
- Pushed working code to GitHub

That is real progress.
