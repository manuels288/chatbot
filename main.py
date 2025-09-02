from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableMap

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# -------------------------------------------------
# Pinecone Init
# -------------------------------------------------
def init_pinecone():
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("Pinecone API Key nicht gesetzt!")
    return Pinecone(api_key=api_key)


# -------------------------------------------------
# Embeddings Init
# -------------------------------------------------
def init_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")
    # ggf. austauschbar gegen andere LLMs


# -------------------------------------------------
# LLM Init
# -------------------------------------------------
def init_llm():
    return ChatOpenAI(model_name="gpt-4o-mini")
    # oder: OllamaLLM(model="llama3.2")


# -------------------------------------------------
# Prompt Definition
# -------------------------------------------------
def build_prompt():
    template = (
        "Du bist ein SAP S/4HANA-Experte. Beantworte die Frage ausschließlich basierend auf dem bereitgestellten Kontext."
        "Füge keine Informationen hinzu, die nicht im Kontext stehen. Beachte den Chatverlauf."
        "Falls im Kontext der Pfad zu einer SAP Fiori App genannt wird, füge diesen vollständig in deiner Antwort ein. "
        "Betone die Navigation über das Fiori Launchpad, sofern vorhanden."
        "Gib deine Antwort als Schritt-für-Schritt-Anleitung zurück."
        "\n\n"
        "Kontext: {context}"
        "Chatverlauf: {chat_history}"
        "Frage: {input}"
        "Deine Antwort sollte auf deutsch, klar, präzise und SAP-spezifisch sein"
    )
    return ChatPromptTemplate.from_template(template)


# -------------------------------------------------
# Retriever Init 
# -------------------------------------------------
def init_retriever(pc, embeddings, index_name="myllmindex1"):
    index = pc.Index(index_name)
    vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
    return vectorstore.as_retriever()


# -------------------------------------------------
# RAG Chain
# -------------------------------------------------
def build_rag_chain(retriever, prompt, llm):
    parser = StrOutputParser()
    rag_chain = (
        RunnableMap({
            "context": lambda x: retriever.invoke(x["input"]),
            "chat_history": lambda x: x["chat_history"],
            "input": lambda x: x["input"],
        })
        | prompt
        | llm
        | parser
    )
    return rag_chain


# -------------------------------------------------
# Chain with Chat Memory
# -------------------------------------------------
def init_chain_with_memory(rag_chain):
    chat_history = InMemoryChatMessageHistory()
    return RunnableWithMessageHistory(
        rag_chain,
        lambda: chat_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )


# -------------------------------------------------
# Flask Setup
# -------------------------------------------------
def create_app():
    app = Flask(__name__)
    CORS(app)

    
    pc = init_pinecone()
    embeddings = init_embeddings()
    llm = init_llm()
    prompt = build_prompt()
    retriever = init_retriever(pc, embeddings)
    rag_chain = build_rag_chain(retriever, prompt, llm)
    chain_with_memory = init_chain_with_memory(rag_chain)

    # API Route
    @app.route("/api/ask", methods=["POST"])
    def ask():
        data = request.get_json()
        question = data.get("question")
        if not question:
            return jsonify({"error": "❌ Keine Frage übergeben"}), 400
        try:
            response = chain_with_memory.invoke({"input": question})
            return jsonify({"answer": response})
        except Exception as e:
            return jsonify({"error": repr(e)}), 500

    return app


# -------------------------------------------------
# Main Entry
# -------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
