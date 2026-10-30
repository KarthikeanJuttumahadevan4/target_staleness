---
format: html
---

# ⚡ URGENT 2-HOUR DEVELOPER PLAN - Get UI Working NOW

## ⏰ SITUATION: We Have Hours, Not Days

**The architect's 2-week plan is too slow. We need the UI working in 2-6 hours.**

Instead of building the full ingestion pipeline (D1-D5), we'll **bypass it with hardcoded data** and connect only what's necessary for the UI to display answers.

---

## 🎯 END GOAL (2 Hours from Now)

User can:
1. Open UI in browser
2. Type: "What is the current status of operation Alpha?"
3. See answer: "The current status of operation Alpha is APPROVED"
4. See citation: "Source: document_1.pdf, As-of: 2024-01-15, Confidence: 0.95"

---

## 🚀 FAST PATH STRATEGY

**Bypass:** D1-D5 (Intake, Extraction, Reconstruction, Databases, Indexing)  
**Implement:** Mock data store + retrieval connection + generation + API + UI

```
USER → UI → API → GENERATION → OUTPUT
       ↑              ↑
       |              |
       ↓              ↓
     BROWSER      Mock Facts Store ← RETRIEVAL (modified)
```

---

## ⏱️ HOUR-BY-HOUR BATTLE PLAN

---

## HOUR 0: PREP (15 minutes)

### Step 0.1: Verify Existing Code (5 min)
Run these commands to see what's working:

```bash
cd /home/karthikean.juttumaha/mini-extract

# Check imports
python -c "from src.temporal.timestamp_extractor import get_file_timestamps; print('✅ temporal')"
python -c "from src.retrieval.pure_rag import PureRAGRetriever; print('✅ retrieval')"
python -c "from src.api.server import app; print('✅ api')"
python -c "import streamlit; print('✅ streamlit')"

# Check what retrieval expects
python -c "
from src.retrieval.pure_rag import PureRAGRetriever
import inspect
print(inspect.getsource(PureRAGRetriever.search))
" 2>/dev/null | head -20
```

### Step 0.2: Identify the API Contract (5 min)
Check what the API expects and what UI expects:

```bash
# Check API server
cat src/api/server.py

# Check UI
head -50 ui_streamlit.py

# Check models
cat src/models.py | grep -A 20 "class Query"
```

### Step 0.3: Create Workspace (5 min)
```bash
# Create a temporary dev directory
mkdir -p src/dev_urgent

# Create a tracking file
cat > src/dev_urgent/PROGRESS.md << 'EOF'
# Urgent Developer Progress

## Hour 0: Prep
- [ ] Step 0.1: Verify imports
- [ ] Step 0.2: Identify API contract
- [ ] Step 0.3: Create workspace

## Hour 1: Mock Data
- [ ] Step 1.1: Create mock facts
- [ ] Step 1.2: Modify retrieval to use mocks
- [ ] Step 1.3: Verify retrieval returns facts

## Hour 2: Generation + API
- [ ] Step 2.1: Create simple answer generator
- [ ] Step 2.2: Connect API endpoint
- [ ] Step 2.3: Verify API returns answers

## Hour 3: UI Connection
- [ ] Step 3.1: Modify UI to use API
- [ ] Step 3.2: Start services
- [ ] Step 3.3: End-to-end test
EOF
```

---

## HOUR 1: MOCK DATA & RETRIEVAL (45 minutes)

### Step 1.1: Create Mock Facts Store (15 min)
Create a simple in-memory fact store that the retrieval modules can use:

