import google.generativeai as genai
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging
from enum import Enum
from fastapi import WebSocket
import json

genai.configure(api_key="AIzaSyB31TTDkSRm-PH7V61JIm7BloppLCy1F7I")

class ChatSession:
    def __init__(self, session_id: str):
        # Configuration settings
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 300,
            "response_mime_type": "text/plain",
        }

        # System instruction for dot's personality
        self.system_instruction = "you are a persona named dot. your conversational style is informal and all lowercase, characterized by humor, acting stupid, and support. your responses are goofy, often unserious, and you engage in playful roasting, but always in a friendly manner. you are not corny and don't overuse female slang and don't use the word 'like' a lot. you love anime. you use modern slang often and barely ever use emojis. your posts are animated, supportive, but you are a mysterious and cool figure with a lot of aura. your interactions should blend hype, aura, encouragement, and stupidity to keep conversations engaging and fun."

        # Initialize model and session
        self.session_id = session_id
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=self.generation_config,
            system_instruction=self.system_instruction
        )
        
        # Initialize chat with history structure
        self.history = []
        self.chat = self.model.start_chat(history=self.history)
        self.last_active = datetime.now()

    def update_timestamp(self):
        """Update last active timestamp"""
        self.last_active = datetime.now()

    def add_to_history(self, role: str, content: str):
        """Add message to history in correct format"""
        message = {
            "role": role,
            "parts": [content]
        }
        self.history.append(message)

    def get_history(self) -> List[Dict]:
        """Get chat history"""
        return self.history

    async def generate_response(self, message: str):
        """Generate response using the model"""
        try:
            # Add user message to history
            self.add_to_history("user", message)
            self.update_timestamp()

            # Generate response
            response = self.chat.send_message(message)
            response_text = response.text

            # Add model response to history
            self.add_to_history("model", response_text)
            
            return response_text

        except Exception as e:
            print(f"Error generating response: {e}")
            raise

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired"""
        elapsed = datetime.now() - self.last_active
        return elapsed.total_seconds() > (timeout_minutes * 60)

    def cleanup(self):
        """Cleanup method for session resources"""
        self.history.clear()

    async def generate_streaming_response(self, message: str):
        try:
            self.add_to_history("user", message)
            
            # Generate streaming response
            response = self.model.generate_content(
                message,
                stream=True
            )
            
            partial_response = ""
            for chunk in response:
                if chunk.text:
                    partial_response += chunk.text
                    yield {
                        "type": "partial",
                        "content": chunk.text
                    }
            
            self.add_to_history("model", partial_response)
            
            yield {
                "type": "complete",
                "content": partial_response
            }
                
        except Exception as e:
            print(f"Error generating response: {e}")
            yield {
                "type": "error",
                "content": str(e)
            }

class GeminiService:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.model = None

    async def create_session(self) -> str:
        session_id = datetime.now().isoformat()
        self.sessions[session_id] = ChatSession(session_id, [])
        return session_id

    async def process_message(self, session_id: str, message: str):
        pass

    async def handle_history(self, session_id: str):
        pass

    def _clean_up_old_sessions(self):
        pass

    def _handle_rate_limit(self):
        pass

    async def _stream_response(self, session_id: str, message: str):
        pass