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
        self.feedback_db = {}  # Simple in-memory storage for feedback
        self.cost_tracker = {}  # Track API costs
        self.ab_testing = True  # Enable A/B testing

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

    async def get_response(self, message: str, service: str) -> str:
        # Track API call
        self._track_api_call(service)
        
        # Get response from service
        response = await self._call_service(service, message)
        
        # If A/B testing is enabled, randomly select response format
        if self.ab_testing:
            response = self._apply_ab_testing(response)
            
        return response
    
    def _track_api_call(self, service: str):
        """Track API calls and costs"""
        if service not in self.cost_tracker:
            self.cost_tracker[service] = {
                'calls': 0,
                'total_cost': 0.0
            }
        self.cost_tracker[service]['calls'] += 1
        # Add actual cost calculation based on service pricing
        
    def _apply_ab_testing(self, response: str) -> str:
        """Apply A/B testing variations to response"""
        import random
        if random.random() < 0.5:  # 50% chance for each variation
            return response.upper()  # Variation A
        return response.lower()  # Variation B
        
    def record_feedback(self, message_id: str, service: str, feedback: str):
        """Record user feedback for a response"""
        if message_id not in self.feedback_db:
            self.feedback_db[message_id] = {}
        self.feedback_db[message_id][service] = feedback
        
    def get_performance_metrics(self) -> dict:
        """Get performance metrics for all services"""
        metrics = {
            'total_calls': sum(service['calls'] for service in self.cost_tracker.values()),
            'total_cost': sum(service['total_cost'] for service in self.cost_tracker.values()),
            'feedback_summary': {
                'positive': sum(1 for feedbacks in self.feedback_db.values() 
                              for feedback in feedbacks.values() if feedback == 'positive'),
                'negative': sum(1 for feedbacks in self.feedback_db.values() 
                              for feedback in feedbacks.values() if feedback == 'negative')
            }
        }
        return metrics 