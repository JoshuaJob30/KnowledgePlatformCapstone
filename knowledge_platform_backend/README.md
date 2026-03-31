Knowledge Platform Backend

Overview:
This is the FastAPI backend for the Knowledge Platform Capstone. It handles:
Document ingestion (PDF, DOCX, TXT, CSV, Excel).
Query routing via specialized agents (calculator, finance, healthcare, shopping, code, search).
RAG pipeline orchestration (Planner → Retriever → Executor → Critic → Memory).
Safety guardrails (blocklist + regex).
Vector search with FAISS and HuggingFace embeddings.
Memory persistence with Chroma.

Requirements:
Python 3.11+
Dependencies listed in requirements.txt

Setup:
# Clone repo
git clone https://github.com/JoshuaJob30/KnowledgePlatformCapstone.git
cd KNOWLEDGE_PLATFORM_BACKEND
# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
# Install dependencies
pip install -r requirements.txt

Run Locally:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000