import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(__file__), "query_logs.db")

def init_db():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT NOT NULL,
            latency REAL NOT NULL,
            answer_found BOOLEAN NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_query(query: str, answer: str, sources: list, latency: float, answer_found: bool):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (query, answer, sources, latency, answer_found)
        VALUES (?, ?, ?, ?, ?)
    """, (query, answer, json.dumps(sources), latency, 1 if answer_found else 0))
    conn.commit()
    conn.close()

def get_analytics():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*), AVG(latency) FROM logs")
    total_queries, avg_latency = cur.fetchone()
    total_queries = total_queries or 0
    avg_latency = avg_latency or 0.0
    
    cur.execute("""
        SELECT query, COUNT(*) as cnt 
        FROM logs 
        GROUP BY query 
        ORDER BY cnt DESC 
        LIMIT 10
    """)
    frequent = [{"query": row[0], "count": row[1]} for row in cur.fetchall()]
    
    cur.execute("""
        SELECT query, timestamp, latency 
        FROM logs 
        WHERE answer_found = 0 
        ORDER BY timestamp DESC
    """)
    unresolved = [{"query": row[0], "timestamp": row[1], "latency": row[2]} for row in cur.fetchall()]
    
    cur.execute("SELECT COUNT(*) FROM logs WHERE answer_found = 1")
    answered_count = cur.fetchone()[0] or 0
    success_rate = (answered_count / total_queries * 100) if total_queries > 0 else 0.0
    
    cur.execute("SELECT id, timestamp, latency, answer_found FROM logs ORDER BY id DESC LIMIT 50")
    history = [{"id": row[0], "timestamp": row[1], "latency": row[2], "answer_found": bool(row[3])} for row in cur.fetchall()]
    history.reverse()

    conn.close()
    
    return {
        "total_queries": total_queries,
        "avg_latency": avg_latency,
        "success_rate": success_rate,
        "frequent_queries": frequent,
        "unresolved_queries": unresolved,
        "latency_history": history
    }
