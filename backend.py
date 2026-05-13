from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rag_utils import build_vectorstore, build_rag_chain, get_answer
import tempfile
import os

load_dotenv()

app = FastAPI(title="Resume Analyzer API")

# Allow Streamlit to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── IN MEMORY SESSION STORAGE ──────────────────────────────
# session_id → {chain, history}
sessions = {}

# ── REQUEST MODELS ─────────────────────────────────────────
class QuestionRequest(BaseModel):
    session_id: str
    question: str

# ── ENDPOINT 1: Upload PDF ─────────────────────────────────
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Build vectorstore + chain
    vectorstore = build_vectorstore(tmp_path)
    chain = build_rag_chain(vectorstore)

    # Create session
    import uuid
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "chain": chain,
        "history": []
    }

    # Clean up temp file
    os.unlink(tmp_path)

    return {
        "session_id": session_id,
        "message": "Resume uploaded and processed successfully",
        "status": "ready"
    }

# ── ENDPOINT 2: Ask Question ───────────────────────────────
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    # Check session exists
    if request.session_id not in sessions:
        return {"error": "Session not found. Please upload a resume first."}

    session = sessions[request.session_id]

    # Get answer
    answer, updated_history = get_answer(
        chain=session["chain"],
        question=request.question,
        history=session["history"]
    )

    # Update history in session
    sessions[request.session_id]["history"] = updated_history

    return {
        "answer": answer,
        "history_length": len(updated_history)
    }

# ── ENDPOINT 3: Get History ────────────────────────────────
@app.get("/history/{session_id}")
async def get_history(session_id: str):
    if session_id not in sessions:
        return {"error": "Session not found"}

    history = sessions[session_id]["history"]
    formatted = []
    for msg in history:
        formatted.append({
            "role": "human" if msg.__class__.__name__ == "HumanMessage" else "ai",
            "content": msg.content
        })

    return {"history": formatted}

# ── ENDPOINT 4: Clear Session ──────────────────────────────
@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Session cleared"}

# ── ROOT ───────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Resume Analyzer API",
        "endpoints": {
            "upload": "POST /upload",
            "ask": "POST /ask",
            "history": "GET /history/{session_id}",
            "clear": "DELETE /session/{session_id}",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)