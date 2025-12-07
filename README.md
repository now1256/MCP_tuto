# MCP + Gemini Demo (web + mcp 구조)

간단한 **ChatGPT 스타일 웹 UI**에서 입력을 받으면,

1. `web` 서비스가 프롬프트를 만들고
2. `mcp` 서비스에 `/create_post` 요청을 보냄
3. `mcp`가 Gemini로 글을 생성한 뒤
4. 다시 `web`의 `/posts` API를 호출해서 글을 저장
5. `/posts` 페이지에서 생성된 글을 확인

구조를 Docker로 구성

---

## 📦 전체 구조

도커 기준 서비스 구성은 다음과 같습니다.

```text
브라우저
  ↓
[web 컨테이너 : mcp-web]  (포트 9000)
  - FastAPI
  - "/"  : 입력 폼 UI
  - "/generate" : MCP에 글 생성 요청
  - "/posts" : 생성된 글 인메모리 저장

  ↓ HTTP (MCP_BASE_URL)

[mcp 컨테이너 : mcp-server] (포트 9100)
  - FastAPI
  - "/create_post" : 프롬프트를 받아 Gemini로 글 생성
                   → web "/posts" 로 전달

  ↓ Google API

[Gemini API]
