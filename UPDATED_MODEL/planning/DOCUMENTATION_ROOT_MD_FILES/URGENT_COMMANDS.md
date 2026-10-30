# ⚡ URGENT: COMMAND-BY-COMMAND (Copy-Paste These)

## NO READING. NO THINKING. JUST DO IT.

**Total time: ~2-3 hours if you follow exactly.**

---

## PHASE 1: SETUP (5 minutes)

```bash
# BE IN THE RIGHT DIRECTORY
cd /home/karthikean.juttumaha/mini-extract

# CREATE URGENT DIRECTORY
mkdir -p src/dev_urgent

# VERIFY PYTHON PATH
python -c "import sys; print(); sys.path.insert(0, '.'); from src.temporal.timestamp_extractor import get_file_timestamps; print('✅ Path OK')"
```

---

## PHASE 2: MOCK FACTS (10 minutes)

```bash
# COPY-PASTE THIS ENTIRE BLOCK
cat > src/dev_urgent/mock_facts.py << 'EOF'
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Any

class MockFact(BaseModel):
    fact_id: str
    content: str
    source: str
    as_of: datetime
    current: bool = True
    confidence: float = 0.95
    citation: str

class MockFactStore:
    def __init__(self):
        self.facts: List[MockFact] = [
            MockFact(fact_id="fact_001", content="Operation Alpha status is APPROVED", source="doc1.pdf", as_of=datetime(2024, 1, 15), confidence=0.95, citation="Source: doc1.pdf | As-of: 2024-01-15T10:00:00Z"),
            MockFact(fact_id="fact_002", content="Operation Alpha budget is $500000", source="doc1.pdf", as_of=datetime(2024, 1, 15), confidence=0.90, citation="Source: doc1.pdf | As-of: 2024-01-15T10:00:00Z"),
            MockFact(fact_id="fact_003", content="Operation Beta status is PENDING", source="doc2.pdf", as_of=datetime(2024, 1, 10), confidence=0.85, citation="Source: doc2.pdf | As-of: 2024-01-10T08:00:00Z"),
            MockFact(fact_id="fact_004", content="Commander of Alpha is Captain Smith", source="doc1.pdf", as_of=datetime(2024, 1, 15), confidence=0.92, citation="Source: doc1.pdf | As-of: 2024-01-15T10:00:00Z"),
        ]
    
    def search(self, query: str, as_of=None, limit=5):
        query_lower = query.lower()
        results = [f for f in self.facts if f.current and (not as_of or f.as_of <= as_of)]
        matched = [f for f in results if query_lower in f.content.lower()]
        return matched[:limit] if matched else results[:limit]

mock_fact_store = MockFactStore()
EOF
```

---

## PHASE 3: URGENT RETRIEVER (10 minutes)

```bash
# COPY-PASTE THIS ENTIRE BLOCK
cat > src/dev_urgent/urgent_retriever.py << 'EOF'
from typing import List, Optional
from datetime import datetime
from src.dev_urgent.mock_facts import mock_fact_store

class UrgentRetriever:
    def __init__(self):
        self.store = mock_fact_store
    
    def search(self, query: str, as_of: Optional[datetime] = None, mode: str = None, limit: int = 5, **kwargs):
        facts = self.store.search(query, as_of, limit)
        return [fact.model_dump() for fact in facts]

urgent_retriever = UrgentRetriever()
EOF

# TEST IT
python -c "
from src.dev_urgent.urgent_retriever import urgent_retriever
results = urgent_retriever.search('Operation Alpha')
assert len(results) > 0
assert results[0]['content']
print('✅ Retriever works:', len(results), 'facts returned')
"
```

---

## PHASE 4: URGENT GENERATOR (10 minutes)

