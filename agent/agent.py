import os
import requests
from openai import OpenAI

# 환경변수에서 OpenAI 키 읽기
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 필요합니다.")

client = OpenAI(api_key=OPENAI_API_KEY)

# docker-compose 내에서 mcp 서비스 이름으로 접근
MCP_BASE = "http://mcp:9100"

def call_mcp_create_post(title: str, content: str):
    res = requests.post(
        f"{MCP_BASE}/tools/create_post",
        json={"title": title, "content": content},
    )
    res.raise_for_status()
    return res.json()

def main():
    user_prompt = "오늘 서울 날씨에 대해 블로그 글 하나 써줘. 제목도 같이 정해줘."

    system_prompt = """
너는 블로그 글 작성을 도와주는 어시스턴트다.
사용자 요청을 읽고, JSON 형식으로만 응답해라.

형식:
{
  "title": "<글 제목>",
  "content": "<글 내용>"
}
"""

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    data = completion.choices[0].message.parsed
    title = data["title"]
    content = data["content"]

    print("생성된 글 제목:", title)
    print("내용 앞부분:", content[:100], "...")
    print("\nMCP 서버를 통해 홈페이지에 글을 올립니다...")

    result = call_mcp_create_post(title, content)
    print("MCP 결과:", result)

if __name__ == "__main__":
    main()
