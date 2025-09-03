# SAP RAG Flask App

A **Retrieval-Augmented-Generation (RAG)** service using **LangChain**, **Pinecone**, and **Flask**.  
This project allows you to ask questions about SAP S/4HANA and get step-by-step answers based on indexed documents.

---

## Features

- Uses a **RAG pipeline**: retrieves context from a Pinecone vector store and generates answers with a language model.
- Supports **multi-step, SAP-specific, step-by-step answers**.
- Fully containerized with **Docker** for easy deployment.
- Chat history support for context-aware responses.

---

## Prerequisites

- Python 3.11+  
- Docker (optional, but recommended)  
- Pinecone API key (for the vector database)  
- OpenAI API key (for the LLM)  

> ⚠️ Notes for running the code:
> - Set your **Pinecone index name** in `main.py` on **line 63**.
> - By default, it uses **OpenAI GPT models**, but you can quickly switch to **open-source models** by modifying **lines 30 and 38** in `main.py`.

---

## Installation (Local Python Environment)

1. Clone the repository:

git clone https://github.com/manuels288/chatbot.git
cd chatbot

2. Create a virtual environment and install dependencies:

python -m venv venv
# Activate virtual environment
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt

3. Set environment variables:

export PINECONE_API_KEY=your_pinecone_key
export OPENAI_API_KEY=your_openai_key

4. Run the Flask app:

python main.py

## Running with Docker

1. Build the Docker image:

docker build -t chatbot .

2. Run the container:

docker run -p 5000:5000 \
  -e PINECONE_API_KEY=your_pinecone_key \
  -e OPENAI_API_KEY=your_openai_key \
  chatbot

  or with .env:

  docker run -p 5000:5000 --env-file .env chatbot

3. Ask your question:

curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I navigate to a customer order in SAP S/4HANA?"}'