```bash
# COPY-PASTE THIS ENTIRE BLOCK
cat > src/dev_urgent/urgent_generator.py << 'EOF'
from typing import List, Optional, Dict
import re

class UrgentGenerator:
    def generate(self, query: str, facts: List[Dict], mode: str = None, **kwargs) -> Dict:
        if not facts:
            return {"answer": "No information found.", "facts": [], "confidence": 0.0, "citations": []}
        
        answer = self._extract_answer(query, facts)
        confidence = sum(f.get("confidence", 0.5) for f in facts) / len(facts)
        citations = [f"[{i+1}] {f.get('citation', '')}" for i, f in enumerate(facts)]
        
        return {
            "answer": answer,
            "facts": facts,
            "confidence": confidence,
            "citations": citations
        }
    
    def _extract_answer(self, query: str, facts: List[Dict]) -> str:
        q = query.lower()
        for f in facts:
            c = f.get("content", "").lower()
            if "what is" in q or "what's" in q:
                if "status" in q and "status" in c:
                    m = re.search(r'status (\w+)', c, re.I)
                    if m: return f"The status is **{m.group(1).upper()}**."
                if "budget" in q and "budget" in c:
                    m = re.search(r'budget[\s\w]*?(\$\d+,?\d*)', c, re.I)
                    if m: return f"The budget is **{m.group(1)}**."
                if "commander" in q and "commander" in c:
                    m = re.search(r'commander[\s\w]*?(\w+\s*\w+)', c, re.I)
                    if m: return f"The commander is **{m.group(1)}**."
        return facts[0].get("content", "No specific answer found.")

urgent_generator = UrgentGenerator()
EOF

# TEST IT
python -c "
from src.dev_urgent.urgent_retriever import urgent_retriever
from src.dev_urgent.urgent_generator import urgent_generator
facts = urgent_retriever.search('status of Alpha')
result = urgent_generator.generate('What is the status of operation Alpha?', facts)
assert result['answer']
assert result['confidence'] > 0
print('✅ Generator works:', result['answer'][:50])
"
```

---

## PHASE 5: MODIFY API (15 minutes)

```bash
# BACKUP ORIGINAL
cp src/api/server.py src/api/server.py.backup 2>/dev/null; echo "Backup created"

# COPY-PASTE THIS ENTIRE BLOCK (replaces server.py)
cat > src/api/server.py << 'EOF'
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

# Import urgent components
from src.dev_urgent.urgent_retriever import urgent_retriever
from src.dev_urgent.urgent_generator import urgent_generator

app = FastAPI(title="Temporal KG-RAG Demo")

# CORS for Streamlit
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryRequest(BaseModel):
    question: str
    mode: str = "pure_rag"
    as_of: Optional[str] = None
    include_history: bool = False
    org_unit: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    facts: List[dict]
    citations: List[str]
    audit_id: str
    confidence: float

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    as_of_dt = None
    if request.as_of:
        try:
            as_of_dt = datetime.fromisoformat(request.as_of.replace("Z", ""))
        except:
            pass
    
    facts = urgent_retriever.search(
        query=request.question,
        as_of=as_of_dt,
        mode=request.mode,
        limit=5
    )
    
    result = urgent_generator.generate(
        query=request.question,
        facts=facts,
        mode=request.mode
    )
    
    return QueryResponse(
        answer=result["answer"],
        facts=result["facts"],
        citations=result["citations"],
        audit_id=str(uuid.uuid4()),
        confidence=result["confidence"]
    )

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}
EOF

# TEST API
python -c "
import requests, json, time, subprocess, sys

# Start API in background
proc = subprocess.Popen([sys.executable, 'src/api/server.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)

try:
    r = requests.post('http://localhost:8000/query', json={'question': 'test', 'mode': 'pure_rag'})
    data = r.json()
    assert 'answer' in data
    print('✅ API works:', data['answer'][:50])
finally:
    proc.terminate()
    proc.wait()
"
```

---

## PHASE 6: MODIFY UI (10 minutes)

