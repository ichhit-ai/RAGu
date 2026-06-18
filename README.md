# RAGu: RAG-based Document Q&A System with Analytics Dashboard

An end-to-end Retrieval-Augmented Generation (RAG) system built over the **AWS Customer Agreement** (PDF). The system consists of a FastAPI backend with SQL-based interaction logging and a polished Streamlit analytics dashboard.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[AWS Customer Agreement.pdf] -->|Parse & Chunk| B[Recursive Text Splitter]
    B -->|Generate Embeddings| C[all-MiniLM-L6-v2]
    C -->|Store Vectors| D[ChromaDB Local Vector Store]
    
    E[User Query] -->|Ask / Retrieve| F[FastAPI Backend]
    F -->|Similarity Search| D
    D -->|Context Chunks| F
    F -->|Construct Prompt| G[Groq Cloud API / Local Ollama]
    G -->|Generate Answer| F
    
    F -->|Log Interaction| H[(SQLite Database)]
    F -->|Return Response| I[Streamlit Dashboard UI]
    I -->|Fetch Stats| H
```

The system is designed to be highly modular and support two backend LLM orchestration options:
1. **Groq Cloud API (Default / Recommended)**: Queries the cloud endpoint using `llama-3.1-8b-instant` for ultra-fast, sub-second responses.
2. **Local Ollama Server**: Compatible with local models like `llama3.2` running on localhost (ideal for offline, private deployments).

---

## 🛠️ Key Design Decisions & Assumptions

### 1. Chunking Strategy
- **Chunk Size**: `800` characters.
- **Chunk Overlap**: `150` characters.
- **Justification**: Legal agreements contain highly structured, dense, and clause-specific sections. If the chunk size is too small (e.g., 200 characters), it partitions sections mid-sentence or mid-definition, losing vital contextual details. If it is too large (e.g., 3000 characters), irrelevant clauses contaminate the prompt context and increase inference latency. An 800-character chunk ensures legal clauses fit within the context, while a 150-character overlap prevents critical boundaries from being truncated at chunk splits.

### 2. Model & Embedding Selections
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors). It runs completely locally on CPU/GPU, is extremely lightweight, and produces high-quality semantic representations.
- **LLM Options**:
  - **Groq API**: `llama-3.1-8b-instant` (8 Billion parameters) via environment variables. Extremely low latency (sub-second answers).
  - **Ollama**: `llama3.2:latest` (3 Billion parameters) running locally.
- **Safety/Hallucination Guardrails**: The system prompt forces the LLM to reply with exactly `"Answer not found in context."` when the retrieved context lacks the answer. The backend tracks this to flag queries as out-of-scope in the logs.

---

## 🚀 Installation & Setup (After Cloning)

If you have cloned this repository, follow these steps to run it locally:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key (.env)
Create a new file named **`.env`** in the root of the project (at the same level as `frontend.py` and `app/`). Inside `.env`, add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```
*(Note: `.env` is already configured in `.gitignore` so your API key will never be committed to Git).*

### 3. Run FastAPI Backend
Start the backend server on port 8000:
```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*The server will automatically initialize the SQLite log database (`app/query_logs.db`).*

### 4. Ingest the Document
Trigger the PDF parsing and ingestion into ChromaDB by sending a POST request:
```bash
curl -X POST http://127.0.0.1:8000/ingest
```

### 5. Seed Test Queries (Optional)
Run the script to populate the analytics dashboard with realistic test logs:
```bash
python3 seed_logs.py
```

### 6. Start the Streamlit Dashboard UI
Run the frontend in a separate terminal:
```bash
python3 -m streamlit run frontend.py --server.port 8501 --server.address 127.0.0.1
```
Open **`http://127.0.0.1:8501`** in your web browser.

---

## 📈 API Endpoints Reference

### 1. `POST /ingest`
- **Description**: Parses, chunks, embeds, and saves the `AWS Customer Agreement.pdf` text in ChromaDB.
- **Response**:
  ```json
  {
    "message": "PDF ingested successfully",
    "num_chunks": 99
  }
  ```

### 2. `POST /ask`
- **Request Body**:
  ```json
  {
    "query": "What is the governing law of the agreement?"
  }
  ```
- **Response**:
  ```json
  {
    "answer": "The governing law of the agreement is the laws of the State of Washington, without reference to conflict of laws principles...",
    "sources": [
      {
        "content": "...Governing Law. The laws of the State of Washington, without reference to conflict of laws principles, govern this Agreement...",
        "metadata": {
          "page": 11,
          "score": 0.3541
        }
      }
    ],
    "latency": 0.25,
    "answer_found": true
  }
  ```
