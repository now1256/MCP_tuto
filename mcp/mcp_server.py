# mcp/mcp_server.py
import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import google.generativeai as genai

app = FastAPI()

WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://web:9000")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    # 굳이 JSON 안 쓰고 텍스트로 받을 거면 이 설정은 생략 가능
)


class CreatePostRequest(BaseModel):
    prompt: str


@app.post("/create_post")
async def create_post(req: CreatePostRequest):
    print(f"[MCP] /create_post 호출! prompt 길이 = {len(req.prompt)}")

    # 1) Gemini로 글 생성
    full_prompt = req.prompt  # 네가 이미 web 쪽에서 알아서 만든 프롬프트

    try:
        response = model.generate_content(full_prompt)
        content = (response.text or "").strip()
        print(f"[MCP] Gemini 응답 앞 80자: {content[:80]!r}")
    except Exception as e:
        print("[MCP] Gemini 호출 실패:", e)
        # 실패하면 fallback으로라도 포스트 하나는 생성
        content = f"테스트 포스트 (임시 생성)\n\n원본 프롬프트:\n{full_prompt}"

    # 2) 첫 줄 = 제목, 나머지 = 본문
    lines = content.splitlines()
    title = lines[0].strip() if lines else "제목 없음"
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else title

    print(f"[MCP] 최종 제목: {title!r}")

    # 3) web /posts 로 전송
    target_url = f"{WEB_BASE_URL}/posts"
    try:
        print(f"[MCP] web /posts 호출 시도: {target_url}")
        resp = requests.post(
            target_url,
            json={"title": title, "content": body},
            timeout=30,
        )
        print("[MCP] web /posts 응답 코드:", resp.status_code)
        print("[MCP] web /posts 응답 내용 앞 100자:", resp.text[:100])
        resp.raise_for_status()
    except Exception as e:
        print("[MCP] web /posts 호출 실패:", e)
        return {"error": f"web /posts 호출 실패: {e}"}

    return {"status": "ok", "title": title}
