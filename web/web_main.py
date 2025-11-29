from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Local Homepage API")

POSTS: List[dict] = []

class PostCreate(BaseModel):
    title: str
    content: str

@app.post("/posts")
def create_post(post: PostCreate):
    new_post = {
        "id": len(POSTS) + 1,
        "title": post.title,
        "content": post.content,
    }
    POSTS.append(new_post)
    return {"success": True, "post": new_post}

@app.get("/posts")
def list_posts():
    return {"posts": POSTS}

@app.get("/health")
def health():
    return {"status": "ok"}
