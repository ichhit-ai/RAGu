import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(
    page_title="RAGu - Legal Q&A & Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 80% 10%, rgba(99, 102, 241, 0.07), transparent 45%),
                radial-gradient(circle at 10% 90%, rgba(236, 72, 153, 0.04), transparent 45%),
                #09090b;
}

.metric-card {
    background: rgba(24, 24, 27, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-card:hover {
    transform: translateY(-5px);
    border-color: rgba(99, 102, 241, 0.35);
    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.12);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}
.metric-label {
    font-size: 0.85rem;
    color: #a1a1aa;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 500;
}

.main-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 30%, #a1a1aa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.subtitle {
    font-size: 1.1rem;
    color: #a1a1aa;
    margin-bottom: 30px;
}

.source-card {
    background: rgba(24, 24, 27, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 4px solid #6366f1;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 12px;
}
.source-meta {
    display: flex;
    gap: 15px;
    margin-bottom: 8px;
}
.source-badge {
    background: rgba(99, 102, 241, 0.15);
    color: #c7d2fe;
    border: 1px solid rgba(99, 102, 241, 0.3);
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
.source-score {
    background: rgba(244, 63, 94, 0.1);
    color: #fca5a5;
    border: 1px solid rgba(244, 63, 94, 0.2);
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
.source-content {
    font-size: 0.9rem;
    color: #d4d4d8;
    line-height: 1.5;
}

div.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
    color: white;
}
div.stButton > button:active {
    transform: translateY(0);
}

.config-card {
    background: rgba(39, 39, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
}
.config-title {
    font-weight: 600;
    color: #f4f4f5;
    margin-bottom: 5px;
}
.config-value {
    color: #a1a1aa;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

def render_kpi_card(value, label):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=80)
    st.markdown("### **RAGu Assistant**")
    st.markdown("An enterprise AI-driven Q&A system trained on the *AWS Customer Agreement* with real-time request analytics.")
    st.markdown("---")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        if response.status_code == 200:
            st.success("🟢 API Server: Online")
        else:
            st.warning("🟡 API Server: Issue")
    except Exception:
        st.error("🔴 API Server: Offline")
        
    st.markdown("---")
    st.caption("developed by junior ai developer")

st.markdown('<div class="main-title">RAGu Document Q&A & Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Search the AWS Customer Agreement and inspect usage aggregates in real time.</div>', unsafe_allow_html=True)

tab_chat, tab_analytics, tab_config = st.tabs([
    "💬 Q&A Document Chat", 
    "📊 Usage Analytics", 
    "⚙️ System Architecture"
])

with tab_chat:
    st.markdown("### Ask a Question about the AWS Customer Agreement")
    st.markdown("Ask anything about terms, termination, user responsibilities, or liability. The system will retrieve relevant agreement chunks and generate a factual response.")
    
    chat_container = st.container()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message and message["sources"]:
                    with st.expander("🔍 View Retrieved Sources"):
                        for src in message["sources"]:
                            st.markdown(f"""
                            <div class="source-card">
                                <div class="source-meta">
                                    <span class="source-badge">Page {src['metadata']['page']}</span>
                                    <span class="source-score">Relevance: {1 - src['metadata']['score']:.4f}</span>
                                </div>
                                <div class="source-content">{src['content']}</div>
                            </div>
                            """, unsafe_allow_html=True)

    user_query = st.chat_input("What is the governing law of the agreement?")
    
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_query)
                
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.markdown("🧠 *Analyzing document and retrieving context...*")
                
                try:
                    res = requests.post(f"{API_URL}/ask", json={"query": user_query}, timeout=45)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data["answer"]
                        sources = data["sources"]
                        latency = data["latency"]
                        found = data["answer_found"]
                        
                        response_placeholder.markdown(answer)
                        
                        if sources and found:
                            with st.expander("🔍 View Retrieved Sources"):
                                for src in sources:
                                    st.markdown(f"""
                                    <div class="source-card">
                                        <div class="source-meta">
                                            <span class="source-badge">Page {src['metadata']['page']}</span>
                                            <span class="source-score">Relevance: {1 - src['metadata']['score']:.4f}</span>
                                        </div>
                                        <div class="source-content">{src['content']}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources if found else []
                        })
                        
                        st.caption(f"⏱️ Response Latency: {latency:.2f}s | Source Chunks: {len(sources)}")
                    else:
                        err_msg = f"⚠️ Error {res.status_code}: {res.text}"
                        response_placeholder.error(err_msg)
                        st.session_state.messages.append({"role": "assistant", "content": err_msg})
                except Exception as e:
                    err_msg = f"⚠️ Connection Error: Failed to reach FastAPI backend. Details: {str(e)}"
                    response_placeholder.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})

with tab_analytics:
    st.markdown("### System Log Analytics")
    st.markdown("These stats are generated live by executing aggregations against the SQLite logs database.")
    
    try:
        res = requests.get(f"{API_URL}/analytics", timeout=5)
        if res.status_code == 200:
            analytics_data = res.json()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                render_kpi_card(analytics_data["total_queries"], "Total Queries Handled")
            with col2:
                render_kpi_card(f"{analytics_data['avg_latency']:.3f} s", "Avg Response Latency")
            with col3:
                render_kpi_card(len(analytics_data.get("unresolved_queries", [])), "Out-of-Scope Queries Blocked")
                
            st.markdown("---")
            
            v_col1, v_col2 = st.columns(2)
            
            with v_col1:
                st.markdown("#### 📈 Response Latency History (Last 50 queries)")
                history = analytics_data["latency_history"]
                if history:
                    df_history = pd.DataFrame(history)
                    df_history["timestamp"] = pd.to_datetime(df_history["timestamp"])
                    df_history["Status"] = df_history["answer_found"].map({True: "Answer Resolved", False: "Unresolved / Out-of-scope"})
                    
                    fig_latency = px.area(
                        df_history, 
                        x="timestamp", 
                        y="latency",
                        color="Status",
                        color_discrete_map={"Answer Resolved": "#6366f1", "Unresolved / Out-of-scope": "#f43f5e"},
                        labels={"latency": "Latency (seconds)", "timestamp": "Query Timestamp"},
                        template="plotly_dark"
                    )
                    fig_latency.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=20, r=20, t=10, b=20),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_latency, use_container_width=True)
                else:
                    st.info("No latency history available yet.")
                    
            with v_col2:
                st.markdown("#### 📊 Most Frequently Asked Questions")
                freq = analytics_data["frequent_queries"]
                if freq:
                    df_freq = pd.DataFrame(freq)
                    fig_freq = px.bar(
                        df_freq,
                        x="count",
                        y="query",
                        orientation="h",
                        color="count",
                        color_continuous_scale=["#818cf8", "#4f46e5"],
                        labels={"count": "Times Asked", "query": "Query"},
                        template="plotly_dark"
                    )
                    fig_freq.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        coloraxis_showscale=False,
                        margin=dict(l=20, r=20, t=10, b=20),
                        yaxis={'categoryorder':'total ascending'}
                    )
                    fig_freq.update_yaxes(tickmode="array", tickvals=df_freq["query"], ticktext=df_freq["query"].str.wrap(40))
                    st.plotly_chart(fig_freq, use_container_width=True)
                else:
                    st.info("No frequent queries recorded yet.")
                    
            st.markdown("---")
            
            st.markdown("#### ❌ Queries Where Answer Was Not Found in Context")
            unresolved = analytics_data["unresolved_queries"]
            if unresolved:
                df_unresolved = pd.DataFrame(unresolved)
                df_unresolved.columns = ["Out-of-Scope Query", "Logged Timestamp", "Latency (s)"]
                st.dataframe(
                    df_unresolved,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("All queries so far have been successfully resolved inside context!")
                
        else:
            st.error(f"Failed to fetch analytics from backend. Server returned HTTP {res.status_code}")
    except Exception as e:
        st.error(f"Failed to retrieve analytics. API server connection error: {str(e)}")

with tab_config:
    st.markdown("### System Architecture & Pipeline Configurations")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown('<div class="config-title">📂 Document Ingestion Source</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-value">AWS Customer Agreement (PDF)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown('<div class="config-title">✂️ Text Splitter Strategy</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-value">RecursiveCharacterTextSplitter<br><b>Chunk Size:</b> 800 characters<br><b>Chunk Overlap:</b> 150 characters</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown('<div class="config-title">🧠 Embeddings Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-value">Hugging Face <code>all-MiniLM-L6-v2</code> (384-dimensional dense vectors)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_b:
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown('<div class="config-title">🗄️ Vector Database Store</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-value">ChromaDB (Local persistent sqlite3 engine)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        provider = os.getenv("LLM_PROVIDER", "groq").lower().strip()
        if provider == "ollama":
            endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            provider_desc = f"Local Ollama Server<br><b>Endpoint:</b> {endpoint}<br><b>Model:</b> <code>{model}</code><br><b>Temperature:</b> 0.0"
        else:
            model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            provider_desc = f"Groq Cloud API<br><b>Model:</b> <code>{model}</code><br><b>Temperature:</b> 0.0"

        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown('<div class="config-title">🤖 LLM Orchestration Server</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="config-value">{provider_desc}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown('<div class="config-title">📊 SQL Logging Engine</div>', unsafe_allow_html=True)
        st.markdown('<div class="config-value">SQLite database <code>app/query_logs.db</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        st.markdown("#### Re-run Document Ingestion")
        st.markdown("If you want to clear and re-ingest the document PDF, click the button below. This will reload the PDF, partition it, calculate new embeddings, and rebuild the vector database.")
        if st.button("🔄 Trigger Document Ingestion"):
            with st.spinner("Processing PDF, generating embeddings, and updating index..."):
                try:
                    res = requests.post(f"{API_URL}/ingest", timeout=60)
                    if res.status_code in [200, 201]:
                        data = res.json()
                        st.success(f"Ingestion Succeeded! Split document into {data['num_chunks']} vector snippets.")
                    else:
                        st.error(f"Ingestion failed. Server response HTTP {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Could not connect to FastAPI server. Ingestion failed: {str(e)}")
                    
    with col_btn2:
        st.markdown("#### Reset Analytics Logs")
        st.markdown("Delete all logged query history, response times, and chat metrics from the SQLite database to start fresh.")
        if st.button("🗑️ Clear Analytics Database"):
            try:
                res = requests.delete(f"{API_URL}/analytics", timeout=10)
                if res.status_code == 200:
                    st.success("Database cleared successfully! Refresh the page to see changes.")
                else:
                    st.error(f"Failed to clear database. Server response HTTP {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI server. Reset failed: {str(e)}")