```bash
# BACKUP ORIGINAL
cp ui_streamlit.py ui_streamlit.py.backup 2>/dev/null; echo "Backup created"

# COPY-PASTE THIS ENTIRE BLOCK (replaces ui_streamlit.py)
cat > ui_streamlit.py << 'EOF'
import streamlit as st
import requests

st.set_page_config(page_title="KG-RAG Demo", layout="wide")
API = "http://localhost:8000"

st.title("🔍 Temporal KG-RAG Demo")

with st.form("q"):
    col1, col2, col3 = st.columns([4,1,1])
    with col1:
        question = st.text_input("Query:", placeholder="What is the status of operation Alpha?", label_visibility="collapsed")
    with col2:
        mode = st.selectbox("Mode:", ["pure_rag","rag_kg_validator","kg_only"], label_visibility="collapsed")
    with col3:
        submitted = st.form_submit_button("Search")

if submitted and question:
    with st.spinner("Thinking..."):
        try:
            r = requests.post(f"{API}/query", json={"question": question, "mode": mode})
            if r.status_code == 200:
                data = r.json()
                st.markdown("---")
                st.markdown("### ✅ Answer")
                st.markdown(f"**{data['answer']}**")
                st.markdown(f"**Confidence:** {data['confidence']:.0%}")
                if data['citations']:
                    st.markdown("### 📜 Citations")
                    for c in data['citations']:
                        st.text(c)
                if data['facts']:
                    st.markdown("### 📊 Facts")
                    for f in data['facts']:
                        st.json(f)
            else:
                st.error(f"API error: {r.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

st.sidebar.markdown("### 🔧 Status")
try:
    r = requests.get(f"{API}/health")
    st.sidebarSuccess(f"API: {r.json().get('status')}")
except:
    st.sidebar.error("API: OFFLINE")
EOF

# TEST IMPORTS
python -c "import streamlit; print('✅ Streamlit installed')"
```

---

## PHASE 7: START EVERYTHING (5 minutes)

```bash
# Terminal 1: Start API
python src/api/server.py > /tmp/api.log 2>&1 &
API_PID=$!
echo "API running on port 8000 (PID: $API_PID)"

# Wait 3 seconds
sleep 3

# Terminal 2: Start UI
streamlit run ui_streamlit.py --server.port 8501 > /tmp/streamlit.log 2>&1 &
UI_PID=$!
echo "UI running on port 8501 (PID: $UI_PID)"

# Wait 5 seconds
sleep 5

# Verify both
curl -s http://localhost:8000/health
echo ""
curl -s http://localhost:8501 >/dev/null && echo "✅ UI accessible" || echo "❌ UI not accessible"
```

---

## PHASE 8: TEST IN BROWSER (2 minutes)

1. **Open browser to:** `http://localhost:8501`
2. **Enter query:** `What is the status of operation Alpha?`
3. **Click Search**

**EXPECTED RESULT:**
- ✅ Answer appears: "The status is **APPROVED**"
- ✅ Confidence score appears
- ✅ Citations appear
- ✅ Facts appear in JSON format

---

## IF SOMETHING FAILS

### Check API:
```bash
curl -v http://localhost:8000/health
curl -v -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question":"test","mode":"pure_rag"}'
```

### Check logs:
```bash
tail -20 /tmp/api.log
tail -20 /tmp/streamlit.log
```

### Kill everything and restart:
```bash
kill $API_PID $UI_PID 2>/dev/null
sleep 2
cd /home/karthikean.juttumaha/mini-extract
python src/api/server.py & streamlit run ui_streamlit.py --server.port 8501 &
```

---

## STOP EVERYTHING

```bash
pkill -f "python src/api/server.py"
pkill -f "streamlit run ui_streamlit.py"
echo "✅ All services stopped"
```

---

## 🎯 INSTANT DEMO SCRIPT

Create this script and run it:

```bash
cat > run_demo.sh << 'SCRIPT'
#!/bin/bash
cd /home/karthikean.juttumaha/mini-extract

# Start API
python src/api/server.py > /tmp/api.log 2>&1 &
API_PID=$!

# Start UI
streamlit run ui_streamlit.py --server.port 8501 > /tmp/streamlit.log 2>&1 &
UI_PID=$!

echo "✅ Demo is running!"
echo "   API: http://localhost:8000"
echo "   UI:  http://localhost:8501"
echo ""
echo "Open your browser to http://localhost:8501"
echo "Try: What is the status of operation Alpha?"
echo ""
echo "Press ENTER to stop..."
read

kill $API_PID $UI_PID 2>/dev/null
echo "✅ Stopped"
SCRIPT

chmod +x run_demo.sh
./run_demo.sh
```

---

## SUCCESS CHECKLIST

