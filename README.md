# auto-blog

Claude Code 로 워드프레스 블로그 글 초안과 이미지를 자동 생성하는 프로젝트.

## 핵심 흐름

영문 자료를 LLM 한 번에 한국어 글로 옮기면 어순·동사 결합·명사화가 영어식으로 따라온다. 그래서 **번역과 작문을 분리한다**.

1. 메인 Claude 가 영문 Tavily 결과를 **한국어 사실 카드**로 옮긴다 (번역 전문)
2. Codex (GPT-5.5) 가 한국어 카드만 보고 글을 쓴다 (영문 노출 X)
3. Codex 가 자기 글을 자가 검수한다
4. 검수가 FAIL 이면 Codex 가 1 회 재작성한다

본문 작성·검수는 모두 Codex. 메인 Claude 는 오케스트레이션·번역·카드 메타·X 요약만.

## 사용법

### 가장 빠른 흐름

```bash
/blog                # 주제 탐색 → 사실 카드 변환 → Codex 작성·검수 → 카드 → X 요약
/blog-cards          # HTML 카드 템플릿 이미지 (Playwright 렌더)
```

### 단계별 실행

```bash
/blog-discover          # 13개 소스 (트렌드 + long-tail) 에서 주제 후보 10개
/blog-research          # 검색 + 동적 Q&A (단독 호출 시 초안 작성도 Codex 위임 권장)
/blog-review            # 검수 리포트 (--judge 모드는 /blog 자동 흐름에서 호출)
/blog-cards             # 초안의 ## 이미지 메타 YAML → 카드형 WebP
```

생성된 글은 `posts/YYYY-MM-DD-<슬러그>.md`, 이미지는 `posts/images/<슬러그>/*.webp`. 모두 `.gitignore` 에 포함됨. 워드프레스에 수동 붙여넣기 업로드.

## 사전 준비

- Claude Code (메인 모델 Opus 4.7 권장)
- Codex CLI plugin (`/codex:setup` 으로 설치·인증)
- Python + `uv` (모든 스크립트 실행)
- Tavily API 키 (리서치용, 무료 월 1,000건) → `.env` 에 `TAVILY_API_KEY=tvly-...`
- Playwright Chromium (카드 렌더) → `uv run --with playwright python -m playwright install chromium` 1 회

`.env.example` 참고. 실제 `.env` 는 gitignore.

## 구조

```
auto-blog/
├── CLAUDE.md                     # 블로그 글쓰기 규칙 (단일 정관)
├── AGENTS.md                     # 프로젝트 구조 (AI 용)
├── internal-links.md             # ILJ 키워드 표
├── posts/                        # 생성된 글·이미지 (gitignore)
├── profiles/<name>.yml           # 필자별 프로파일 (커밋 대상)
├── templates/cards/              # /blog-cards 가 쓰는 HTML 템플릿 15개
│   ├── thumbnail.html / -bold / -stat / -quote / -magazine
│   ├── section-hero / -simple / -numbered / -timeline
│   ├── section-split / -stat-grid / -compare / -callout
│   └── section-terminal / -flow
├── scripts/
│   ├── discover-topics.py       # /blog-discover (13 소스 트렌드 + long-tail)
│   ├── tavily-search.py         # /blog-research (세션별 ≤8 회 하드 상한)
│   └── render-cards.py          # /blog-cards (Playwright + Jinja2)
└── .claude/skills/
    ├── blog/                     # 메인 파이프라인 (Codex 작성·검수)
    ├── blog-discover/            # 13 소스 → 주제 후보 10 개
    ├── blog-research/            # 검색 + Q&A (단독 호출 가능)
    ├── blog-review/              # 검수 (--judge JSON 리포트)
    └── blog-cards/               # 카드 템플릿 이미지
```

## 글쓰기 규칙

`CLAUDE.md` 가 단일 정관. 다음 핵심 원칙에서 출발:

1. 결론 먼저
2. 짧게 (한 문장 40 자, 한 단락 2~4 문장)
3. 능동형
4. 한 문장 한 가지 내용
5. 추상 주장은 숫자·예시·코드·상황으로 받침

자세한 룰 (대체 표현 표·번역투 회피·도입부 형식·제목·SEO·카드 작성 원칙) 은 CLAUDE.md 참조.