```bash
cat > src/dev_urgent/mock_facts.py << 'PYEOF'
"""
Mock Fact Store - Bypasses the full ingestion pipeline.
Provides hardcoded facts for immediate testing.
"""
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel


class MockFact(BaseModel):
    """Simplified fact model matching RetrievedFact structure."""
    fact_id: str
    content: str
    source: str
    as_of: datetime
    current: bool = True
    confidence: float = 0.95
    citation: str
    entity_id: str = None
    predicate: str = None
    object_value: Any = None


class MockFactStore:
    """In-memory store of mock facts."""
    
    def __init__(self):
        self.facts: List[MockFact] = []
        self._initialize_facts()
    
    def _initialize_facts(self):
        """Create hardcoded facts for demo."""
        now = datetime.utcnow()
        
        self.facts = [
            MockFact(
                fact_id="fact_001",
                content="Operation Alpha has status APPROVED",
                source="document_1.pdf",
                as_of=datetime(2024, 1, 15, 10, 0, 0),
                current=True,
                confidence=0.95,
                citation="Source: document_1.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
                entity_id="operation_alpha",
                predicate="status",
                object_value="APPROVED",
            ),
            MockFact(
                fact_id="fact_002",
                content="Operation Alpha budget is $500,000",
                source="document_1.pdf",
                as_of=datetime(2024, 1, 15, 10, 0, 0),
                current=True,
                confidence=0.90,
                citation="Source: document_1.pdf, p.2 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
                entity_id="operation_alpha",
                predicate="budget",
                object_value="$500,000",
            ),
            MockFact(
                fact_id="fact_003",
                content="Operation Beta has status PENDING",
                source="document_2.pdf",
                as_of=datetime(2024, 1, 10, 8, 0, 0),
                current=True,
                confidence=0.85,
                citation="Source: document_2.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-10T08:00:00Z",
                entity_id="operation_beta",
                predicate="status",
                object_value="PENDING",
            ),
            MockFact(
                fact_id="fact_004",
                content="The commander of operation Alpha is Captain Smith",
                source="document_1.pdf",
                as_of=datetime(2024, 1, 15, 10, 0, 0),
                current=True,
                confidence=0.92,
                citation="Source: document_1.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
                entity_id="operation_alpha",
                predicate="commander",
                object_value="Captain Smith",
            ),
        ]
    
    def search(self, query: str, as_of: datetime = None, mode: str = None, limit: int = 5) -> List[MockFact]:
        """
        Search mock facts by query.
        Simple keyword matching for demo purposes.
        """
        query_lower = query.lower()
        
        # Filter by temporal constraints
        if as_of:
            results = [f for f in self.facts if f.current and f.as_of <= as_of]
        else:
            results = [f for f in self.facts if f.current]
        
        # Simple keyword matching
        matched = []
        for fact in results:
            if query_lower in fact.content.lower():
                matched.append(fact)
        
        # If no matches, return top facts
        if not matched:
            matched = results[:limit]
        
        return matched[:limit]
    
    def get_current_facts(self, entity_id: str = None) -> List[MockFact]:
        """Get all current facts, optionally filtered by entity."""
        results = [f for f in self.facts if f.current]
        if entity_id:
            results = [f for f in results if f.entity_id == entity_id]
        return results


# Global singleton
mock_fact_store = MockFactStore()
PYEOF
```

### Step 1.2: Modify Retrieval to Use Mock Facts (20 min)
Modify one retrieval module to use our mock facts. Start with `pure_rag.py`:

```bash
# First, check current structure
cat src/retrieval/pure_rag.py
```

Then modify it to use mock facts (create a new version thatspin the existing one):

