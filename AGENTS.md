<!-- Generated: 2026-04-22 | Updated: 2026-05-16 -->

# auto-blog

## Purpose
Claude Code 기반 워드프레스 블로그 글 자동 생성 파이프라인. 영문 자료를 한국어 글로 옮길 때 발생하는 직번역체를 차단하기 위해 **번역과 작문을 분리한다** — 메인 Claude 가 한국어 사실 카드로 번역하고, Codex (GPT-5.5) 가 한국어 카드만 보고 작문·자가 검수한다. 필자별 컨셉은 `profiles/<name>.yml` 로 공유 포맷 관리. 생성물은 `posts/` 하위에 저장되며 워드프레스 업로드는 수동 (블록 에디터 붙여넣기).

## Key Files

| File | Description |
|------|-------------|
| `CLAUDE.md` | 블로그 글쓰기 규칙 단일 정관 (글쓰기 핵심 원칙·한국어 사실 카드 절차·대체 표현 표·번역투 회피·도입부·제목·SEO·카드 작성 원칙). |
| `README.md` | 사용자용 프로젝트 소개와 기본 사용법. |
| `internal-links.md` | Internal Link Juicer 키워드 표 (글 간 자동 연결 키워드). |
| `.env.example` | `TAVILY_API_KEY` 환경변수 예시. 실제 `.env` 는 gitignore. |
| `.gitignore` | `posts/`, `.omc/`, `.env` 제외. |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `.claude/` | 스킬·커맨드 정의 (see `.claude/AGENTS.md`) |
| `scripts/` | 실행 스크립트 (see `scripts/AGENTS.md`) |
| `templates/cards/` | `/blog-cards` 가 사용하는 HTML 카드 템플릿 15 개 (Jinja2, Pretendard, 1200x630) |
| `profiles/` | 필자별 프로파일 YAML (공유 포맷, 커밋 대상) |
| `posts/` | 생성된 글·이미지 저장소 (gitignore, 런타임 산출물) |

## 전체 파이프라인

```
/blog [--profile X]
  1. 주제 탐색·키워드·검색·Q&A         (메인 Claude, blog-research 위임)
  1.5 영문 → 한국어 사실 카드 변환      (메인 Claude, NEW)
  2. Codex 작성 (한국어 카드만 입력)    (Codex sub-agent)
  3. Codex 자가 검수 (JSON 리포트)      (Codex sub-agent)
  4. Codex 재작성 1 회 (FAIL 시만)      (Codex sub-agent)
  5. 카드 메타 자동 생성·렌더·X 요약    (메인 Claude)

# 단계별 단독 실행도 가능
/blog-discover [--profile X]   →  13 소스 (트렌드 + long-tail) 에서 주제 후보 10 개
/blog-research [--profile X]   →  검색 + 동적 Q&A (단독 호출 시 초안 작성도 Codex 위임 권장)
/blog-review [파일] [--judge]  →  검수 (--judge 모드는 /blog 자동 흐름에서 호출)
/blog-cards [파일]             →  초안의 `## 이미지 메타` 블록 → 카드형 WebP
```

### 모델 분리 원칙

| 역할 | 모델 |
|------|------|
| 메인 오케스트레이션·번역·카드 메타·X 요약 | Opus 4.7 |
| 본문 한국어 작성 | Codex (GPT-5.5) |
| 본문 검수 | Codex (GPT-5.5) |
| 점수화·메타 작성 | Opus 4.7 |

Claude 의 한국어 본문 작성·검수는 직번역체·어색 결합 한계가 회귀 검증에서 두 번 확인됐다 (2026-05-14, 2026-05-15). 그래서 본문 자리는 모두 Codex.

### Tavily 예산 가드

`scripts/tavily-search.py` 는 `BLOG_RESEARCH_SESSION_ID` 세션 단위로 호출을 세고 기본 8 회 상한을 넘으면 exit 4 로 강제 차단한다. 상태는 `.omc/state/tavily-budget.json`.

## For AI Agents

### Working In This Directory

- **CLAUDE.md 가 글쓰기 규칙의 단일 정관**. 규칙 변경 시 CLAUDE.md 를 먼저 고친 뒤 스킬·스크립트를 맞춰 수정한다.
- 블로그 본문 한국어는 Codex 가 쓴다. Claude 가 직접 본문을 쓰거나 검수하지 않는다 (메모리 [[blog-writer-model]] 참조).
- 영문 Tavily 결과를 Codex 에게 그대로 넘기지 않는다. 메인 Claude 가 한국어 사실 카드로 변환한 뒤에만 Codex 가 본다.
- 블로그 문체는 평서체 (~ 한다, ~ 된다, ~ 이다). 대화체와 혼동하지 말 것.
- 채팅·문서 어디에서도 "자리·박다·잡다·모델 둘레" 같은 직번역·구어 단어 회피 (CLAUDE.md `## 자연스러운 대체 표현` 표).
- 워드프레스 업로드는 수동. REST API 자동화는 현재 범위 밖.
- 생성된 이미지는 `posts/images/` 에 들어가며 gitignore.

### Testing Requirements

- 파이썬 스크립트는 `uv run scripts/<파일>.py` 로 실행 (PEP 723 인라인 deps).
- 스킬 변경 후에는 샘플 글 하나로 전체 흐름 (`/blog`) 이 돌아가는지 확인한다.
- Tavily 실제 호출 전에는 `scripts/tavily-search.py --dry-run` 으로 smoke test.
- `/blog-cards` 최초 1 회: `uv run --with playwright python -m playwright install chromium`.
- Codex 호출은 `Agent` 툴로 `codex:codex-rescue` sub-agent 위임. 사전 `/codex:setup` 필요.

### Common Patterns

- 마크다운 기반, 단순한 파이프라인. 데이터베이스·웹 서버 없음.
- 각 스킬은 단독 호출 가능하고 상태를 파일 (`posts/*.md`, `posts/images/*`) 로만 주고받는다.
- 모든 LLM 호출 (Codex 작성·검수) 은 컨텍스트 사전 주입 — 메인 Claude 가 CLAUDE.md·메모리·ILJ 표·한국어 사실 카드를 발췌해 프롬프트에 넣음. Codex 가 cat 호출로 기준 문서 다시 읽지 않게 해 시간 단축.

## Dependencies

### Internal
없음 (단일 모듈 프로젝트)

### External
- `uv` (Python 의존성·실행)
- `tavily` (웹 검색 — HTTP 직접 호출, SDK 없음)
- `playwright` + Chromium (`/blog-cards`), `jinja2`, `pyyaml`, `pillow`
- `python-dotenv`, `requests`
- Tavily API 키 (무료 월 1,000건)
- Codex CLI plugin (`/codex:setup` 으로 설치·인증)

<!-- MANUAL: -->
