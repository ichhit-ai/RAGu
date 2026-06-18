import time
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, log_query, get_analytics, clear_db
from app.rag import ingest_pdf, query_rag, get_vectorstore
from app.schemas import QueryRequest, QueryResponse, AnalyticsResponse, SourceSnippet

app = FastAPI(
    title="RAGu API Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_handler():
    init_db()

@app.get("/")
def index():
    return {"status": "ok", "message": "rag backend is online"}

@app.post("/ingest", status_code=status.HTTP_201_CREATED)
def handle_ingest():
    try:
        # Clear the SQLite query log analytics database first
        clear_db()
        chunks_count = ingest_pdf()
        return {"message": "pdf ingested successfully", "num_chunks": chunks_count}
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ingestion failed: {str(e)}"
        )

@app.post("/ask", response_model=QueryResponse)
def handle_ask(req: QueryRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="query cannot be empty"
        )
    
    if get_vectorstore() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="vector database is empty. run /ingest first"
        )
        
    start_time = time.time()
    try:
        answer, sources, answer_found = query_rag(query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"rag execution failed: {str(e)}"
        )
    latency = time.time() - start_time
    
    try:
        log_query(query, answer, sources, latency, answer_found)
    except Exception as e:
        print(f"warning: failed to log query: {e}")
        
    snippets = [
        SourceSnippet(content=s["content"], metadata=s["metadata"])
        for s in sources
    ]
    
    return QueryResponse(
        answer=answer,
        sources=snippets,
        latency=latency,
        answer_found=answer_found
    )

@app.get("/analytics", response_model=AnalyticsResponse)
def handle_analytics():
    try:
        return get_analytics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to fetch analytics: {str(e)}"
        )

@app.delete("/analytics")
def handle_clear_analytics():
    try:
        clear_db()
        return {"message": "analytics database cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to clear analytics database: {str(e)}"
        )
