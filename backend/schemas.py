# pydantic v2 schemas for request and response

from pydantic import BaseModel, Field

from typing import List

class ArchitectureRequest(BaseModel):
    #Payload accemtped by POST /architecture

    architecture_text: str = Field(
        ...,
        min_length = 1,
        description = "Raw architecture description to be stored and later analysed.",
    )

class ArchitectureResponse(BaseModel):
    # response returend by POST /architecture and GET /architecture/{id}.

    id: str = Field(..., description="UUID of the stored record.")
    architecture_text: str = Field(..., description="The submitted architecture text.")
    created_at: str = Field(..., description="ISO-8601 UTC timestamp of creation.")
    status: str = Field(..., description="Processing status of the record.")

class ExtractionResult(BaseModel):
    """
    Structured security extraction produced by the LLM layer.
 
    Returned by POST /extract/{id}.
    Each field is a list of short descriptive strings identified in the
    architecture text by the LLM.
    """
 
    architecture_id: str = Field(
        ...,
        description="UUID of the source architecture record.",
    )
    components: List[str] = Field(
        default_factory=list,
        description="Internal services, microservices, or modules.",
    )
    auth: List[str] = Field(
        default_factory=list,
        description="Authentication and authorisation mechanisms.",
    )
    data_stores: List[str] = Field(
        default_factory=list,
        description="Databases, caches, object stores, and queues.",
    )
    external_services: List[str] = Field(
        default_factory=list,
        description="Third-party APIs, SaaS integrations, and cloud services.",
    )
    sensitive_data: List[str] = Field(
        default_factory=list,
        description="PII, secrets, credentials, financial data, or health data.",
    )
    public_endpoints: List[str] = Field(
        default_factory=list,
        description="Routes, ports, or interfaces exposed to external clients.",
    )