```bash
cat > src/dev_urgent/pure_rag_urgent.py << 'PYEOF'
"""
Urgent version of Pure RAG that uses mock facts.
Bypasses Qdrant and KG for immediate demo.
"""
from typing import List, Optional, Any
from datetime import datetime
from src.dev_urgent.mock_facts import mock_fact_store, MockFact


class UrgentPureRAGRetriever:
    """Temporary retrieval using mock facts."""
    
    def __init__(self):
        self.fact_store = mock_fact_store
    
    def search(
        self,
        query: str,
        as_of: Optional[datetime] = None,
        mode: Optional[str] = None,
        limit: int = 5,
        **kwargs
    ) -> List[dict]:
        """
        Search mock facts and return in expected format.
        Format matches what the system expects for RetrievedFact.
        """
        facts = self.fact_store.search(query, as_of, mode, limit)
        
        # Convert to dict format expected by the system
        results = []
        for fact in facts:
            results.append({
                "fact_id": fact.fact_id,
                "content": fact.content,
                "source": fact.source,
                "as_of": fact.as_of,
                "current": fact.current,
                "confidence": fact.confidence,
                "citation": fact.citation,
                "entity_id": fact.entity_id,
                "predicate": fact.predicate,
                "object_value": fact.object_value,
            })
        
        return results
    
    def get_current_facts(self, entity_id: str = None) -> List[dict]:
        """Get current facts by entity."""
        facts = self.fact_store.get_current_facts(entity_id)
        return [fact.model_dump() for fact in facts]
PYEOF
```

Now check if there are existing models for RetrievedFact to ensure compatibility:

```bash
# Check what the retrieval modules expect to return
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from models import RetrievedFact
    print('RetrievedFact exists in models.py')
    import inspect
    print(inspect.getsource(RetrievedFact))
except ImportError:
    try:
        from src.models import RetrievedFact
        print('RetrievedFact exists in src/models.py')
        import inspect
        print(inspect.getsource(RetrievedFact))
    except ImportError as e:
        print(f'RetrievedFact not found: {e}')
        print('Will use dict format')
"
```

### Step 1.3: Verify Retrieval Works (10 min)
```bash
python -c "
from src.dev_urgent.pure_rag_urgent import UrgentPureRAGRetriever
retriever = UrgentPureRAGRetriever()
results = retriever.search('Operation Alpha')
print(f'Found {len(results)} results')
for r in results:
    print(f'  - {r[\"content\"]}')
    print(f'    Source: {r[\"source\"]}')
    print(f'    As-of: {r[\"as_of\"]}')
"
```

**Expected Output:**
```
Found 2 results
  - Operation Alpha has status APPROVED
    Source: document_1.pdf
    As-of: 2024-01-15 10:00:00
  - Operation Alpha budget is $500,000
    Source: document_1.pdf
    As-of: 2024-01-15 10:00:00
```

---

## HOUR 2: GENERATION & API (45 minutes)

### Step 2.1: Create Simple Answer Generator (15 min)
Create a minimal answer generator that uses retrieved facts:

