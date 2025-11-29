import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

# docker-compose 안에서는 서비스 이름으로 접근
WEB_BASE = "http://web:9000"

app = FastAPI(
    title="Local MCP-like Server",
    description="홈페이지 글쓰기 MCP 스타일 툴 서버",
    version="0.0.1",
)

class CreatePostInput(BaseModel):
    title: str
    content: str

@app.post("/tools/create_post")
def create_post_tool(payload: CreatePostInput) -> Dict[str, Any]:
    """
    MCP 툴: create_post
    - 역할: web 서비스에 글을 하나 작성
    """
    res = requests.post(f"{WEB_BASE}/posts", json=payload.dict())
    res.raise_for_status()
    data = res.json()
    return {
        "success": True,
        "message": "홈페이지에 글을 작성했습니다.",
        "post": data["post"],
    }

@app.get("/tools")
def list_tools() -> Dict[str, Any]:
    """
    툴 메타 정보 (MCP의 list_tools 느낌)
    """
    return {
        "tools": [
            {
                "name": "create_post",
                "description": "로컬 홈페이지에 새 글을 작성합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["title", "content"],
                },
            }
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}
