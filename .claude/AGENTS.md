<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-22 | Updated: 2026-04-22 -->

# .claude

## Purpose
Claude Code 프로젝트 설정 루트. 프로젝트 로컬 스킬과 슬래시 커맨드가 여기에 위치한다. Claude Code가 세션 시작 시 자동으로 인식.

## Key Files
(해당 디렉토리 직속 파일 없음)

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `skills/` | 블로그 파이프라인을 구성하는 3개 스킬 정의 (see `skills/AGENTS.md`) |
| `commands/` | 슬래시 커맨드 (현재 비어 있음) |

## For AI Agents

### Working In This Directory
- 새 스킬 추가 시 `skills/<name>/SKILL.md` 형식 준수 (frontmatter `name`/`description`/`argument-hint`).
- `commands/`는 아직 사용 안 함. 필요해지면 `<name>.md`에 지시문 작성.

### Common Patterns
- 스킬 한 개 = 한 디렉토리 = 한 `SKILL.md`. 스킬 간 공유 코드는 프로젝트 루트 `scripts/` 로 뺀다.

## Dependencies

### Internal
- `../CLAUDE.md` — 스킬들이 참조하는 글쓰기 규칙
- `../scripts/` — 스킬이 호출하는 실행 스크립트

<!-- MANUAL: -->