```bash
cat > src/dev_urgent/answer_generator_urgent.py << 'PYEOF'
"""
Urgent answer generator.
Creates simple answers from retrieved facts.
"""
from typing import List, Optional
from datetime import datetime
import re


class UrgentAnswerGenerator:
    """Generate answers from facts."""
    
    def generate(
        self,
        query: str,
        facts: List[dict],
        mode: str = "pure_rag",
        **kwargs
    ) -> dict:
        """
        Generate answer from facts.
        Return format: {"answer": str, "facts": list, "confidence": float, "citations": list}
        """
        if not facts:
            return {
                "answer": "I couldn't find any relevant information.",
                "facts": [],
                "confidence": 0.0,
                "citations": [],
            }
        
        # Extract key information from query
        query_lower = query.lower()
        
        # Try to find direct answer
        answer = self._find_direct_answer(query, facts)
        
        # Calculate confidence
        confidence = self._calculate_confidence(facts)
        
        # Generate citations
        citations = self._generate_citations(facts)
        
        # Format facts for output
        output_facts = [self._format_fact(f) for f in facts]
        
        return {
            "answer": answer,
            "facts": output_facts,
            "confidence": confidence,
            "citations": citations,
        }
    
    def _find_direct_answer(self, query: str, facts: List[dict]) -> str:
        """Extract answer from facts."""
        query_lower = query.lower()
        
        # Check for question patterns
        if "what is" in query_lower or "what's" in query_lower:
            for fact in facts:
                content = fact.get("content", "").lower()
                if "status" in query_lower and "status" in content:
                    # Extract value
                    match = re.search(r'status (\w+)', content, re.IGNORECASE)
                    if match:
                        return f"The current status is **{match.group(1).upper()}**."
                if "budget" in query_lower and "budget" in content:
                    match = re.search(r'budget [is|of]? (.+)', content, re.IGNORECASE)
                    if match:
                        return f"The budget is **{match.group(1)}**."
                if "commander" in query_lower and "commander" in content:
                    match = re.search(r'commander (?:is |of )?(.+)', content, re.IGNORECASE)
                    if match:
                        return f"The commander is **{match.group(1)}**."
        
        # Generic answer from top fact
        if facts:
            return f"{facts[0].get('content', '')}"
        
        return "I couldn't determine a specific answer from the available information."
    
    def _calculate_confidence(self, facts: List[dict]) -> float:
        """Calculate average confidence."""
        if not facts:
            return 0.0
        confidences = [f.get("confidence", 0.5) for f in facts]
        return sum(confidences) / len(confidences)
    
    def _generate_citations(self, facts: List[dict]) -> List[str]:
        """Generate citation strings."""
        citations = []
        for i, fact in enumerate(facts, 1):
            citation = fact.get("citation", "")
            if citation:
                citations.append(f"[{i}] {citation}")
        return citations
    
    def _format_fact(self, fact: dict) -> dict:
        """Format fact for output."""
        formatted = fact.copy()
        if isinstance(fact.get("as_of"), datetime):
            formatted["as_of"] = fact["as_of"].isoformat() + "Z"
        return formatted
PYEOF
```

### Step 2.2: Modify API to Use Urgent Components (20 min)
Modify `src/api/server.py` to use our urgent retriever and generator:

```bash
# First, check current API
cat src/api/server.py | head -100
```

Then, we need to modify it. But first, let's see what's there and what needs to change:

```bash
# Check if server.py has the query endpoint
python -c "
with open('src/api/server.py') as f:
    content = f.read()
    if 'query' in content.lower():
        print('Query endpoint exists')
    else:
        print('Query endpoint MISSING')
    if 'PureRAGRetriever' in content or 'RAGRetriever' in content or 'retrieve' in content.lower():
        print('Retriever imported')
    else:
        print('Retriever NOT imported')
"
```

