#  Hybrid RAG Document & Web Chat API

A high-performance FastAPI backend service that enables context-aware conversational chat over uploaded documents (PDF/DOCX). Built with an intelligent routing architecture, the system seamlessly falls back to live web searches when document context is insufficient, utilizing Redis for memory and caching to ensure lightning-fast responses.

##  Key Features

*   **Intelligent Document Processing:** Ingests `.pdf` and `.docx` files, extracts text, chunks it, and stores it in a state-based Vector Database (ChromaDB) with robust metadata tagging.
*   **Context-Aware Chat Memory:** Maintains conversation history per user session using Redis, allowing for natural, follow-up queries.
*   **Smart Query Reformulation:** Uses a zero-temperature LLM parser to detect pronouns and rewrite follow-up questions into standalone queries, preventing context bleed and hallucination loops.
*   **Dynamic Fallback Routing:** If the retrieved document chunks cannot answer the user's query, the system automatically routes the question to the live web (DuckDuckGo).
*   **Transparent Source Labeling:** Every response is explicitly tagged with `"source": "document"` or `"source": "web"`.
*   **High-Speed Caching:** Queries and responses are stored in Redis to bypass redundant LLM computation on repeated questions.

##  Architecture & Query Flow

This system follows a strict pipeline to guarantee accuracy and efficiency:

1.  **Receive Request:** Accepts the user query and `session_id`.
2.  **Memory & Cache Check:** Retrieves chat history from Redis.
3.  **Query Reformulation:** An LLM invisibly rewrites the query if it relies on past context.
4.  **Document Retrieval:** Performs similarity search in ChromaDB.
5.  **Generation & Rerouting:** 
    *   *Pass 1 (Local):* Attempts to answer using Document context.
    *   *Pass 2 (Web):* If the local attempt fails, fetches external context via DuckDuckGo and answers.
6.  **Source Labeling:** Attaches the definitive source tag to the payload.
7.  **Cache Storage:** Saves the final interaction to Redis.

##  Tech Stack

*   **Framework:** FastAPI
*   **LLM Engine:** Groq API (groq/compound)
*   **Orchestration:** LangChain
*   **Vector Database:** ChromaDB
*   **Memory & Cache:** Redis
*   **Web Search:** DuckDuckGo (`ddgs`)

##  Installation & Setup

### Prerequisites
*   Python 3.10+
*   Redis server running locally or via Docker

### 1. Clone the repository
```bash
git clone [https://github.com/prasad-j155/Document-Web-Chat-Interface-.git](https://github.com/prasad-j155/Document-Web-Chat-Interface-.git)
cd YOUR_REPO_NAME
```

### 2. Set up the Virtual Environment
```bash
python -m venv venv
# On Mac/Linux:
source venv/bin/activate  
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory and add your required API keys and connection strings:
```env
GROQ_API_KEY=your_groq_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
```

##  Running the Application

Start the FastAPI server using Uvicorn:
```bash
uvicorn app.main:app --reload
```
The server will be available at `http://127.0.0.1:8000`. You can access the interactive Swagger API documentation at `http://127.0.0.1:8000/docs`.

##  API Endpoints

### `POST /upload`
Uploads a document to the Vector DB.
*   **Payload:** `multipart/form-data` (file)
*   **Response:** `{"message": "File processed successfully", "file_id": "uuid"}`

### `POST /chat`
Sends a message to the AI.
*   **Payload:** JSON
    ```json
    {
      "session_id": "user_123",
      "query": "Explain the core mechanics of the project."
    }
    ```
*   **Response:** JSON
    ```json
    {
      "answer": "The core mechanics involve...",
      "source": "document"
    }
    ```

---
