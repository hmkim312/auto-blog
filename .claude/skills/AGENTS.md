<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-22 | Updated: 2026-04-22 -->

# skills

## Purpose
블로그 파이프라인을 구성하는 로컬 스킬 3개. 각 스킬은 독립 실행 가능하며, `posts/` 하위 파일을 통해 서로 상태를 주고받는다.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `blog-post/` | `/blog-post <주제>` — 9문 질의응답으로 마크다운 초안 생성 |
| `blog-review/` | `/blog-review [파일]` — CLAUDE.md 규칙 자가 검수, `--fix` 플래그로 안전 치환 |
| `blog-images/` | `/blog-images [파일]` — 초안의 이미지 프롬프트로 Replicate Flux schnell 호출 |

## 스킬 간 관계

```
blog-post      (초안 생성)
   ↓ posts/YYYY-MM-DD-slug.md
blog-review    (검수 + 교정)
   ↓ 같은 파일 수정
blog-images    (이미지 생성)
   → posts/images/<slug>/*.webp
```

순서를 강제하지는 않는다. 사용자가 임의 순서로 호출 가능 (예: 초안 수기 수정 → 이미지만).

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
- `../../scripts/generate-images.py` — `blog-images`가 호출

### External
- `blog-images`만 외부 의존: Replicate API, `uv`, `REPLICATE_API_TOKEN`

<!-- MANUAL: -->