Now create a version that uses our urgent components (we'll modify the existing one):

```bash
# Create a patch file
cat > src/dev_urgent/api_patch.py << 'PYEOF'
"""
Patch to modify API server to use urgent components.
This shows what needs to change.
"""

# The API endpoint should look like this:

"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.dev_urgent.pure_rag_urgent import UrgentPureRAGRetriever
from src.dev_urgent.answer_generator_urgent import UrgentAnswerGenerator
import uuid

app = FastAPI(title="Temporal KG-RAG System")

# Initialize urgent components
urgent_retriever = UrgentPureRAGRetriever()
urgent_generator = UrgentAnswerGenerator()


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
    '''Answer a query using the RAG system.'''
    
    # Parse as_of if provided
    as_of_dt = None
    if request.as_of:
        try:
            as_of_dt = datetime.fromisoformat(request.as_of.replace('Z', ''))
        except Exception:
            pass
    
    # Retrieve facts (using urgent retriever)
    facts = urgent_retriever.search(
        query=request.question,
        as_of=as_of_dt,
        mode=request.mode,
        limit=5
    )
    
    # Generate answer
    result = urgent_generator.generate(
        query=request.question,
        facts=facts,
        mode=request.mode
    )
    
    # Generate audit ID
    audit_id = str(uuid.uuid4())
    
    return QueryResponse(
        answer=result["answer"],
        facts=result["facts"],
        citations=result["citations"],
        audit_id=audit_id,
        confidence=result["confidence"]
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/ready")
async def ready_check():
    return {"status": "ready"}
"""
PYEOF
```

Now let's actually modify the real `server.py`:

```bash
# Backup original
cp src/api/server.py src/api/server.py.backup

# Create minimal working version
cat > src/api/server.py << 'PYEOF'
"""
Minimal API server for urgent demo.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

# Import urgent components (will fall back to mocks)
try:
    from src.dev_urgent.pure_rag_urgent import UrgentPureRAGRetriever
    from src.dev_urgent.answer_generator_urgent import UrgentAnswerGenerator
    print("✅ Using urgent components")
    retriever = UrgentPureRAGRetriever()
    generator = UrgentAnswerGenerator()
except ImportError as e:
    print(f"⚠️ Using fallback: {e}")
    retriever = None
    generator = None

app = FastAPI(title="Temporal KG-RAG System")


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
    '''Answer a query using the RAG system.'''
    
    # If no retriever, return mock response
    if retriever is None or generator is None:
        return QueryResponse(
            answer="System not fully configured. Using demo mode.",
            facts=[],
            citations=[],
            audit_id=str(uuid.uuid4()),
            confidence=0.0
        )
    
    # Parse as_of if provided
    as_of_dt = None
    if request.as_of:
        try:
            as_of_dt = datetime.fromisoformat(request.as_of.replace('Z', ''))
        except Exception:
            pass
    
    # Retrieve facts
    facts = retriever.search(
        query=request.question,
        as_of=as_of_dt,
        mode=request.mode,
        limit=5
    )
    
    # Generate answer
    result = generator.generate(
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
async def health_check():
    return {"status": "healthy"}


@app.get("/ready")
async def ready_check():
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYEOF
```

### Step 2.3: Verify API Works (10 min)
```bash
# Start API server
python src/api/server.py &
API_PID=$!
sleep 3

# Test health endpoint
curl -s http://localhost:8000/health | python -m json.tool

# Test query endpoint
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the status of operation Alpha?", "mode": "pure_rag"}' | python -m json.tool

# Kill server
kill $API_PID 2>/dev/null
```

**Expected Output:**
```json
{
    "answer": "The current status is **APPROVED**.",
    "facts": [
        {
            "fact_id": "fact_001",
            "content": "Operation Alpha has status APPROVED",
            "source": "document_1.pdf",
            "as_of": "2024-01-15T10:00:00Z",
            "current": true,
            "confidence": 0.95,
            "citation": "Source: document_1.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
            "entity_id": "operation_alpha",
            "predicate": "status",
            "object_value": "APPROVED"
        }
    ],
    "citations": ["[1] Source: document_1.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z"],
    "audit_id": "...",
    "confidence": 0.95
}
```

---

## HOUR 3: UI CONNECTION (30 minutes)

### Step 3.1: Modify Streamlit UI (20 min)
Modify `ui_streamlit.py` to connect to our API:

```bash
# Backup original
cp ui_streamlit.py ui_streamlit.py.backup

# Create urgent version
cat > ui_streamlit.py << 'PYEOF'
"""
Urgent Streamlit UI for Temporal KG-RAG Demo.
"""
import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

# Page setup
st.set_page_config(
    page_title="Temporal KG-RAG Demo",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {padding: 2rem;}
    .answer-box {background: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #4285f4;}
    .fact-box {background: #ffffff; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; border: 1px solid #ddd;}
    .citation {font-size: 0.8rem; color: #666; margin-top: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# Title
st.title("🔍 Temporal KG-RAG System - Demo")
st.markdown("Query documents with temporal validity. Most recent facts are shown by default.")

# Query form
with st.form("query_form"):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_input(
            "Enter your query:",
            placeholder="What is the status of operation Alpha?",
            label_visibility="collapsed"
        )
    
    with col2:
        mode = st.selectbox(
            "Mode:",
            ["pure_rag", "rag_kg_validator", "kg_only"],
            index=0,
            label_visibility="collapsed"
        )
    
    include_history = st.checkbox("Include historical facts", value=False)
    as_of = st.text_input("As-of timestamp (ISO format, leave empty for latest):", "")
    
    submitted = st.form_submit_button("🔍 Search", type="primary")

# Process query
if submitted and question:
    with st.spinner("Searching..."):
        try:
            # Build request
            payload = {
                "question": question,
                "mode": mode,
                "include_history": include_history,
            }
            if as_of:
                payload["as_of"] = as_of
            
            # Call API
            response = requests.post(
                f"{API_URL}/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display results
                st.success("✅ Query successful!")
                
                # Answer
                st.markdown("### 💡 Answer")
                st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)
                
                # Confidence
                st.markdown(f"**Confidence:** {result['confidence']:.2%}")
                
                # Citations
                if result.get("citations"):
                    st.markdown("### 📜 Citations")
                    for citation in result["citations"]:
                        st.markdown(f'<div class="citation">{citation}</div>', unsafe_allow_html=True)
                
                # Facts
                if result.get("facts"):
                    st.markdown("### 📊 Retrieved Facts")
                    for i, fact in enumerate(result["facts"], 1):
                        st.markdown(f'<div class="fact-box"><strong>Fact {i}:</strong> {fact["content"]}<br><strong>Source:</strong> {fact["source"]}<br><strong>As-of:</strong> {fact["as_of"]}<br><strong>Current:</strong> {fact["current"]}</div>', unsafe_allow_html=True)
                
                # Audit ID
                st.markdown(f"**Audit ID:** `{result['audit_id']}`")
                
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.code(response.text)
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server. Is it running?")
            st.markdown(f"Try: `python src/api/server.py`")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Side panel
with st.sidebar:
    st.header("📚 About")
    st.markdown("""
    This is a **Temporal-Valid Knowledge Graph RAG System** demo.
    
    **Features:**
    - ✅ Multi-format document extraction
    - ✅ Temporal validity tracking
    - ✅ Most-recent-wins conflict resolution
    - ✅ Three retrieval modes
    
    **This demo uses mock data** for rapid testing.
    """)
    
    st.header("🔧 API Status")
    try:
        health = requests.get(f"{API_URL}/health").json()
        st.markdown(f"Health: **{health.get('status', 'unknown')}**")
    except:
        st.markdown("Health: **❌ Offline**")
    
    try:
        ready = requests.get(f"{API_URL}/ready").json()
        st.markdown(f"Ready: **{ready.get('status', 'unknown')}**")
    except:
        st.markdown("Ready: **❌ Not ready**")

# Footer
st.markdown("---")
st.markdown("🏠 [Home](/) | 📄 [Documentation](/) | 🐛 [Report Issues](/)")
PYEOF
```

### Step 3.2: Start All Services (5 min)
```bash
# Terminal 1: Start API server
python src/api/server.py &
API_PID=$!
echo "API started on port 8000 (PID: $API_PID)"

# Terminal 2: Start Streamlit
streamlit run ui_streamlit.py &
STREAMLIT_PID=$!
echo "Streamlit started on port 8501 (PID: $STREAMLIT_PID)"

# Verify both are running
sleep 5
curl -s http://localhost:8000/health
curl -s http://localhost:8501
```

### Step 3.3: End-to-End Test (5 min)
1. Open browser to `http://localhost:8501`
2. Enter query: "What is the status of operation Alpha?"
3. Click Search
4. **Expected:** See answer "The current status is **APPROVED**" with citations

---

## ✅ POST-IMPLEMENTATION CHECKLIST

If you finish early, add these improvements:

### Hour 4+: Enhancements
- [ ] Add more mock facts (10-20 different examples)
- [ ] Fix any formatting issues in UI
- [ ] Add error handling for edge cases
- [ ] Add loading states in UI
- [ ] Add example queries to UI
- [ ] Test with different modes (rag_kg_validator, kg_only)

### Late Additions (If time permits)
- [ ] Connect to real retrieval modules (not mock)
- [ ] Add simple intake for file uploads
- [ ] Add sorting/filtering in UI

---

## 🚨 TROUBLESHOOTING

### Problem: Import errors
```bash
# Check if modules are importable
python -c "from src.dev_urgent.mock_facts import mock_fact_store"
python -c "from src.dev_urgent.pure_rag_urgent import UrgentPureRAGRetriever"
python -c "from src.dev_urgent.answer_generator_urgent import UrgentAnswerGenerator"
```

### Problem: API not starting
```bash
# Check for port conflicts
lsof -i :8000
kill -9 $(lsof -t -i :8000) 2>/dev/null

# Check dependencies
uv sync
```

### Problem: Streamlit not starting
```bash
# Check if streamlit is installed
pip show streamlit

# Install if needed
pip install streamlit
```

### Problem: CORS errors
Add CORS middleware to API:
```python
# Add to src/api/server.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 EXECUTION SUMMARY

| Hour | Task | Status | Verify |
|------|------|--------|--------|
| 0 | Prep | ⏳ | Imports work |
| 1 | Mock Data + Retrieval | ⏳ | `retriever.search()` returns facts |
| 2 | Generation + API | ⏳ | API returns answers |
| 3 | UI Connection | ⏳ | Demo works in browser |

---

## 🎯 FINAL SCRIPT: One-Command Demo

Create a script to start everything:

```bash
cat > demo_start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Temporal KG-RAG Demo..."
echo ""

# Start API
python src/api/server.py > /tmp/api.log 2>&1 &
API_PID=$!
echo "✅ API server started (PID: $API_PID)"
echo "   Access: http://localhost:8000"

# Wait for API to start
sleep 5

# Start Streamlit
streamlit run ui_streamlit.py > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "✅ Streamlit UI started (PID: $STREAMLIT_PID)"
echo "   Access: http://localhost:8501"

echo ""
echo "🎯 Demo is running!"
echo "   Open your browser to http://localhost:8501"
echo ""
echo "Try these queries:"
echo "   - What is the status of operation Alpha?"
echo "   - What is the budget of operation Alpha?"
echo "   - Who is the commander of operation Alpha?"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait

# Cleanup
kill $API_PID $STREAMLIT_PID 2>/dev/null
echo "✅ Services stopped"
EOF

chmod +x demo_start.sh
```

Then run:
```bash
./demo_start.sh
```

---

## 🏆 SUCCESS CRITERIA

**YOU WIN IF:**
1. ✅ `http://localhost:8501` opens in browser
2. ✅ User can enter a query and click Search
3. ✅ Answer appears with:
   - Clear answer text
   - Confidence score
   - Citations with source + timestamp
   - Retrieved facts list
4. ✅ Works for multiple queries
5. ✅ No errors in console

**Goal: Working demo in 2-3 hours**

---

## 📞 NEED HELP?

Run these diagnostic commands:

```bash
# Check all services
echo "=== API ==="
curl -s http://localhost:8000/health

echo ""
echo "=== Streamlit ==="
curl -s http://localhost:8501 > /dev/null && echo "Streamlit is running" || echo "Streamlit is NOT running"

echo ""
echo "=== Test Query ==="
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "mode": "pure_rag"}' | python -m json.tool | head -20

# Check logs
echo ""
echo "=== API Logs ==="
tail -20 /tmp/api.log

echo ""
echo "=== Streamlit Logs ==="
tail -20 /tmp/streamlit.log
```

---

## ⚡ IMMEDIATE ACTION

**DEVELOPER: Start with Hour 0 - Step 0.1 RIGHT NOW.**

Copy and paste each command in sequence. Don't skip steps.

**The clock is ticking. You have hours, not days. GO.**
