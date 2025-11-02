"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response for document upload."""
    document_id: str
    filename: str
    file_size: int
    status: str
    message: str
    processed_at: Optional[datetime] = None


class QueryRequest(BaseModel):
    """Request for querying documents."""
    query: str = Field(..., description="Natural language query")
    document_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific document IDs to query"
    )
    max_results: int = Field(default=5, description="Maximum number of results")
    model: Optional[str] = Field(default="gpt-4", description="LLM model to use")


class QueryResponse(BaseModel):
    """Response for query."""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: Optional[float] = None
    processing_time: float
    model_used: str


class CodeGenerationRequest(BaseModel):
    """Request for code generation."""
    task: str = Field(..., description="Description of the code to generate")
    document_id: Optional[str] = Field(default=None)
    language: str = Field(default="python", description="Programming language")
    context: Optional[str] = Field(default=None, description="Additional context")


class CodeGenerationResponse(BaseModel):
    """Response for code generation."""
    code: str
    explanation: str
    language: str
    dependencies: Optional[List[str]] = None


class AnalysisRequest(BaseModel):
    """Request for financial analysis."""
    document_id: str
    analysis_type: str = Field(
        ...,
        description="Type of analysis: categorization, forecasting, summary, anomaly_detection"
    )
    parameters: Optional[Dict[str, Any]] = Field(default=None)


class AnalysisResponse(BaseModel):
    """Response for analysis."""
    analysis_type: str
    results: Dict[str, Any]
    visualizations: Optional[List[str]] = None
    insights: List[str]
    confidence_scores: Optional[Dict[str, float]] = None


class DocumentListResponse(BaseModel):
    """Response for listing documents."""
    documents: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    environment: str
    version: str
    services: Optional[Dict[str, str]] = None