# auto-blog

Claude Code 로 티스토리 블로그 글 초안과 이미지를 자동 생성하는 프로젝트.

## 사용법

### 가장 빠른 흐름

```bash
/blog <주제>        # 초안 생성 + 자동 검수/교정 한 번에
/blog-cards         # HTML 카드 템플릿 이미지 3장 (Playwright 렌더)
# 또는
/blog-images        # AI 일러스트 3장 (Replicate recraft-v3)
```

### 단계별 실행

```bash
/blog-research <주제>   # Tavily 리서치 + 동적 Q&A → 초안 + 이미지 프롬프트 + 이미지 메타
/blog-review            # CLAUDE.md 규칙 자가 검수 (--fix 로 자동 교정)
/blog-cards             # 초안의 ## 이미지 메타 YAML → 카드형 WebP
/blog-images            # 초안의 ## 이미지 프롬프트 → AI 일러스트 WebP
```

생성된 글은 `posts/YYYY-MM-DD-<슬러그>.md`, 이미지는 `posts/images/<슬러그>/*.webp`. 모두 `.gitignore`에 포함됨. 티스토리에는 수동 드래그 업로드.

## 사전 준비

- Claude Code
- Python + `uv` (모든 스크립트 실행)
- Tavily API 키 (리서치용, 무료 월 1,000건) → `.env` 에 `TAVILY_API_KEY=tvly-...`
- (선택) Replicate 계정 + 토큰 (AI 일러스트) → `.env` 에 `REPLICATE_API_TOKEN=r8_...`
- (선택) Playwright Chromium (카드 렌더) → `uv run --with playwright python -m playwright install chromium` 1회

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
│   ├── generate-images.py        # /blog-images 호출 (Replicate)
│   └── render-cards.py           # /blog-cards 호출 (Playwright + Jinja2)
└── .claude/skills/
    ├── blog/                     # 초안+검수 묶음
    ├── blog-research/            # 초안 생성 (현재 주 경로)
    ├── blog-post/                # DEPRECATED 리다이렉트 shim
    ├── blog-review/              # 자가 검수
    ├── blog-images/              # AI 일러스트
    └── blog-cards/               # 카드 템플릿 이미지
```

## 이미지 두 경로 — AI 일러스트 vs 카드 템플릿

초안은 두 종류의 이미지 블록을 마지막에 포함한다.

- `## 이미지 프롬프트` → 영문 프롬프트 3개. `/blog-images` 가 Replicate recraft-v3 로 일러스트 생성.
- `## 이미지 메타` → YAML. 팔레트(포스트당 1개) + 템플릿별 필드. `/blog-cards` 가 HTML 템플릿으로 카드형 이미지 렌더.

둘은 독립적이라 원하는 쪽만 돌려도 된다. 카드 템플릿은 한글·수치가 또렷하게 박히고, AI 일러스트는 분위기 삽화에 가깝다.
