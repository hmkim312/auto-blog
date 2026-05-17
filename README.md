# auto-blog

Claude Code 기반 한국어 기술 블로그 자동 생성 파이프라인. 영문 자료를 한국어 글로 옮길 때 직번역체를 차단하기 위해 **번역과 작문을 분리**한다 — 메인 Claude (Opus) 가 영문을 한국어 사실 카드로 옮긴 뒤 본문도 직접 쓰고, Opus sub-agent 가 다른 컨텍스트에서 독립 검수한다.

## 사용법

```bash
/blog                  # 주제 탐색 → 사실 카드 → 작성 → 검수 → 카드 → X 요약
/blog uv 패키지 매니저  # 주제 직접 지정

# 단계별 단독 호출
/blog-discover         # 13 소스에서 주제 후보 10 개
/blog-review [파일]     # 검수 리포트 (--fix 안전 치환)
/blog-cards [파일]      # 초안의 `## 이미지 메타` → WebP
```

생성물은 `posts/YYYY-MM-DD-<슬러그>.md`, 이미지는 `posts/images/<슬러그>/*.webp`. 모두 gitignore. 워드프레스에 수동 붙여넣기.

## 사전 준비

- Claude Code (메인 모델 Opus 4.7 권장)
- Python + `uv`
- Tavily API 키 (`.env` 에 `TAVILY_API_KEY=tvly-...`)
- Playwright Chromium (1 회): `uv run --with playwright python -m playwright install chromium`

## 모델 분리 정책

| 역할 | 모델 |
|------|------|
| 오케스트레이션·번역·카드 메타·X 요약 | Opus (메인 Claude) |
| 본문 한국어 작성 | Opus (메인 Claude 직접) |
| 본문 검수 | Opus (sub-agent, `model=opus`) |

작성과 검수를 다른 컨텍스트로 분리해 자기 합리화를 차단한다. 같은 컨텍스트 자가 검수는 직번역체를 못 잡는다 (회귀 검증 2 회).

## 구조

```
auto-blog/
├── CLAUDE.md                  # 글쓰기 규칙 단일 정관
├── README.md                  # 이 파일
├── internal-links.md          # ILJ 키워드 표 (들어오는·나가는)
├── profiles/<name>.yml        # 필자별 프로파일 (커밋 대상)
├── posts/                     # 생성된 글·이미지 (gitignore)
├── templates/cards/           # /blog-cards 템플릿 15 개
├── scripts/
│   ├── discover-topics.py    # /blog-discover (13 소스)
│   ├── tavily-search.py      # /blog 검색 (세션별 ≤8 회 강제)
│   └── render-cards.py       # /blog-cards (Playwright + Jinja2)
└── .claude/skills/
    ├── blog/                  # 메인 파이프라인 (전 단계 통합)
    ├── blog-discover/         # 주제 탐색
    ├── blog-review/           # 검수 (--judge JSON · --fix 치환)
    └── blog-cards/            # 카드 렌더
```

## 프로파일

`profiles/<name>.yml` 에 필자 컨셉·톤·검색 취향. `/blog --profile <name>` 으로 적용.

| 필드 | 설명 |
|------|------|
| `name` (필수) | 파일명과 일치 |
| `niche` (필수) | 블로그 한 줄 요약 |
| `reader_level` (필수) | 대상 독자 |
| `persona` | 1인칭 자유 서술 (경험 섹션 톤) |
| `preferred_topics` / `avoid_topics` | 키워드 리스트 |
| `search_bias.region` / `.language` | Tavily 검색 힌트 |

샘플은 `profiles/example.yml`, `profiles/hmkim.yml`.

## 글쓰기 규칙

`CLAUDE.md` 가 단일 정관. 핵심 원칙 5 가지:

1. 결론 먼저
2. 짧게 (한 문장 40 자, 한 단락 2~4 문장)
3. 능동형
4. 한 문장 한 가지 내용
5. 추상 주장은 숫자·예시·코드·상황으로 받침

대체 표현 표·도입부·SEO·카드 작성 원칙은 CLAUDE.md 참조.

## AI 에게 (작업 가이드)

- **이 프로젝트에는 AGENTS.md 를 만들지 않는다**. 디렉토리별 가이드가 필요하면 `CLAUDE.md` 를 그 자리에 두거나, 이 파일 (README.md) 에 흡수.
- 본문 작성은 메인 Claude (Opus) 가 직접. 검수는 Opus sub-agent (`Agent`, `subagent_type: claude`, `model: opus`) — 같은 모델이라도 다른 컨텍스트.
- 영문 Tavily 결과는 작성 단계 컨텍스트에 직접 노출 X. 한국어 사실 카드를 거친 뒤에만 작성 단계로.
- 사실·수치·인용·URL 은 카드 + 사용자 Q&A 가 정답. 개념 설명·비유는 Opus 본인 지식으로 보강 OK.
- 워드프레스 자동 업로드 범위 밖. 수동 붙여넣기.
- Python 스크립트는 `uv run scripts/<파일>.py` (PEP 723 인라인 deps).
- `/blog-cards` 최초 1 회: `uv run --with playwright python -m playwright install chromium`.
