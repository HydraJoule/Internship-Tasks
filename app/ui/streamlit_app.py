import streamlit as st
import os
import uuid
import tempfile
import json
from app.config import settings
from app.rag.pdf_ingestor import PDFIngestor
from app.rag.chunker import TextChunker
from app.rag.vector_store import VectorStoreManager
from app.graph.builder import compiled_graph
from app.hitl.escalation import ESCALATION_FILE

# Set Page Config
st.set_page_config(page_title="Support Assistant", layout="wide")

# Initialize managers
@st.cache_resource
def get_managers():
    chunker = TextChunker()
    vsm = VectorStoreManager()
    return chunker, vsm

chunker, vsm = get_managers()

# Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🤖 Dynamic RAG Support Assistant")

# ====== SIDEBAR ======
with st.sidebar:
    st.header("Workspace Config")
    st.write(f"Session ID: `{st.session_state.session_id}`")
    
    st.subheader("Upload PDFs")
    uploaded_files = st.file_uploader(
        "Upload knowledge base PDFs", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    if st.button("Process & Index Documents"):
        if uploaded_files:
            with st.spinner("Extracting, Chunking, and Indexing..."):
                all_chunks = []
                for file in uploaded_files:
                    # Save temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(file.read())
                        tmp_path = tmp.name
                        
                    # Process
                    try:
                        pages_data = PDFIngestor.process_pdf(tmp_path, st.session_state.session_id, file.name)
                        doc_chunks = chunker.chunk_documents(pages_data)
                        all_chunks.extend(doc_chunks)
                        if file.name not in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.append(file.name)
                    finally:
                        os.unlink(tmp_path)
                
                # Ingest to Chroma
                if all_chunks:
                    vsm.ingest_chunks(st.session_state.session_id, all_chunks)
                    st.success(f"Successfully indexed {len(all_chunks)} chunks from {len(uploaded_files)} files!")
        else:
            st.warning("Please upload files first.")

    if st.button("Clear Workspace / Reset API"):
        vsm.clear_session(st.session_state.session_id)
        st.session_state.uploaded_files = []
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4()) # New Session
        st.success("Workspace reset! New Session ID Generated.")

    st.subheader("HITL Reviewer Dashboard")
    try:
        if os.path.exists(ESCALATION_FILE):
             with open(ESCALATION_FILE, "r") as f:
                 tickets = json.load(f)
                 pending = [t for t in tickets if t["status"] == "pending"]
                 if pending:
                     st.warning(f"Pending Escalations: {len(pending)}")
                     for p in pending:
                         st.write(f"**Query:** {p['query']}")
                         st.write(f"**Intent:** {p['intent']}")
                         if st.button(f"Resolve Ticket {p['ticket_id'][:6]}", key=p['ticket_id']):
                             from app.hitl.reviewer import resolve_escalation
                             resolve_escalation(p["ticket_id"], "Resolved by simulated agent")
                             st.success("Ticket Resolved!")
                             st.rerun()
                 else:
                     st.info("No pending escalations.")
    except Exception:
        pass


# ====== MAIN CHAT UI ======
st.header("Chat with your Data")

# Display History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("View Sources"):
                for s in msg["sources"]:
                    st.write(f"- {s}")

if query := st.chat_input("Ask a question based on uploaded documents..."):
    # Show User query
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Process via LangGraph
    with st.chat_message("assistant"):
        with st.spinner("Analyzing and Routing..."):
            initial_state = {
                "session_id": st.session_state.session_id,
                "user_query": query,
                "uploaded_files": st.session_state.uploaded_files,
                "retrieved_chunks": [],
                "sources": []
            }
            
            # Execute Graph
            result_state = compiled_graph.invoke(initial_state)
            
            response = result_state.get("final_response", "Error generating response.")
            intent = result_state.get("intent", "N/A")
            route = result_state.get("route", "N/A")
            sources = result_state.get("sources", [])
            
            # Display results
            st.markdown(response)
            
            with st.expander(f"Debug Info (Intent: {intent} | Route: {route})"):
                st.write("**Evaluation Sufficient:**", result_state.get("context_sufficient", False))
                if sources:
                    st.write("**Sources Retrieved:**")
                    for s in sources:
                        st.write(f"- {s}")
                if result_state.get("escalation_required"):
                    st.error("Escalation Ticket Created in System")

            # Update history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "sources": sources
            })
