from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict, List
from app.services.gemini import ChatSession
import asyncio
import json

router = APIRouter()

html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <h2>Your ID: <span id='clientId'></span></h2>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages' style="list-style-type: none; padding: 0;">
            </ul>
            <script>
                var clientId = Date.now()
                document.querySelector("#clientId").innerText = clientId
                
                var ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${clientId}`)
                
                ws.onmessage = function(event) {
                    addMessage('dot', event.data)
                }
                
                function addMessage(sender, content) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    message.style.margin = '10px 0'
                    message.style.padding = '10px'
                    message.style.borderRadius = '5px'
                    
                    // Different styles for user and bot messages
                    if (sender === 'user') {
                        message.style.backgroundColor = '#e3f2fd'
                        message.style.textAlign = 'right'
                        content = 'You: ' + content
                    } else {
                        message.style.backgroundColor = '#f5f5f5'
                        message.style.textAlign = 'left'
                        content = 'dot: ' + content
                    }
                    
                    var contentNode = document.createTextNode(content)
                    message.appendChild(contentNode)
                    messages.appendChild(message)
                    
                    // Auto scroll to bottom
                    messages.scrollTop = messages.scrollHeight
                }
                
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    var message = input.value
                    if (message.trim()) {
                        // Add user message to chat
                        addMessage('user', message)
                        // Send to WebSocket
                        ws.send(message)
                    }
                    input.value = ''
                    event.preventDefault()
                }
                
                // Handle WebSocket connection status
                ws.onopen = function(event) {
                    console.log('Connected to WebSocket')
                }
                
                ws.onclose = function(event) {
                    console.log('WebSocket connection closed')
                    // You might want to show a reconnection message here
                }
                
                ws.onerror = function(event) {
                    console.error('WebSocket error:', event)
                }
            </script>
        </body>
    </html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.chat_sessions: Dict[int, ChatSession] = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.chat_sessions[client_id] = ChatSession(str(client_id))

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.chat_sessions:
            self.chat_sessions[client_id].cleanup()
            del self.chat_sessions[client_id]

    async def process_and_send_message(self, client_id: int, message: str):
        if client_id not in self.chat_sessions or client_id not in self.active_connections:
            return
        
        try:
            chat_session = self.chat_sessions[client_id]
            websocket = self.active_connections[client_id]
            
            # Generate response
            #response = await chat_session.generate_response(message)
            async for response in chat_session.generate_streaming_response(message):
                await websocket.send_text(json.dumps(response))
            
            # Send response if connection is still open
            if client_id in self.active_connections:
                await websocket.send_text(response)
                
        except Exception as e:
            print(f"Error processing message: {e}")
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_text(f"oops, something went wrong! try again?")

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Wait for message
            message = await websocket.receive_text()
            # Process message in background without awaiting
            asyncio.create_task(manager.process_and_send_message(client_id, message))
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)