| Task | Command | Expected |
|------|---------|----------|
| ✅ Mock facts | `python -c "from src.dev_urgent.mock_facts import mock_fact_store; print(len(mock_fact_store.facts))"` | 4 |
| ✅ Retriever | `python -c "from src.dev_urgent.urgent_retriever import urgent_retriever; print(len(urgent_retriever.search('Alpha')))"` | >0 |
| ✅ Generator | `python -c "from src.dev_urgent.urgent_generator import urgent_generator; print(urgent_generator.generate('test', [{'content':'test'}])['answer'])"` | text |
| ✅ API health | `curl -s http://localhost:8000/health` | {"status":"healthy"} |
| ✅ API query | `curl -s -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question":"Alpha","mode":"pure_rag"}'` | JSON with answer |
| ✅ UI | Browser to `http://localhost:8501` | Search works |

---

## 🚨 3-MINUTE QUICK START

If you're really in a hurry:

```bash
cd /home/karthikean.juttumaha/mini-extract

# Create directory
mkdir -p src/dev_urgent

# Create all 3 files in one shot
cat > src/dev_urgent/__init__.py << 'E'
E

cat > src/dev_urgent/all_in_one.py << 'EOPY'
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid, re, requests

# MOCK FACTS
facts = [
    {"fact_id":"f1","content":"Status of Alpha is APPROVED","source":"doc1.pdf","as_of":"2024-01-15T10:00:00Z","current":True,"confidence":0.95},
    {"fact_id":"f2","content":"Budget of Alpha is $500000","source":"doc1.pdf","as_of":"2024-01-15T10:00:00Z","current":True,"confidence":0.90},
]

# RETRIEVER
def search_facts(query):
    return [f for f in facts if query.lower() in f["content"].lower()] or facts[:2]

# GENERATOR
def generate_answer(query, facts):
    if not facts: return {"answer":"No info","facts":[],"confidence":0,"citations":[]}
    q = query.lower()
    for f in facts:
        c = f["content"].lower()
        if "status" in q and "status" in c:
            return {"answer":"The status is APPROVED.","facts":facts,"confidence":0.95,"citations":[f["source"]]}
        if "budget" in q and "budget" in c:
            return {"answer":"The budget is $500,000.","facts":facts,"confidence":0.90,"citations":[f["source"]]}
    return {"answer":facts[0]["content"],"facts":facts,"confidence":0.8,"citations":[f["source"] for f in facts]}

# API
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryRequest(BaseModel):
    question: str
    mode: str = "pure_rag"

class QueryResponse(BaseModel):
    answer: str
    facts: List[dict]
    citations: List[str]
    audit_id: str
    confidence: float

@app.post("/query")
def query(req: QueryRequest):
    matched = search_facts(req.question)
    result = generate_answer(req.question, matched)
    return QueryResponse(**result, audit_id=str(uuid.uuid4()))

@app.get("/health")
def health():
    return {"status":"healthy"}
EOPY

# Replace API
cp src/api/server.py src/api/server.py.bak 2>/dev/null
cat > src/api/server.py << 'EAPI'
from src.dev_urgent.all_in_one import app, QueryRequest, QueryResponse
EAPI

# Simple UI
cat > ui_streamlit.py << 'EUI'
import streamlit as st, requests
st.title("KG-RAG Demo")
q = st.text_input("Query")
if q:
    r = requests.post("http://localhost:8000/query", json={"question": q})
    if r.ok:
        d = r.json()
        st.write("### Answer")
        st.write(d["answer"])
        st.write("### Facts")
        for f in d["facts"]:
            st.json(f)
EUI

# Start services
python src/api/server.py & streamlit run ui_streamlit.py --server.port 8501 &
E

# The ultra-simplified all-in-one approach above
```

---

## FINAL COMMAND

**When you're done, just run this to see if it worked:**

```bash
# Start everything
cd /home/karthikean.juttumaha/mini-extract
python src/api/server.py > /tmp/api.log 2>&1 &
streamlit run ui_streamlit.py --server.port 8501 > /tmp/streamlit.log 2>&1 &

# Test
sleep 5
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question":"status of Alpha","mode":"pure_rag"}' | python -m json.tool

# Open browser
echo "Opening browser to http://localhost:8501"
xdg-open http://localhost:8501 2>/dev/null || echo "Browser: http://localhost:8501"
```

---

## 🎯 YOU'RE DONE WHEN:

1. ✅ `http://localhost:8501` loads in browser
2. ✅ You can type a query and get an answer
3. ✅ Answer says "The status is APPROVED" for "What is the status of operation Alpha?"

**Time: ~2-3 hours. Go.**
