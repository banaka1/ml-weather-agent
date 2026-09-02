from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import agent


app = FastAPI()

# 定义请求模型
class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat(req: ChatRequest):
    reply = agent.test_chat_openai(req.message)
    return {"reply": reply}