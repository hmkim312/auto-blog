---
name: blog-discover
description: 13 소스 (HN·GitHub·arXiv·AI 랩 블로그·GeekNews·Reddit·SO·GH Issues) 에서 블로그 주제 후보 10 개 추출
argument-hint: "[--profile <name>]"
---

호출 시점에 한 번 도는 주제 탐색기. 무인증 RSS·공개 API 만 쓴다. 후보 10 개 제목 리스트만 출력하고 사용자가 번호 고르면 `/blog` 안내.

권장 모델: Opus 4.7.

## 사용법

```
/blog-discover
/blog-discover --profile hmkim
```

## 실행 흐름

### 1. 프로파일 로드 (선택)

`--profile <name>` 있으면 `profiles/<name>.yml` Read. `niche`/`tone`/`reader_level`/`interests` 가 점수화 입력. 없어도 진행 (한국 입문자 기본).

### 2. 후보 수집

```bash
uv run scripts/discover-topics.py
```

stdout 으로 JSON 배열. 형식: `{"source","title","url","summary","published"}`.

소스 13 개:
- 트렌드 (8): `hackernews`, `github_trending_python/typescript`, `arxiv_cs_ai`, `openai_blog`, `anthropic_news`, `deepmind_blog`, `geeknews`
- long-tail (5): `reddit_claudeai/cursor/localllama`, `stackoverflow_langchain`, `github_issues_langchain-ai_langchain`

일부 소스 실패해도 stderr 경고만 남고 나머지 정상.

### 3. LLM 점수화 + 중복 병합

평가 기준 (가중치 큰 순):

1. **문제 해결형 long-tail (최대 가산점)**: Reddit/SO/GH Issues 또는 제목이 `Why ~ not working`, `How to ~`, `~ error`, `~ 안 될 때` 형태면 자동 가산. **후보 10 개 중 최소 4 개**는 이 카테고리.
2. **신선도**: 최근 7 일 가산, 30 일+ 감점 (long-tail 질문은 1 년까지 유효).
3. **입문자 적합**: 학술 raw 감점.
4. **글로 풀 만한 거리**: 한 편 (2,000 자+) 분량 줄거리 그려지는가.
5. **한국 검색 수요**: GeekNews 동시 등장 가산.
6. **빅 키워드 회피**: `RAG`, `LLM`, `agent` 단독 감점. 구체 도구명·문제 상황 우선.
7. **프로파일 적합**: `interests`/`niche` 와 겹치면 가산.

중복 토픽 병합 (같은 주제 여러 소스 → 한 줄).

### 4. 후보 10 개 출력 (제목만)

표·이모지·출처·URL·근거 X. 번호 리스트만.

```
주제 후보 10 개입니다. 번호로 고르세요. (다른 후보 보고 싶으면 "다시")

1. ...
10. ...
```

### 5. 사용자 선택 처리

- 번호 → 제목을 한국어 톤으로 정제 (사용자 확인) → "이 주제로 `/blog` 시작?" 동의 시 `/blog <정제 주제>` 안내.
- `다시` → 11~20 위 재출력. 한 세션 최대 2 회.
- 자유 키워드 → 후보 안 가까운 1~3 개 재추천.
- 다 거부하고 직접 입력도 없으면 종료.

### 6. 정탐 (선택)

번호 선택 직후 "글거리 충분한지 사전 확인 Tavily 1 회 돌릴까?" 물음. 동의 시:

```bash
BLOG_RESEARCH_SESSION_ID=discover-$(date +%s)-$$ uv run scripts/tavily-search.py \
  --query "<선택 주제> 2026" --max-results 10 --include-answer
```

별도 세션 ID 라 `/blog` 의 8 회 예산을 안 갉아먹는다. 결과 2~3 줄 요약 → 충분하면 `/blog` 진행, 부족하면 후보 다시.

## 출력 규칙

- **제목만**. 출처·URL·근거·점수·태그 X.
- 정확히 10 개. 부족하면 9 개 이하라도 OK + 사유 한 줄.
- 제목은 사용자가 그대로 `/blog` 에 넣을 형태로 정제. 예:
  - `Anthropic releases Claude 4.7 with extended thinking` → `Claude 4.7 — extended thinking 이 바꾸는 것`
  - long-tail: `Why does Cursor keep looping on tool calls?` → `Cursor 에이전트가 무한 루프에 빠질 때 점검할 것`
- 정제는 한국어 + 사용자 톤. CLAUDE.md 제목 규칙 따르되 키워드성 살린다.
- **저작권 가드**: 영어권 소스는 *주제·문제 지점*만 추출해 한국어로 새로 정제. 원문 제목·요약 직역 X.

## 에러 대응

- 모든 소스 실패 → "외부 소스 모두 실패. 네트워크 또는 API 차단 의심" 출력 후 종료.
- 일부 소스 실패 → stderr 만 (사용자에게 전달 X), 가용 소스로 진행.
- stdout 비면 즉시 종료. 빈 후보 출력 X.

## 규칙

- 재추천 최대 2 회. 그 이상은 "직접 주제 입력해 주세요".
- 정탐 검색은 항상 선택. 자동 실행 X.
- 점수화는 LLM 판단 → 같은 입력에도 결과 조금 달라질 수 있음을 한 번은 안내.
