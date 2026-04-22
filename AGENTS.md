<!-- Generated: 2026-04-22 | Updated: 2026-04-22 -->

# auto-blog

## Purpose
Claude Code 기반 티스토리 블로그 글 자동 생성 파이프라인. 주제 입력 → 질의응답 → 마크다운 초안 → 자가 검수 → 이미지 생성까지 3개 스킬로 연결된다. 생성물은 `posts/` 하위에 저장되며 티스토리 업로드는 수동(드래그앤드롭).

## Key Files

| File | Description |
|------|-------------|
| `CLAUDE.md` | 블로그 글쓰기 규칙 (문체, 구조, 분량, 파일명). 모든 스킬의 기준 문서. |
| `README.md` | 사용자용 프로젝트 소개와 기본 사용법 |
| `.env.example` | `REPLICATE_API_TOKEN` 환경변수 예시. 실제 `.env`는 gitignore. |
| `.gitignore` | `posts/`, `.omc/`, `.env` 제외 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `.claude/` | 스킬·커맨드 정의 (see `.claude/AGENTS.md`) |
| `scripts/` | 실행 스크립트 (see `scripts/AGENTS.md`) |
| `posts/` | 생성된 글 저장소 (gitignore, 런타임 산출물) |

## 전체 파이프라인

```
/blog <주제>        →  초안 생성 + 자동 검수/교정 한 번에 (권장)
/blog-images        →  posts/images/<slug>/ 에 이미지 3장씩 생성 (수동 호출)

# 단계별 실행도 가능
/blog-post <주제>   →  posts/YYYY-MM-DD-slug.md 초안 생성 (9문 Q&A)
/blog-review        →  CLAUDE.md 규칙으로 검수 (--fix 옵션)
/blog-images        →  posts/images/<slug>/ 에 이미지 3장씩 생성
```

## For AI Agents

### Working In This Directory
- **CLAUDE.md는 블로그 글쓰기 규칙의 유일한 진리 원천**이다. 규칙 변경 시 반드시 CLAUDE.md를 먼저 고친 뒤 스킬/스크립트를 맞춰 수정한다.
- 블로그 문체는 평서체(~했다, ~이다, ~한다). 대화/문서 문체와 혼동하지 말 것.
- 티스토리 Open API는 2024년 신규 발급 중단 → 업로드 자동화는 설계하지 않는다.
- 생성된 이미지는 `posts/images/` 에 들어가며 gitignore된다.

### Testing Requirements
- 파이썬 스크립트는 `uv run scripts/<파일>.py` 로 실행 (PEP 723 인라인 deps 사용).
- 스킬 변경 후에는 `/blog-post`, `/blog-review`, `/blog-images` 흐름이 실제로 돌아가는지 샘플 글 하나로 확인한다.

### Common Patterns
- 마크다운 기반, 단순한 파이프라인. 데이터베이스·웹 서버 없음.
- 각 스킬은 독립적으로 호출 가능하고 상태를 파일(`posts/*.md`, `posts/images/*`)로만 주고받는다.

## Dependencies

### Internal
없음 (단일 모듈 프로젝트)

### External
- `uv` (Python 의존성/실행)
- `replicate` (recraft-v3 API)
- `python-dotenv`, `requests` (보조 라이브러리)
- Replicate 계정/API 토큰 (이미지 생성 시 필요)

<!-- MANUAL: -->
