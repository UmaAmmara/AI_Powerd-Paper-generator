# main.py
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add services to path
sys.path.append(str(Path(__file__).parent / "services"))

# Import routers
from api.routes_search import router as search_router
from api.routes_index import router as index_router
from api.routes_auth import router as auth_router
from api.routes_generate_paper import router as generate_paper_router
from api.routes_saved_papers import router as saved_papers

# Import exam generation router
try:
    from api.routes_exam_generation import router as exam_generation_router
    EXAM_GEN_AVAILABLE = True
except ImportError as e:
    print(f"Exam generation routes not available: {e}")
    EXAM_GEN_AVAILABLE = False

# Import services
try:
    from services.data_ingestion import PDFIngestor
    from qdrant.schema import create_collection
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Some services not available: {e}")
    SERVICES_AVAILABLE = False

# ----------------------------
# 1️⃣ Setup FastAPI app
# ----------------------------
app = FastAPI(title="Semantic Chunking & Qdrant API") 

# Include all routers
app.include_router(generate_paper_router, prefix="/api", tags=["Paper"])
app.include_router(saved_papers, prefix="/api", tags=["Saved Papers"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(index_router, prefix="/index", tags=["Indexing"])
app.include_router(search_router, prefix="/search", tags=["Search"])

# Include exam generation router if available
if EXAM_GEN_AVAILABLE:
    app.include_router(exam_generation_router, prefix="/api/exam", tags=["Exam Generation"])

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "exam_generation": EXAM_GEN_AVAILABLE}

# ----------------------------
# 2️⃣ Ingest PDFs on startup (if services available)
# ----------------------------
if SERVICES_AVAILABLE:
    PDF_FOLDER = "pdfs"
    ingestor = PDFIngestor()

    @app.on_event("startup")
    def startup_event():
        # Ensure collection exists
        create_collection()
        print("Qdrant collection check completed.")
        
        # Initialize exam service if available
        if EXAM_GEN_AVAILABLE:
            try:
                from services.exam_service import exam_service
                print("Initializing exam generation service...")
                if exam_service.initialize_controller():
                    print("Exam generation service initialized successfully")
                else:
                    print("Exam generation service initialization failed")
            except Exception as e:
                print(f"Error initializing exam service: {e}")

        # Ingest PDFs if folder exists
        if os.path.exists(PDF_FOLDER):
            for filename in os.listdir(PDF_FOLDER):
                if filename.lower().endswith(".pdf"):
                    file_path = os.path.join(PDF_FOLDER, filename)
                    try:
                        ingestor.ingest_to_qdrant(file_path)
                        print(f"Ingested {filename}")
                    except Exception as e:
                        print(f"Failed to ingest {filename}: {e}")
        else:
            print(f"No PDF folder found at '{PDF_FOLDER}', skipping ingestion.")

# ----------------------------
# 3️⃣ Run server
# ----------------------------
if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
    except ImportError:
        print("Uvicorn is not installed. Install with: pip install 'uvicorn[standard]'")