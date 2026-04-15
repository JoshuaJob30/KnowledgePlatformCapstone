# app/services/memory_service.py
import os, json
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DATA_DIR = "data/memory"
os.makedirs(DATA_DIR, exist_ok=True)

STM_PATH = os.path.join(DATA_DIR, "stm.json")
EPI_PATH = os.path.join(DATA_DIR, "episodes.json")
LTM_PATH = os.path.join(DATA_DIR, "ltm.json")

_embedding_model = None
_stm_vs = None
_epi_vs = None
_ltm_vs = None

def _get_embedding():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embedding_model

def _load_json(path, default):
    try:
        return json.load(open(path)) if os.path.exists(path) else default
    except:
        return default

_stm_texts = _load_json(STM_PATH, [])
_episodes = _load_json(EPI_PATH, [])
_ltm_facts = _load_json(LTM_PATH, [])

def stm_add(msg: str):
    if not msg: return
    _stm_texts.append(msg)
    _stm_texts[:] = _stm_texts[-40:]
    global _stm_vs
    _stm_vs = Chroma.from_texts(_stm_texts, _get_embedding(),
                                persist_directory=os.path.join(DATA_DIR,"chroma_stm"))
    _stm_vs.persist()
    json.dump(_stm_texts, open(STM_PATH,"w"))

def epi_add(summary: str):
    if not summary: return
    _episodes.append(summary)
    _episodes[:] = _episodes[-50:]
    global _epi_vs
    _epi_vs = Chroma.from_texts(_episodes, _get_embedding(),
                                persist_directory=os.path.join(DATA_DIR,"chroma_epi"))
    _epi_vs.persist()
    json.dump(_episodes, open(EPI_PATH,"w"))

def ltm_add_facts(facts):
    cleaned = [f.strip() for f in facts if f and f.strip()]
    for f in cleaned:
        if f not in _ltm_facts:
            _ltm_facts.append(f)
    global _ltm_vs
    _ltm_vs = Chroma.from_texts(_ltm_facts, _get_embedding(),
                                persist_directory=os.path.join(DATA_DIR,"chroma_ltm"))
    _ltm_vs.persist()
    json.dump(_ltm_facts, open(LTM_PATH,"w"))

# Added getters so memory_agent can read
def get_recent_queries(limit: int = 10):
    return _stm_texts[-limit:]

def get_durable_facts():
    return _ltm_facts

def get_episodic_memories(limit: int = 3):
    return _episodes[-limit:]

# Added clear function
def clear_memory():
    """Reset all memory stores and JSON files safely."""
    global _stm_texts, _episodes, _ltm_facts, _stm_vs, _epi_vs, _ltm_vs
    _stm_texts = []
    _episodes = []
    _ltm_facts = []
    _stm_vs = None
    _epi_vs = None
    _ltm_vs = None
    # Overwrite JSON files with empty lists
    json.dump(_stm_texts, open(STM_PATH, "w"))
    json.dump(_episodes, open(EPI_PATH, "w"))
    json.dump(_ltm_facts, open(LTM_PATH, "w"))
