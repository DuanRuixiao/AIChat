from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio
import random
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

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
    return {"status": "OK", "message": "AI Agent is running", "ai_service": "openai"}

@app.post("/api/chat")
async def chat_endpoint(chat_data: ChatMessage):
    """REST API endpoint for chat"""
    try:
        # Get AI response
        ai_response = await get_openai_response(chat_data.message)
        
        return {
            "message": ai_response,
            "conversationId": chat_data.conversationId
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
                # Get AI response with conversation context
                ai_response = await get_openai_response_with_context(client_id, user_message)
                
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

async def get_openai_response_with_context(client_id: str, user_message: str) -> str:
    """Get OpenAI response with conversation context"""
    try:
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
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        
        return response.choices[0].message.content
        
    except RateLimitError:
        # Use mock response when quota is exceeded
        mock_response = random.choice(mock_responses)
        return f"{mock_response}\n\n[Note: Using demo mode due to quota limit.]"
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Fallback to mock response for any other error
        mock_response = random.choice(mock_responses)
        return f"{mock_response}\n\n[Note: Using demo mode due to service error.]"

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port) 