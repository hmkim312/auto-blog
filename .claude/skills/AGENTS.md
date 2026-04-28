<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-22 | Updated: 2026-04-25 -->

# skills

## Purpose
블로그 파이프라인을 구성하는 로컬 스킬들. 각 스킬은 독립 실행 가능하며, `posts/` 하위 파일을 통해 서로 상태를 주고받는다.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `blog/` | `/blog [--profile X]` — 주제 탐색+리서치+초안+자동 검수/교정까지 묶은 메타 스킬 (카드 이미지는 수동) |
| `blog-discover/` | `/blog-discover [--profile X]` — 8개 트렌드 소스에서 주제 후보 10개를 제목만 추려준다 (단독 호출용) |
| `blog-research/` | `/blog-research [--profile X]` — 주제 탐색 + Tavily 웹 검색 + 동적 Q&A + 초안 + **이미지 메타 블록** 생성 (주 경로) |
| `blog-review/` | `/blog-review [파일]` — CLAUDE.md 규칙 자가 검수, `--fix` 플래그로 안전 치환 |
| `blog-cards/` | `/blog-cards [파일]` — 초안의 `## 이미지 메타` YAML 블록을 HTML 템플릿으로 Playwright 렌더 → 카드형 WebP 생성 |

## 스킬 간 관계

```
blog-discover  (13 소스 → 후보 10개 제목)       ← 단독 호출 시
   ↓ 사용자 선택
blog-research  (주제 탐색 내장 + Tavily + Q&A → 본문 + 이미지 메타)
   ↓ posts/YYYY-MM-DD-slug.md
blog-review    (규칙 검수 + 교정)
   ↓ 같은 파일 수정
blog-cards     (카드 템플릿)
   → posts/images/<slug>/*.webp
```

순서를 강제하지는 않는다. 사용자가 임의 순서로 호출 가능 (예: 초안 수기 수정 → 카드만).

## For AI Agents

### Working In This Directory
- 스킬 파일은 `<name>/SKILL.md` 단일 파일. frontmatter 필수 필드: `name`, `description`, `argument-hint`.
- 스킬 내부에서 실제 코드 실행이 필요하면 `../../scripts/` 의 스크립트를 호출.
- 새 스킬 추가 시 **파이프라인의 어느 단계에 들어가는지**를 먼저 정의한 뒤 설계.

### Common Patterns
- 모든 스킬이 `../CLAUDE.md`의 규칙을 따른다 (문체, 구조, 분량, 파일명).
- 입력: `posts/*.md` 경로 또는 최신 파일.
- 출력: `posts/` 하위 파일 생성·수정.

### Testing Requirements
- 스킬 수정 후 샘플 주제로 End-to-End 흐름을 한 번 돌려 회귀 확인.
- `blog-review` 의 결정론 규칙은 정규식이므로 변경 시 위반/통과 케이스 최소 1개씩 확인.

## Dependencies

### Internal
- `../../CLAUDE.md` — 글쓰기 규칙의 기준
- `../../scripts/render-cards.py` — `blog-cards`가 호출
- `../../scripts/tavily-search.py` — `blog-research`가 호출
- `../../scripts/discover-topics.py` — `blog-discover` / `blog-research` 가 호출
- `../../templates/cards/*.html` — `blog-cards`가 사용하는 Jinja2 템플릿
- `../../profiles/<name>.yml` — `blog-research` 가 읽는 필자별 프로파일

### External
- `blog-cards`: Playwright + Chromium (`playwright install chromium` 최초 1회), `uv`
- `blog-research`: Tavily API(무료 월 1,000건), `uv`, `TAVILY_API_KEY`

<!-- MANUAL: -->
