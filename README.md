# auto-blog

Claude Code 로 티스토리 블로그 글 초안과 이미지를 자동 생성하는 프로젝트.

## 사용법

### 가장 빠른 흐름

```bash
/blog                # 주제 탐색 → 초안 생성 → 자동 검수/교정 한 번에
/blog-cards          # HTML 카드 템플릿 이미지 (Playwright 렌더, 본문 H2 수에 맞춰 동적, 캡 5장)
```

### 단계별 실행

```bash
/blog-discover          # 8개 트렌드 소스에서 주제 후보 10개 제목만
/blog-research          # 주제 탐색 내장 + Tavily 리서치 + 동적 Q&A → 초안 + 이미지 메타
/blog-review            # CLAUDE.md 규칙 자가 검수 (--fix 로 자동 교정)
/blog-cards             # 초안의 ## 이미지 메타 YAML → 카드형 WebP
```

생성된 글은 `posts/YYYY-MM-DD-<슬러그>.md`, 이미지는 `posts/images/<슬러그>/*.webp`. 모두 `.gitignore`에 포함됨. 티스토리에는 수동 드래그 업로드.

## 사전 준비

- Claude Code
- Python + `uv` (모든 스크립트 실행)
- Tavily API 키 (리서치용, 무료 월 1,000건) → `.env` 에 `TAVILY_API_KEY=tvly-...`
- Playwright Chromium (카드 렌더) → `uv run --with playwright python -m playwright install chromium` 1회

`.env.example` 참고. 실제 `.env` 는 gitignore.

## 구조

```
auto-blog/
├── CLAUDE.md                     # 블로그 글쓰기 규칙 (진리의 원천)
├── AGENTS.md                     # 프로젝트 구조/컨벤션 (AI용)
├── posts/                        # 생성된 글·이미지 (gitignore)
├── profiles/<name>.yml           # 필자별 프로파일 (커밋 대상)
├── templates/cards/              # /blog-cards 가 쓰는 HTML 템플릿
│   ├── thumbnail.html            # 썸네일 비대칭 분할
│   ├── section-hero.html         # 넘버링 + 행형 카드
│   ├── section-simple.html       # 풀쿼트
│   ├── section-numbered.html     # 큰 숫자 + 항목 나열
│   ├── section-split.html        # 수치 + 맥락 2분할
│   └── section-compare.html      # A vs B 2컬럼
├── scripts/
│   ├── tavily-search.py          # /blog-research 호출 (세션별 ≤8회 하드 상한)
│   └── render-cards.py           # /blog-cards 호출 (Playwright + Jinja2)
└── .claude/skills/
    ├── blog/                     # 주제 탐색+초안+검수 묶음
    ├── blog-discover/            # 트렌드 소스 → 주제 후보 10개
    ├── blog-research/            # 초안 생성 (주 경로, 주제 탐색 내장)
    ├── blog-review/              # 자가 검수
    └── blog-cards/               # 카드 템플릿 이미지
```

## 이미지 — 카드 템플릿

초안 끝의 `## 이미지 메타` YAML 블록(팔레트 + 템플릿별 필드)을 `/blog-cards` 가 HTML 템플릿으로 렌더해 카드형 WebP 를 만든다. 한글·수치가 또렷하게 들어간다.
