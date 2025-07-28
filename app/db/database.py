from pymongo import MongoClient
from app.core.config import settings

# ... (keep variable definitions) ...
client = None
db = None
documents_collection = None
chunks_collection = None
users_collection = None

try:
    # --- MODIFY THIS LINE ---
    # Increase the server selection timeout to 30 seconds (30000ms)
    client = MongoClient(settings.MONGO_DB_URL, serverSelectionTimeoutMS=30000)
    
    # ... (rest of the try block is the same) ...
    client.admin.command('ismaster') 
    db = client[settings.DB_NAME]
    documents_collection = db["documents"]
    chunks_collection = db["text_chunks"]
    users_collection = db["users"]
    print("✅ Database connection successful.")
except Exception as e:
    # ... (except block is the same) ...
    print(f"❌ Database connection failed: {e}")

# ... (get_db function is the same) ...
def get_db():
    if db is None:
        raise Exception("Database is not connected. Please check your connection settings and ensure MongoDB is running.")
    return db