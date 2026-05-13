from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os

# ── EMBEDDING MODEL (loaded once, reused) ──────────────────
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ── BUILD VECTOR STORE FROM PDF ────────────────────────────
def build_vectorstore(pdf_path: str):
    # Load
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)

    # Embed + Store
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

# ── BUILD RAG CHAIN WITH MEMORY ────────────────────────────
def build_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume analyzer. 
        Answer questions about the resume using ONLY the context below.
        Be specific and cite details from the resume.
        If something is not in the resume, say 'This information is not in the resume.'
        
        Resume Context:
        {context}"""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_context(input_dict):
        docs = retriever.invoke(input_dict["question"])
        return format_docs(docs)

    chain = (
        RunnablePassthrough.assign(context=get_context)
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

# ── GET ANSWER ─────────────────────────────────────────────
def get_answer(chain, question: str, history: list):
    response = chain.invoke({
        "question": question,
        "history": history
    })

    # Update history
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=response))

    return response, history