from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.config import settings
from app.services.retriever import search_documents
from app.services.web_search import search_web
from app.services.memory import get_chat_history, save_to_history

# 1. Initialize the Groq AI Model


# Use this strictly for the rephrase_chain
llm_parser = ChatGroq(
    api_key=settings.groq_api_key, 
    model_name="groq/compound",
    temperature=0.0 
)

# Use this for the main answer chain
llm_speaker = ChatGroq(
    api_key=settings.groq_api_key, 
    model_name="groq/compound",
    temperature=0.2 
)




# --- NEW: The Query Reformulator Prompt ---
# This prompt's ONLY job is to rewrite the question. It does not answer it.

# --- NEW: The STRICT Query Reformulator Prompt ---
# --- NEW: The STRICT Query Reformulator Prompt ---
# --- THE CONTEXT-AWARE REFORMULATOR PROMPT ---
# --- THE ULTIMATE TAGGED & CONTEXT-AWARE REFORMULATOR PROMPT ---
rephrase_prompt = PromptTemplate.from_template("""
You are a robotic text parser and query reformulator. You DO NOT answer questions. 
Look at the Chat History and the Latest Question.

RULE 1: If the Latest Question refers to the history (e.g., uses words like "it", "he", "this", "its"), rewrite it so it makes sense on its own.
RULE 2: If the Latest Question is a BRAND NEW TOPIC or already makes sense, DO NOT change it. Output the exact original question.
CRITICAL RULE 3: You MUST output your final result starting with the exact word "REWRITTEN:" followed by the question. Do not add any other text, reasoning, or answers.

Example 1 (Follow-up -> Rewrite):
Chat History: Human: Who is the CEO of Apple? AI: Tim Cook.
Latest Question: How old is he?
Output: REWRITTEN: How old is Tim Cook?

Example 2 (New Topic -> Leave it alone):
Chat History: Human: What is Project Vidyut? AI: It is a tech project.
Latest Question: What is a flower?
Output: REWRITTEN: What is a flower?

---
Chat History:
{chat_history}

Latest Question: {query}
Output:
""")




# --- EXISTING: The Main QA Prompt ---
prompt_template = PromptTemplate.from_template("""
You are an intelligent AI assistant. Use the following context and conversation history to answer the user's question. 
If the context doesn't contain the answer, say "I cannot answer this based on the provided context."

Chat History:
{chat_history}

Context:
{context}

Question: {query}

Answer:
""")

def generate_rag_response(session_id: str, query: str) -> dict:
    # 1. Fetch the user's memory
    history = get_chat_history(session_id)
    
    # 2. --- NEW SMART LOGIC: The Reformulator ---
    standalone_query = query
    
    # If we have history, let's ask the LLM to rewrite the question just in case
    if history != "No previous conversation history.":
        print(f"Original Query: {query}")
        rephrase_chain = rephrase_prompt | llm_parser
        
        # We strip() to remove any accidental white spaces the LLM might add
        standalone_query = rephrase_chain.invoke({
            "chat_history": history, 
            "query": query
        }).content.strip()
        
        print(f"Reformulated Query: {standalone_query}")
    # ---------------------------------------------
    
    # Initialize the main answering chain
    chain = prompt_template | llm_speaker
    
    # 3. Search using the STANDALONE query (not the raw user input)
    retrieved_chunks = search_documents(session_id, standalone_query)
    
    if len(retrieved_chunks) > 0:
        context = "\n\n".join(retrieved_chunks)
        
        # FIRST PASS: Knowledge Base
        ai_message = chain.invoke({"context": context, "chat_history": history, "query": query})
        answer = ai_message.content
        source = "document"
        
        if "I cannot answer this" in answer:
            print("Documents were irrelevant. Rerouting to Live Web...")
            # SECOND PASS: Live Web
            web_context = search_web(standalone_query) # Search web with the standalone query!
            final_web_message = chain.invoke({"context": web_context, "chat_history": history, "query": query})
            answer = final_web_message.content
            source = "web"
            
    else:
        # NO DOCUMENTS: Direct Web Search
        print("No documents found. Searching web...")
        web_context = search_web(standalone_query) # Search web with the standalone query!
        ai_message = chain.invoke({"context": web_context, "chat_history": history, "query": query})
        answer = ai_message.content
        source = "web"

    # 4. Save the final result to Redis
    save_to_history(session_id, query, answer)

    return {
        "answer": answer,
        "source": source
    }
