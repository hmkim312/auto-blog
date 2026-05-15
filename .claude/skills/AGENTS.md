<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-22 | Updated: 2026-05-16 -->

# skills

## Purpose
블로그 파이프라인을 구성하는 로컬 스킬 5개. 각 스킬은 단독 실행 가능하며, `posts/` 하위 파일을 통해 서로 상태를 주고받는다. 본문 한국어 작성·검수는 모두 Codex (GPT-5.5) 가 담당하고, 메인 Claude (Opus 4.7) 는 오케스트레이션·영문 → 한국어 번역·메타·X 요약을 맡는다.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `blog/` | `/blog [--profile X]` — 메인 파이프라인. 검색·Q&A → 한국어 사실 카드 변환 → Codex 작성 → Codex 자가 검수 → 카드 메타·렌더 → X 요약 |
| `blog-discover/` | `/blog-discover [--profile X]` — 13 소스 (트렌드 + long-tail) 에서 주제 후보 10 개 추출 (단독 호출용) |
| `blog-research/` | `/blog-research [--profile X]` — 검색 + 동적 Q&A. 단독 호출 시 초안 작성도 Codex 위임 권장 |
| `blog-review/` | `/blog-review [파일] [--judge]` — 검수 리포트. `--judge` 모드는 `/blog` 자동 흐름에서 호출 (JSON 리포트). `--fix` 는 안전 치환 |
| `blog-cards/` | `/blog-cards [파일]` — 초안의 `## 이미지 메타` YAML 블록을 Playwright 로 렌더 → 카드형 WebP |

## 스킬 간 관계

```
blog-discover  (13 소스 → 후보 10 개)              ← 단독 호출 시
   ↓ 사용자 선택
blog-research  (검색 + Q&A)                         ← /blog 의 1단계
   ↓
   메인 Claude: 영문 → 한국어 사실 카드 변환        ← /blog 의 1.5단계 (NEW)
   ↓
   Codex 작성 (한국어 카드만 입력)                  ← /blog 의 2-A
   ↓
   Codex 자가 검수 (JSON)                            ← /blog 의 2-B
   ↓
   Codex 재작성 1 회 (FAIL 시만)                     ← /blog 의 2-C
   ↓ posts/YYYY-MM-DD-slug.md
blog-cards     (카드 템플릿 → WebP)                 ← /blog 의 3~4단계
   ↓ posts/images/<slug>/*.webp
blog-review    (단독 호출 시 검수 리포트, --fix)
```

순서를 강제하지는 않는다. 사용자가 임의 순서로 호출 가능 (예: 초안 수기 수정 → `/blog-cards` 만).

## For AI Agents

### Working In This Directory

- 스킬 파일은 `<name>/SKILL.md` 단일 파일. frontmatter 필수 필드: `name`, `description`, `argument-hint`.
- 스킬 내부에서 코드 실행이 필요하면 `../../scripts/` 의 스크립트를 호출.
- 새 스킬 추가 시 파이프라인의 어느 단계에 들어가는지 먼저 정의한 뒤 설계.
- 본문 작성·검수 자리는 모두 Codex (`codex:codex-rescue` sub-agent). Claude 직접 작성·검수 X.

### Common Patterns

- 모든 스킬이 `../../CLAUDE.md` 의 규칙을 따른다 (글쓰기 핵심 원칙·문체·구조·분량·SEO·카드).
- 입력: `posts/*.md` 경로 또는 최신 파일.
- 출력: `posts/` 하위 파일 생성·수정.
- LLM 호출 시 컨텍스트 사전 주입 — 메인 Claude 가 CLAUDE.md·메모리·ILJ 표를 발췌해 프롬프트에 넣음.

### Testing Requirements

- 스킬 수정 후 샘플 주제로 `/blog` End-to-End 회귀 확인.
- `blog-review` 의 결정론 규칙 (어색 패턴 grep 카탈로그 포함) 변경 시 위반·통과 케이스 최소 1 개씩 확인.

## Dependencies

### Internal
- `../../CLAUDE.md` — 글쓰기 규칙 단일 정관
- `../../scripts/render-cards.py` — `blog-cards` 가 호출
- `../../scripts/tavily-search.py` — `blog-research` 가 호출
- `../../scripts/discover-topics.py` — `blog-discover` / `blog-research` 가 호출
- `../../templates/cards/*.html` — `blog-cards` 가 쓰는 Jinja2 템플릿 15 개
- `../../profiles/<name>.yml` — `blog-research` 가 읽는 필자별 프로파일
- `../../internal-links.md` — `/blog` 가 ILJ 키워드 표로 활용

### External
- `blog-cards`: Playwright + Chromium (`playwright install chromium` 최초 1 회), `uv`
- `blog-research`: Tavily API (무료 월 1,000건), `uv`, `TAVILY_API_KEY`
- `blog`, `blog-research`, `blog-review`: Codex CLI plugin (`/codex:setup` 으로 설치·인증)

<!-- MANUAL: -->
