from fastapi import FastAPI
from app.api import admin, chat # Import the routers
from fastapi.middleware.cors import CORSMiddleware # Import CORS Middleware
from fastapi.staticfiles import StaticFiles

# Create the FastAPI application instance
app = FastAPI(
    title="Agentic RAG API",
    description="API for document management and chat with RAG capabilities.",
    version="1.0.0"
)

# --- Add this CORS middleware section ---
# Define the origins that are allowed to connect
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500", # Common port for VS Code Live Server
    "null" # Allow opening the HTML file directly
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)
# --- End of CORS section ---


# Include the routers from the api directory
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
# Add this line at the end to serve the frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/", tags=["Root"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the Agentic RAG API!"}


