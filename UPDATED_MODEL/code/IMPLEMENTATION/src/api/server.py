"""
FastAPI server for the Temporal-Valid KG RAG System.

This module provides the HTTP API endpoints for querying the
knowledge graph. It implements the three retrieval modes and
provides health check endpoints.

Usage:
    from UPDATED_MODEL.IMPLEMENTATION.src.api.server import app
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from UPDATED_MODEL.IMPLEMENTATION.src.models import QueryRequest, AnswerResponse, RetrievedFact
from UPDATED_MODEL.IMPLEMENTATION.src.dev_urgent.urgent_retriever import urgent_retriever
from UPDATED_MODEL.IMPLEMENTATION.src.dev_urgent.urgent_generator import urgent_generator
import uuid
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Temporal-Valid KG RAG API",
    description="API for querying temporal knowledge graphs with three retrieval modes",
    version="2.0.0",
)

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns basic health status for load balancers and monitoring.
    """
    return {"status": "ok", "service": "temporal-kg-rag"}


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.

    Checks if the service is ready to accept traffic.
    """
    return {"ready": True, "status": "using_mock_data"}


@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Query the knowledge graph.

    Supports three retrieval modes:
    - pure_rag: Vector similarity search only
    - rag_kg_validator: Hybrid with KG validation
    - kg_only: Graph traversal only

    Query Parameters:
    - question: The natural language question to answer
    - mode: Retrieval mode (default: pure_rag)
    - as_of: ISO timestamp for historical query (optional)
    - include_history: Include superseded facts in results
    - k: Number of results to retrieve

    Returns:
    - answer: Generated answer with citations
    - facts: List of supporting facts
    - confidence: Overall confidence score
    - audit_id: ID for audit trail
    """
    try:
        # Parse as_of timestamp if provided
        as_of_dt = None
        if request.as_of:
            try:
                as_of_dt = datetime.fromisoformat(request.as_of.replace("Z", ""))
            except Exception:
                pass  # Use None if parsing fails

        # Execute retrieval using urgent retriever
        raw_facts = urgent_retriever.search(
            query=request.question, as_of=as_of_dt, mode=request.mode, limit=request.k
        )

        # Generate answer using urgent generator
        result = urgent_generator.generate(
            query=request.question, facts=raw_facts, mode=request.mode
        )

        # Convert to RetrievedFact format
        retrieved_facts = []
        for fact_dict in result["facts"]:
            fact = RetrievedFact(
                fact_id=fact_dict.get("fact_id", str(uuid.uuid4())),
                content=fact_dict.get("content", ""),
                source=fact_dict.get("source", "unknown"),
                as_of=fact_dict.get("as_of", datetime.utcnow().isoformat() + "Z"),
                current=fact_dict.get("current", True),
                confidence=fact_dict.get("confidence", 0.0),
                citation=fact_dict.get("citation", ""),
            )
            retrieved_facts.append(fact)

        # Create audit ID
        audit_id = str(uuid.uuid4())

        return AnswerResponse(
            answer=result["answer"],
            facts=retrieved_facts,
            mode=request.mode,
            confidence=result["confidence"],
            audit_id=audit_id,
            supported_claims=[f.content for f in retrieved_facts[:5]],
            unsupported_claims=[],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/health/detailed")
async def detailed_health():
    """
    Detailed health check with component status.
    """
    return {
        "status": "detailed",
        "components": {
            "config": "loaded",
            "mock_facts": "active",
            "retriever": "urgent",
            "generator": "urgent",
            "llm_gateway": "configured",
        },
        "mode": "demo_urgent",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
