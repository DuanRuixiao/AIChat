from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio
import random
import httpx
from typing import Dict, List
import os
from dotenv import load_dotenv
import openai
from openai import OpenAIError, RateLimitError
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

# AI Service Configuration
AI_SERVICE = os.getenv("AI_SERVICE", "ollama")  # Options: "openai", "ollama", "huggingface"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # or "mistral", "codellama", etc.
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Mock AI responses for when quota is exceeded
mock_responses = [
    "Hello! I'm your AI assistant. I'm here to help you with any questions or tasks.",
    "That's an interesting question! Let me think about that for a moment...",
    "I understand what you're asking. Here's what I can tell you about that topic.",
    "Great question! Based on what I know, here's my perspective on this.",
    "I'd be happy to help you with that. Let me provide some information that might be useful.",
    "That's a thoughtful question. Here are some points to consider...",
    "I appreciate you asking that. Let me share some insights with you.",
    "Interesting topic! Here's what I think about this subject.",
    "I'm here to assist you with any questions you might have.",
    "That's a great point! Let me elaborate on that for you."
]

# Store active connections and conversations
active_connections: Dict[str, WebSocket] = {}
conversations: Dict[str, List[Dict]] = {}

class ChatMessage(BaseModel):
    message: str
    conversationId: str

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "OK", "message": "AI Agent is running", "ai_service": AI_SERVICE}

@app.post("/api/chat")
async def chat_endpoint(chat_data: ChatMessage):
    """REST API endpoint for chat"""
    try:
        # Get AI response
        ai_response = await get_ai_response(chat_data.message)
        
        return {
            "message": ai_response,
            "conversationId": chat_data.conversationId
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_ai_response(user_message: str) -> str:
    """Get AI response from configured AI service"""
    try:
        if AI_SERVICE == "ollama":
            return await get_ollama_response(user_message)
        elif AI_SERVICE == "huggingface":
            return await get_huggingface_response(user_message)
        elif AI_SERVICE == "openai":
            return await get_openai_response(user_message)
        else:
            # Fallback to mock response
            mock_response = random.choice(mock_responses)
            return f"{mock_response}\n\n[Note: Using demo mode. Configure AI_SERVICE in .env]"
            
    except Exception as e:
        print(f"AI service error: {e}")
        # Fallback to mock response for any error
        mock_response = random.choice(mock_responses)
        return f"{mock_response}\n\n[Note: Using demo mode due to AI service error.]"

async def get_ollama_response(user_message: str) -> str:
    """Get response from Ollama (local AI)"""
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": f"You are a helpful AI assistant. Be concise, friendly, and helpful in your responses.\n\nUser: {user_message}\nAssistant:",
                    "stream": False
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "I'm sorry, I couldn't generate a response.")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
    except Exception as e:
        print(f"Ollama error: {e}")
        raise e

async def get_huggingface_response(user_message: str) -> str:
    """Get response from Hugging Face Inference API"""
    if not HUGGINGFACE_API_KEY:
        raise Exception("Hugging Face API key not configured")
        
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                json={"inputs": user_message},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result[0].get("generated_text", "I'm sorry, I couldn't generate a response.")
            else:
                raise Exception(f"Hugging Face API error: {response.status_code}")
                
    except Exception as e:
        print(f"Hugging Face error: {e}")
        raise e

async def get_openai_response(user_message: str) -> str:
    """Get response from OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Be concise, friendly, and helpful in your responses."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=500,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
        
    except RateLimitError:
        # Use mock response when quota is exceeded
        mock_response = random.choice(mock_responses)
        return f"{mock_response}\n\n[Note: Using demo mode due to OpenAI quota limit. Add billing to your OpenAI account for full AI responses.]"
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Fallback to mock response for any other error
        mock_response = random.choice(mock_responses)
        return f"{mock_response}\n\n[Note: Using demo mode due to API error.]"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    client_id = str(id(websocket))
    active_connections[client_id] = websocket
    conversations[client_id] = []
    
    print(f"User connected: {client_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            conversation_id = message_data.get("conversationId", "")
            
            # Add user message to conversation history
            conversations[client_id].append({
                "role": "user",
                "content": user_message
            })
            
            # Send typing indicator
            await websocket.send_text(json.dumps({
                "type": "typing",
                "isTyping": True
            }))
            
            try:
                # Get AI response
                ai_response = await get_ai_response_with_context(client_id, user_message)
                
                # Add AI response to conversation history
                conversations[client_id].append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                # Stop typing indicator
                await websocket.send_text(json.dumps({
                    "type": "typing",
                    "isTyping": False
                }))
                
                # Send AI response
                await websocket.send_text(json.dumps({
                    "type": "receiveMessage",
                    "message": ai_response,
                    "conversationId": conversation_id
                }))
                
            except Exception as e:
                print(f"Error processing message: {e}")
                # Stop typing indicator
                await websocket.send_text(json.dumps({
                    "type": "typing",
                    "isTyping": False
                }))
                
                # Send error message
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Sorry, I encountered an error. Please try again."
                }))
                
    except WebSocketDisconnect:
        print(f"User disconnected: {client_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Clean up
        if client_id in active_connections:
            del active_connections[client_id]
        if client_id in conversations:
            del conversations[client_id]

async def get_ai_response_with_context(client_id: str, user_message: str) -> str:
    """Get AI response with conversation context"""
    try:
        if AI_SERVICE == "ollama":
            # For Ollama, we'll send the full conversation context
            conversation_history = conversations[client_id][-10:]  # Last 10 messages
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            context += f"\nuser: {user_message}\nassistant:"
            
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": f"You are a helpful AI assistant. Be concise, friendly, and helpful in your responses.\n\n{context}",
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "I'm sorry, I couldn't generate a response.")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
                    
        elif AI_SERVICE == "openai":
            # Prepare conversation history for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Be concise, friendly, and helpful in your responses."
                }
            ]
            
            # Add conversation history (last 10 messages to avoid token limits)
            conversation_history = conversations[client_id][-10:]
            messages.extend(conversation_history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Try OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        else:
            # For other services, just get a simple response
            return await get_ai_response(user_message)
        
    except RateLimitError:
        # Use mock response when quota is exceeded
        mock_response = random.choice(mock_responses)
        return f"{mock_response}\n\n[Note: Using demo mode due to quota limit.]"
        
    except Exception as e:
        print(f"AI service error: {e}")
        # Fallback to mock response for any other error
        mock_response = random.choice(mock_responses)
        return f"{mock_response}\n\n[Note: Using demo mode due to service error.]"

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port) 