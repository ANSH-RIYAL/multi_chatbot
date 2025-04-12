from fastapi import FastAPI, HTTPException, status, Request, Depends
import logging
from dotenv import load_dotenv
from typing import Dict, Optional, List
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
import google.generativeai as genai
import openai
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Default API keys for testing (replace with your test keys)
DEFAULT_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),  # Free tier Gemini key
    "openai": None,  # No default key for paid service
    "grok": None    # No default key for paid service
}

# Model configurations
MODEL_CONFIGS = {
    "gemini": {
        "free": "gemini-pro",  # Actually free with quota
        "paid": None  # No paid tier needed for demo
    },
    "openai": {
        "free": "gpt-3.5-turbo",  # Not actually free
        "paid": "gpt-4"
    },
    "grok": {
        "free": "grok-1",  # Requires X Premium
        "paid": "grok-2"
    }
}

# Create FastAPI app
app = FastAPI(title="Multi-Chatbot Interface")
logger.info("FastAPI application created")

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store conversation history
history_file = "data/conversation_history.json"

def load_history(user_id: str) -> list:
    """Load conversation history for a user"""
    try:
        with open(history_file, 'r') as f:
            histories = json.load(f)
            return histories.get(user_id, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(user_id: str, history: list):
    """Save conversation history for a user"""
    try:
        with open(history_file, 'r') as f:
            histories = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        histories = {}
    
    histories[user_id] = history
    with open(history_file, 'w') as f:
        json.dump(histories, f)

# Pydantic models
class ServiceKeys(BaseModel):
    gemini: Optional[str] = None
    openai: Optional[str] = None
    grok: Optional[str] = None
    user_id: str
    models: Dict[str, str]

class ChatMessage(BaseModel):
    message: str
    user_id: str
    service_keys: ServiceKeys

class HistoryEntry(BaseModel):
    type: str
    message: str
    source: Optional[str] = None
    user_id: str

async def get_gemini_response(message: str, history: List[Dict], api_key: str, model: str) -> str:
    try:
        # Use default key if none provided
        api_key = api_key or DEFAULT_KEYS["gemini"]
        if not api_key:
            return "Please configure a valid Gemini API key"

        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        # Format conversation for context
        context = "Previous conversation:\n"
        for entry in history[-5:]:
            role = "User" if entry["type"] == "user" else "Assistant"
            context += f"{role}: {entry['message']}\n"
        
        prompt = f"{context}\nUser: {message}\nAssistant:"
        
        try:
            response = await model_instance.generate_content_async(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                return "Free tier quota reached. Please try again later or use your own API key."
            raise e
            
    except Exception as e:
        logger.error(f"Error with Gemini: {e}")
        error_msg = str(e)
        if "quota" in error_msg.lower() or "billing" in error_msg.lower():
            return "Rate limit reached. Please try again later or use your own API key."
        return f"Error with Gemini: {error_msg}"

async def get_openai_response(message: str, history: List[Dict], api_key: str, model: str) -> str:
    try:
        # Use default key if none provided
        api_key = api_key or DEFAULT_KEYS["openai"]
        if not api_key or api_key == "YOUR_TEST_OPENAI_KEY":
            return "Please configure a valid OpenAI API key"

        client = openai.OpenAI(api_key=api_key)
        
        # Format conversation history for OpenAI
        messages = []
        for entry in history[-5:]:
            role = "user" if entry["type"] == "user" else "assistant"
            messages.append({"role": role, "content": entry["message"]})
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error with OpenAI: {e}")
        error_msg = str(e)
        if "429" in str(e) or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return "Rate limit reached. Please try again later or use your own API key."
        return f"Error with OpenAI: {error_msg}"

async def get_grok_response(message: str, history: List[Dict], api_key: str, model: str) -> str:
    try:
        # Use default key if none provided
        api_key = api_key or DEFAULT_KEYS["grok"]
        if not api_key or api_key == "YOUR_TEST_GROK_KEY":
            return "Please configure a valid Grok API key"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Format conversation history
        context = "\n".join([
            f"{'User' if entry['type'] == 'user' else 'Assistant'}: {entry['message']}"
            for entry in history[-5:]
        ])
        
        data = {
            "messages": [{"role": "user", "content": f"{context}\nUser: {message}"}],
            "model": model
        }
        
        # Replace with actual Grok API endpoint
        response = requests.post(
            "https://api.grok.x.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error with Grok: {e}")
        error_msg = str(e)
        if "429" in str(e) or "quota" in error_msg.lower():
            return "Rate limit reached. Please try again later or use your own API key."
        return f"Error with Grok: {error_msg}"

@app.get("/")
async def home(request: Request):
    """Serve the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Send message to all configured AI services"""
    # Load conversation history
    history = load_history(message.user_id)
    history.append({
        "type": "user",
        "message": message.message
    })
    
    responses = {}
    
    # Get responses from each configured service
    if message.service_keys.gemini or DEFAULT_KEYS["gemini"]:
        responses["gemini"] = await get_gemini_response(
            message.message, 
            history, 
            message.service_keys.gemini,
            message.service_keys.models["gemini"]
        )
    
    if message.service_keys.openai or DEFAULT_KEYS["openai"]:
        responses["openai"] = await get_openai_response(
            message.message, 
            history, 
            message.service_keys.openai,
            message.service_keys.models["openai"]
        )
    
    if message.service_keys.grok or DEFAULT_KEYS["grok"]:
        responses["grok"] = await get_grok_response(
            message.message, 
            history, 
            message.service_keys.grok,
            message.service_keys.models["grok"]
        )
    
    save_history(message.user_id, history)
    return responses

@app.post("/api/select_response")
async def select_response(entry: HistoryEntry):
    """Save selected response to conversation history"""
    history = load_history(entry.user_id)
    history.append({
        "type": entry.type,
        "message": entry.message,
        "source": entry.source
    })
    save_history(entry.user_id, history)
    return {"status": "success"}

@app.get("/api/history")
async def get_history(user_id: str):
    """Get conversation history"""
    return load_history(user_id)

@app.post("/api/feedback")
async def record_feedback(
    message_id: str,
    service: str,
    feedback: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """Record user feedback for a response"""
    ai_service.record_feedback(message_id, service, feedback)
    return {"status": "success"}

@app.get("/api/metrics")
async def get_metrics(ai_service: AIService = Depends(get_ai_service)):
    """Get performance metrics for all services"""
    return ai_service.get_performance_metrics()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000) 