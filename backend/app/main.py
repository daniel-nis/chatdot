from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.chat import router as chat_router, html
from app.services.gemini import response

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the WebSocket router
app.include_router(chat_router, prefix="/api/v1")

# Root route for chat interface
@app.get("/")
async def get_chat():
    return HTMLResponse(html)

# Debug route to check if server is running
@app.get("/debug")
async def debug():
    print(response.text)
    return {"routes": [{"path": route.path, "name": route.name} for route in app.routes]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )