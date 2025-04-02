import os
from typing import Dict, Optional, List
import openai
import google.generativeai as genai
import requests
import logging
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

class AIServices:
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.gemini_chat = None
        self.grok_api_key = None

    def setup_openai(self, api_key: str):
        """Setup OpenAI client with API key"""
        openai.api_key = api_key

    def setup_gemini_with_credentials(self, credentials: Credentials):
        """Setup Gemini with OAuth credentials"""
        try:
            genai.configure(credentials=credentials)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            # Initialize a new chat
            self.gemini_chat = self.gemini_model.start_chat(history=[])
            return True
        except Exception as e:
            logger.error(f"Error setting up Gemini: {e}")
            return False

    def setup_grok(self, api_key: str):
        """Setup Grok with API key"""
        self.grok_api_key = api_key

    def format_history_for_gemini(self, history: List[Dict]) -> List[Dict]:
        """Format conversation history for Gemini"""
        formatted_history = []
        for entry in history:
            role = "user" if entry["type"] == "user" else "assistant"
            formatted_history.append({
                "role": role,
                "parts": [entry["message"]]
            })
        return formatted_history

    async def get_chatgpt_response(self, message: str) -> str:
        """Get response from ChatGPT"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with ChatGPT: {str(e)}"

    async def get_gemini_response(self, message: str, history: Optional[List[Dict]] = None) -> str:
        """Get response from Gemini with conversation history"""
        try:
            if not self.gemini_model:
                return "Gemini is not configured. Please authenticate first."

            # Create a new chat for each request with the provided history
            formatted_history = self.format_history_for_gemini(history) if history else []
            chat = self.gemini_model.start_chat(history=formatted_history)
            
            # Send the message and get response
            response = await chat.send_message_async(message)
            return response.text
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            return f"Error with Gemini: {str(e)}"

    async def get_grok_response(self, message: str) -> str:
        """Get response from Grok"""
        try:
            if not self.grok_api_key:
                return "Grok API key not set"
            # Note: Replace with actual Grok API endpoint when available
            response = requests.post(
                "https://api.grok.ai/v1/chat",
                headers={"Authorization": f"Bearer {self.grok_api_key}"},
                json={"message": message}
            )
            return response.json().get("response", "Error with Grok API")
        except Exception as e:
            return f"Error with Grok: {str(e)}"

    async def get_all_responses(self, message: str) -> Dict[str, str]:
        """Get responses from all AI services"""
        responses = {}
        
        # Get responses in parallel
        responses["chatgpt"] = await self.get_chatgpt_response(message)
        responses["gemini"] = await self.get_gemini_response(message)
        responses["grok"] = await self.get_grok_response(message)
        
        return responses 