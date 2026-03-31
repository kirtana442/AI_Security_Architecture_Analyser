#Fast api entry point for AI security assurance analyser backend

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from database import fetch_architecture, init_db, insert_architecture
from schemas import ArchitectureRequest, ArchitectureResponse, ExtractionResult
from llm import extract_architecture

@asynccontextmanager
async def lifespan(app: FastAPI):
    #initialise resources on startup
    init_db()
    yield

app = FastAPI(
    title = "AI Security Assurance Analyser",
    description = "Backend API for storing and retrieving AI architecture descriptions.",
    version = "1.0.0",
    lifespan = lifespan,
)

@app.get("/", summary="Health check")
async def root() -> str:
    """Return a simple liveness message."""
    return "AI Security Architecture Analyzer Backend Running"
 
 
@app.post(
    "/architecture",
    response_model=ArchitectureResponse,
    status_code=201,
    summary="Submit an architecture for analysis",
)
async def create_architecture(payload: ArchitectureRequest) -> ArchitectureResponse:
    """
    Accept an architecture description, persist it to the database,
    and return the newly created record.
 
    - **architecture_text**: Plain-text description of the system architecture.
    """
    record = insert_architecture(payload.architecture_text)
    return ArchitectureResponse(**record)
 
 
@app.get(
    "/architecture/{id}",
    response_model=ArchitectureResponse,
    summary="Retrieve a stored architecture",
)
async def get_architecture(id: str) -> ArchitectureResponse:
    """
    Return the architecture record identified by *id*.
 
    Raises **404** if no record with that UUID exists.
    """
    record = fetch_architecture(id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Architecture with id '{id}' not found.",
        )
    return ArchitectureResponse(**record)

@app.post(
    "/extract/{id}",
    response_model=ExtractionResult,
    summary="Run LLM extraction on a stored architecture",
)
async def extract_architecture_by_id(id: str) -> ExtractionResult:
    """
    Retrieve the architecture record for *id*, pass its text through the LLM
    extraction pipeline, validate the result, and return it as a structured
    :class:`ExtractionResult`.
 
    Flow:
        1. Fetch the architecture record from the database (404 if missing).
        2. Call ``extract_architecture()`` from the LLM layer.
        3. Validate and coerce the returned dict with Pydantic.
        4. Return the structured result.
 
    Raises:
        **404** – architecture record not found.
        **422** – LLM returned a response that does not match the schema.
        **500** – unexpected error during LLM extraction.
    """
    # fetch stored architecture
    record = fetch_architecture(id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Architecture with id '{id}' not found.",
        )
 
    #  run LLM extraction
    try:
        raw_extraction: dict = extract_architecture(record["architecture_text"])
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"LLM extraction failed: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during extraction: {exc}",
        ) from exc
 
    # validate with Pydantic and return
    return ExtractionResult(architecture_id=id, **raw_extraction)