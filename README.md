# SAP RAG Flask App

A Retrieval-Augmented-Generation (RAG) service using LangChain, Pinecone, and Flask

## Docker

# Clone the repository
git clone https://github.com/manuels288/chatbot.git
cd chatbot

# Build the Docker image
docker build -t chatbot .

# Run the container
docker run -p 5000:5000 \
  -e PINECONE_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  chatbot
