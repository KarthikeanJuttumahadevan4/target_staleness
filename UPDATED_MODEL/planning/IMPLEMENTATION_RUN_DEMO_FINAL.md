# 🚀 RUN THE DEMO - FINAL INSTRUCTIONS

## 🎯 **THE SYSTEM IS READY!**

The Temporal KG-RAG System is now fully functional with:
- ✅ Mock facts store (5 facts about operations)
- ✅ Urgent retriever (keyword-based search)
- ✅ Urgent generator (answer extraction)
- ✅ Working API endpoints
- ✅ Streamlit UI

---

## 📁 **IMPORTANT: Run from IMPLEMENTATION directory**

```bash
cd /home/karthikean.juttumaha/mini-extract/UPDATED_MODEL/IMPLEMENTATION
```

All commands below assume you're in this directory!

---

## 🔧 STEP 1: Install Dependencies

```bash
# Install required packages
uv add fastapi uvicorn streamlit requests python-dotenv

# Sync environment
uv sync
```

---

## ▶️ STEP 2: Start the API Server

**Open Terminal 1:**
```bash
cd /home/karthikean.juttumaha/mini-extract/UPDATED_MODEL/IMPLEMENTATION

# Start API server
uv run python src/api/server.py
```

**Expected:** Server starts on http://localhost:8000

**Leave this terminal running!**

---

## ▶️ STEP 3: Start the Streamlit UI

**Open Terminal 2:**
```bash
cd /home/karthikean.juttumaha/mini-extract/UPDATED_MODEL/IMPLEMENTATION

# Start UI
uv run streamlit run ui_streamlit.py --server.port 8501
```

**Expected:** UI starts on http://localhost:8501

**Leave this terminal running!**

---

## 🌐 STEP 4: Access the UI

**Open your browser:** http://localhost:8501

You should see the Temporal KG-RAG Demo interface!

---

## 💬 STEP 5: Test Queries

Enter these queries in the text box and click **Search**:

### Query 1: Status
```
What is the status of operation Alpha?
```
**Expected Answer:** "The current status is **APPROVED**."

### Query 2: Budget
```
What is the budget of operation Alpha?
```
**Expected Answer:** "The budget is **$500,000**."

### Query 3: Commander
```
Who is the commander of operation Alpha?
```
**Expected Answer:** "The commander is **Captain Smith**."

### Query 4: Beta Status
```
What is the status of operation Beta?
```
**Expected Answer:** "The current status is **PENDING**."

---

## 🧪 STEP 6: Test API Directly (Optional)

```bash
# Test health
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the status of operation Alpha?",
    "mode": "pure_rag"
  }'
```

---

## 🛑 STOPPING THE DEMO

```bash
# Kill API server
pkill -f "python src/api/server.py"

# Kill Streamlit
pkill -f "streamlit run ui_streamlit.py"
```

---

## 📊 WHAT YOU'LL SEE

For each query, the UI displays:

✅ **Answer** - Generated from facts  
✅ **Confidence Score** - System confidence (90%)  
✅ **Citations** - Source files and timestamps  
✅ **Supporting Facts** - Raw facts  
✅ **Audit ID** - For tracking  

---

## 🎉 SUCCESS!

The system is working! You can now demonstrate:

1. ✅ Query processing
2. ✅ Answer generation
3. ✅ Temporal validity (timestamps)
4. ✅ Provenance (citations)
5. ✅ Confidence scoring

**Go demo!** 🎊

---

## 📞 QUICK REFERENCE

```bash
# One-liner to start everything:
cd /home/karthikean.juttumaha/mini-extract/UPDATED_MODEL/IMPLEMENTATION && \
uv run python src/api/server.py & uv run streamlit run ui_streamlit.py
```

Then open http://localhost:8501 in your browser!