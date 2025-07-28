from app.db.database import users_collection
from datetime import datetime

def authorize_user(email: str) -> dict:
    """
    Checks if a user is registered by email. If not, it registers them.
    Returns the user's profile information.
    """
    user = users_collection.find_one({"email": email})
    if user:
        # User exists, return their info
        return {
            "message": f"Welcome back, {user['name']}!",
            "user_id": str(user['_id']),
            "name": user['name'],
            "email": user['email']
        }
    else:
        # User does not exist, create a new one
        new_user = {
            "name": email.split('@')[0], # Simple name generation
            "email": email,
            "created_at": datetime.utcnow()
        }
        result = users_collection.insert_one(new_user)
        return {
            "message": f"Welcome! You've been registered.",
            "user_id": str(result.inserted_id),
            "name": new_user['name'],
            "email": new_user['email']
        }

def get_user_profile(email: str) -> dict:
    """
    Fetches a user's profile from the database using their email.
    """
    user = users_collection.find_one({"email": email})
    if user:
        return {
            "name": user['name'],
            "email": user['email'],
            "joined_on": user['created_at'].isoformat()
        }
    else:
        return {"error": "User not found. Please provide an email to register."}

# A dictionary to map function names to the actual functions
AVAILABLE_FUNCTIONS = {
    "authorize_user": authorize_user,
    "get_user_profile": get_user_profile
}