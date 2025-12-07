# web/web_main.py

import os
import requests
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI()

MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://mcp:9100")

posts = []


class Post(BaseModel):
    title: str
    content: str


@app.get("/", response_class=HTMLResponse)
async def index():
    # 여긴 async여도 됨 (블로킹 I/O 없음)
    html = """
    <html>
      <head>
        <title>MCP 튜토 - 메인</title>
      </head>
      <body>
        <h1>MCP TUTO - 글 생성 요청</h1>
        <form method="post" action="/generate">
          <label>글 아이디어 / 한 줄 설명:</label><br />
          <textarea name="user_input" rows="4" cols="60"></textarea><br /><br />
          <button type="submit">AI에게 글 써달라고 보내기</button>
        </form>
        <hr />
        <a href="/posts">포스팅 목록 보기</a>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/generate")   # ⬅️ 여기! async 빼고 그냥 def
def generate(user_input: str = Form(...)):
    """
    여기서는 동기 requests.post를 쓰니까,
    핸들러 자체를 def로 두는 게 안전하다.
    FastAPI가 알아서 threadpool에서 실행해줌.
    """
    prompt = f"""
    아래 내용을 바탕으로 블로그 글을 한국어로 작성해줘.

    - 글 주제/아이디어: {user_input}

    형식:
    1. 첫 줄에 글 제목
    2. 그 아래에 본문(여러 단락)
    """

    try:
        resp = requests.post(
            f"{MCP_BASE_URL}/create_post",
            json={"prompt": prompt},
            timeout=60,
        )
        resp.raise_for_status()
    except Exception as e:
        return {"error": f"MCP 서버 호출 실패: {e}"}

    return RedirectResponse(url="/posts", status_code=303)


@app.post("/posts")
async def create_post(post: Post):
    posts.append(post)
    return {"status": "ok"}


@app.get("/posts", response_class=HTMLResponse)
async def list_posts():
    body = "<h1>포스팅 목록</h1>"
    body += '<a href="/">← 메인으로</a><br /><br />'

    if not posts:
        body += "<p>아직 포스팅이 없습니다.</p>"
    else:
        for i, p in enumerate(posts, start=1):
            body += f"<hr/><h2>{i}. {p.title}</h2>"
            body += "<pre style='white-space:pre-wrap;'>" + p.content + "</pre>"

    html = f"<html><body>{body}</body></html>"
    return HTMLResponse(content=html)
