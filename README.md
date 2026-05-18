📄 Conversational Resume Analyzer

> Still learning, but here's what I built — an AI-powered resume analyzer that lets you upload any resume PDF and have a real conversation about it.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 What is this?

Upload any resume PDF → ask questions about it conversationally → get answers strictly from the document content.

No hallucinations. No guessing. Just facts from the resume.

---

## ✨ Features

- 📁 **PDF Upload** — supports any resume PDF
- 💬 **Conversational Q&A** — ask questions in natural language
- 🧠 **Memory** — follow-up questions work correctly
- 🔍 **Semantic Search** — finds meaning, not just keywords
- 🔒 **Grounded Answers** — LLM answers only from resume content
- ⚡ **Fast Responses** — powered by Groq LLaMA 3.1
- 👥 **Multi-user** — concurrent users with isolated sessions

---

## 🖥️ Demo

### Upload & Chat
> Upload a resume → ask "What are the key skills?" → get answer from actual resume content

### Memory in Action
> Ask "What projects have they built?" → follow up with "Tell me more about the first one" → bot remembers context

---

## 🏗️ Architecture


PDF Upload
    ↓
PyPDFLoader → RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
    ↓
HuggingFace all-MiniLM-L6-v2 → 384-dim vectors → FAISS Vector Store
    ↓
User Question → Semantic Search → Top 3 Relevant Chunks
    ↓
Groq LLaMA 3.1 + Conversation History (MessagesPlaceholder)
    ↓
Grounded Answer → Streamlit Chat UI


---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq API — LLaMA 3.1 8B Instant |
| RAG Framework | LangChain + LCEL |
| Embeddings | HuggingFace all-MiniLM-L6-v2 (local, free) |
| Vector Store | FAISS (Facebook AI Similarity Search) |
| Memory | MessagesPlaceholder — LangChain 0.2+ |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| PDF Processing | PyPDFLoader |
| Text Splitting | RecursiveCharacterTextSplitter |
| Session Management | UUID + in-memory dict |

---

## 📁 Project Structure


conversational-resume-analyzer/
├── backend.py          # FastAPI server — endpoints + session management
├── frontend.py         # Streamlit UI — file upload + chat interface
├── rag_utils.py        # RAG pipeline — load, chunk, embed, retrieve, answer
├── requirements.txt    # All dependencies
├── .env.example        # API key template
└── .gitignore          # Excludes .env, venv, faiss_index


---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or 3.11
- Free Groq API key → [console.groq.com](https://console.groq.com)

### 1. Clone the repository

git clone https://github.com/kathpalsiya01-coder/Conversational-Resume-Analyzer.git
cd Conversational-Resume-Analyzer


### 2. Create virtual environment

python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate


### 3. Install dependencies

pip install -r requirements.txt


### 4. Add API key
Create a `.env` file in the project root:

GROQ_API_KEY=your_groq_api_key_here

Get your free key at [console.groq.com](https://console.groq.com)

### 5. Run backend

python backend.py

Runs at `http://localhost:8000`

### 6. Run frontend (new terminal)

streamlit run frontend.py

Runs at `http://localhost:8501`

### 7. Open browser

http://localhost:8501


---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload PDF, create session |
| POST | `/ask` | Ask question about resume |
| GET | `/history/{session_id}` | Get conversation history |
| DELETE | `/session/{session_id}` | Clear session |
| GET | `/docs` | Swagger UI |

---

## 💡 How It Works

### Indexing Phase (on PDF upload)
1. `PyPDFLoader` reads PDF page by page into Document objects
2. `RecursiveCharacterTextSplitter` breaks into 1000-char chunks with 200-char overlap
3. `HuggingFace all-MiniLM-L6-v2` converts each chunk to a 384-dim vector
4. `FAISS` stores all vectors for fast similarity search
5. Unique UUID session created for this user

### Retrieval Phase (on each question)
1. Question embedded using same HuggingFace model
2. FAISS finds top 3 semantically similar chunks
3. Chunks + full conversation history injected into LLM prompt
4. Groq LLaMA answers strictly from resume context
5. Answer + updated history returned to frontend

---

## 🔑 Key Technical Decisions

**HuggingFace over OpenAI embeddings**
Runs locally — zero cost, no data sent externally, works offline.

**FAISS over cloud vector DBs**
Zero setup, works offline, perfect for single-document use case.

**MessagesPlaceholder for memory**
Modern LangChain 0.2+ approach — deprecated memory classes avoided entirely.

**UUID session management**
Each user gets isolated chain + history — supports concurrent users with zero interference.

**Grounded system prompt**
LLM explicitly instructed to answer only from retrieved context — eliminates hallucination.

**Separation of concerns**
Three files, three responsibilities — RAG logic, API serving, and UI are fully decoupled.

---

## 💬 Sample Questions to Try


What are the candidate's key technical skills?
What projects have they built?
Is this resume suitable for a GenAI internship?
What is their educational background?
Rate this resume out of 10 for an ML role
What frameworks do they have experience with?
Tell me more about their RAG project
What is their CGPA?
Does this candidate have deployment experience?


---

## 🚀 Future Improvements

- [ ] ATS Score — analyze resume against job description
- [ ] Streaming responses — token by token display
- [ ] Interview question generator
- [ ] Cover letter generator
- [ ] Persistent vector store (Pinecone/Chroma)
- [ ] Redis session storage
- [ ] Docker deployment
- [ ] Multi-PDF support

---

## 📦 Requirements


langchain
langchain-groq
langchain-core
langchain-community
langchain-text-splitters
python-dotenv
pypdf
faiss-cpu
sentence-transformers
fastapi
uvicorn
langserve
streamlit

---

## 🤝 Contributing

Pull requests are welcome. For major changes please open an issue first.

---

## 📝 License

MIT License — feel free to use this project for learning or building on top of it.

---

## 👤 Author

Siya Kathpal— B.Tech student | ML & GenAI enthusiast

GitHub: [@kathpalsiya01-coder](https://github.com/kathpalsiya01-coder)

---
⭐ If this project helped you, please give it a star — it motivates me to keep building!
