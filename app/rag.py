import os
import requests
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

db_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AWS Customer Agreement.pdf"))

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
_db = None

def get_vectorstore():
    global _db
    if _db is not None:
        return _db
    
    if os.path.exists(db_dir) and len(os.listdir(db_dir)) > 0:
        _db = Chroma(persist_directory=db_dir, embedding_function=embeddings)
        return _db
    return None

def ingest_pdf():
    global _db
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"pdf not found at: {pdf_path}")
    
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len
    )
    chunks = splitter.split_documents(docs)
    
    _db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_dir
    )
    return len(chunks)

def query_rag(query_text: str, k: int = 10):
    db = get_vectorstore()
    if db is None:
        raise ValueError("database empty, ingest pdf first.")
    
    results = db.similarity_search_with_score(query_text, k=k)
    
    sources = []
    context_parts = []
    
    for i, (doc, score) in enumerate(results):
        snippet = doc.page_content
        page_num = doc.metadata.get("page", 0) + 1
        sources.append({
            "content": snippet,
            "metadata": {
                "page": page_num,
                "score": float(score)
            }
        })
        context_parts.append(f"[Chunk {i+1} | Page {page_num}]:\n{snippet}")
        
    context = "\n\n".join(context_parts)
    
    system_prompt = (
        "You are an assistant trained to answer questions about the AWS Customer Agreement.\n"
        "Your task is to answer the user query based ONLY on the provided context.\n"
        "If the context does not contain the answer or is not relevant to the query, you must respond with exactly: 'Answer not found in context.' and do not explain or add anything else.\n"
        "Do not hallucinate or make assumptions. Keep your answer factual, direct, and concise.\n"
        "Do not refer to the context as 'the text' or 'the context' in the final response if you can avoid it; just state the facts."
    )
    
    provider = os.getenv("LLM_PROVIDER", "groq").lower().strip()
    
    if provider == "ollama":
        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434").rstrip("/")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2").strip()
        url = f"{ollama_endpoint}/api/chat"
        payload = {
            "model": ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query_text}"}
            ],
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=45)
            response.raise_for_status()
            res_data = response.json()
            answer = res_data["message"]["content"].strip()
        except Exception as e:
            answer = f"failed to query ollama api: {str(e)}"
            
    else:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set. check your .env file.")
            
        groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query_text}"}
            ],
            "temperature": 0.0
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            res_data = response.json()
            answer = res_data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            answer = f"failed to query groq api: {str(e)}"
    
    answer_found = True
    if "Answer not found in context" in answer or answer.strip() == "Answer not found in context.":
        answer_found = False
        answer = "Answer not found in context."
        
    return answer, sources, answer_found
