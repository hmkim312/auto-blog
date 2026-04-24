<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-22 | Updated: 2026-04-22 -->

# scripts

## Purpose
스킬이 호출하는 Python 실행 스크립트. 외부 API 호출이나 파일 후처리처럼 스킬 지시문만으로 처리하기 어려운 로직을 담는다.

## Key Files

| File | Description |
|------|-------------|
| `generate-images.py` | Replicate recraft-v3로 블로그 포스트의 이미지 프롬프트를 실제 이미지(WebP)로 변환. `/blog-images` 스킬이 호출. |
| `tavily-search.py` | Tavily 웹 검색 API 어댑터. `BLOG_RESEARCH_SESSION_ID` 기반 세션 카운터로 호출 ≤8 하드 강제. `--dry-run` fixture 지원. `/blog-research` 스킬이 호출. |
| `fixtures/tavily-dry-run.json` | `tavily-search.py --dry-run` 이 반환하는 고정 응답. 네트워크 없이 파이프라인 스모크 테스트용. |

## For AI Agents

### Working In This Directory
- 모든 Python 스크립트는 **PEP 723 인라인 의존성**을 `# /// script` 블록에 선언한다. `requirements.txt`/`pyproject.toml` 만들지 말 것.
- 실행은 `uv run scripts/<파일>.py`. 셰뱅은 `#!/usr/bin/env -S uv run --script`.
- 환경변수는 프로젝트 루트 `.env`에서 `python-dotenv`로 로드 (gitignore 되어 있음).
- 출력 경로는 항상 프로젝트 루트 기준(`posts/` / `posts/images/`)으로 고정.

### Testing Requirements
- 새 스크립트 추가 후 `python3 -c "import ast; ast.parse(open(...).read())"` 로 최소 구문 검증.
- Replicate 등 유료 API 호출 전, 파싱/전처리 단계를 API 없이 단독 실행 가능하도록 분리해 테스트.

### Common Patterns
- 인자 파서: `argparse` (표준 라이브러리).
- 에러 시 `sys.exit(f"[error] ...")` 로 명확히 종료.
- 진행 상황은 짧은 한 줄 로그로 출력 (사용자가 터미널에서 본다).

## Dependencies

### Internal
- 프로젝트 루트 `.env` (API 토큰)
- `posts/` 디렉토리 구조에 의존
- `.omc/state/tavily-budget.json` (`tavily-search.py` 가 자동 생성/갱신. 런타임 상태, gitignore)

### External
- `uv` (필수 실행기)
- `replicate`, `python-dotenv`, `requests` — `generate-images.py` 의존
- `requests`, `python-dotenv` — `tavily-search.py` 의존 (Tavily SDK 없이 HTTP 직접 호출)

<!-- MANUAL: -->
