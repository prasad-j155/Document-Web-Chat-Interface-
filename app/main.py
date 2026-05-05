from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # NEW IMPORT
from app.api import routes

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hybrid RAG Chat API",
        description="Document Intelligence with Web Search Fallback",
        version="1.0.0"
    )
    
    # --- NEW CORS CONFIGURATION ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Allows your HTML file to connect securely
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # ------------------------------
    
    # Register our API endpoints
    app.include_router(routes.router)
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
