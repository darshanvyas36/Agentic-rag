from fastapi import APIRouter, HTTPException, status, Body
from app.services import rag_service, function_service
from app.core.config import settings
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

router = APIRouter()

# Configure the generative model
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Define the tools (functions) the model can use
tools = [
    {
        "name": "authorize_user",
        "description": "Check if user is registered and return user info or register if new.",
        "parameters": {
            "type": "OBJECT", # Was: "object"
            "properties": {
                "email": {
                    "type": "STRING", # Changed from "string"
                    "description": "User's email address"
                }
            },
            "required": ["email"]
        }
    },
    {
        "name": "get_user_profile",
        "description": "Fetch user profile from the database.",
        "parameters": {
            "type": "OBJECT", # Was: "object"
            "properties": {
                "email": {
                    "type": "STRING", # Changed from "string"
                    "description": "User's email address"
                }
            },
            "required": ["email"]
        }
    }
]


# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=tools,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)


@router.post("/chat")
async def chat_handler(payload: dict = Body(...)):
    user_prompt = payload.get("prompt")
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")

    try:
        # 1. Send the prompt to the model
        response = model.generate_content(user_prompt)
        
        # --- CORRECTED CHECK ---
        # 2. Safely check if the model wants to call a function
        if hasattr(response, 'function_calls') and response.function_calls:
            function_call = response.function_calls[0]
            function_name = function_call.name
            args = function_call.args

            # 3. Execute the function
            if function_name in function_service.AVAILABLE_FUNCTIONS:
                api_function = function_service.AVAILABLE_FUNCTIONS[function_name]
                function_response = api_function(**dict(args))

                # 4. Send the function's result back to the model
                final_response = model.generate_content(
                    [user_prompt, response, function_response]
                )
                return {"response": final_response.text}
            else:
                return {"response": "Sorry, I can't call that function."}

        # 5. If no function call, perform a RAG search
        else:
            context_chunks = rag_service.search_rag(user_prompt)
            if not context_chunks:
                # If no relevant context, just use the original prompt's text
                return {"response": response.text}

            # 6. Augment the prompt with RAG context
            augmented_prompt = (
                "Based ONLY on the following context, answer the user's question.\n"
                "If the context does not contain the answer, say you don't have enough information.\n\n"
                "CONTEXT:\n"
                f"{' '.join(context_chunks)}\n\n"
                "USER QUESTION:\n"
                f"{user_prompt}"
            )
            final_response = model.generate_content(augmented_prompt)
            return {"response": final_response.text}

    except Exception as e:
        # Send the actual error message to the frontend for easier debugging
        raise HTTPException(status_code=500, detail=f"An error occurred: '{str(e)}'")