---
name: blog
description: 주제 탐색(또는 직접 입력) → 초안 작성 → 자동 검수 루프 (Claude N회 + Codex sign-off) → 카드 메타 → 카드 이미지
argument-hint: "[주제] [--profile <name>]"
---

블로그 파이프라인. 주제 탐색 → 제목+초안 한 번에 작성 → **자동 검수 루프** (사람 개입 없이 Claude 검수 sub-agent N회 + Codex 외부 sign-off) → 카드 생성 순서.

> **권장 모델:** Opus 4.7. 자동 루프라 사람 개입이 없고 품질이 우선이다. 검수·재작성 반복이 많으므로 Opus 권장.

## 사용법

```
/blog                              # 주제 탐색부터 시작
/blog uv 패키지 매니저              # 주제 직접 지정
/blog --profile hmkim
/blog uv --profile hmkim
```

## 실행 흐름

### 1단계: 초안 생성 (blog-research 위임)

`blog-research` 스킬의 전체 흐름을 그대로 수행한다:

1. CLAUDE.md 규칙 및 `blog-research` SKILL.md 규칙을 적용
2. **주제 탐색** (`scripts/discover-topics.py` → 후보 10개 → 사용자 선택) → 주제 확정
3. **핵심 키워드·슬러그 결정** (0.5단계) — 한국 검색 트렌드 기준 후보 3~5개 추천 → 사용자 선택 → 한글 슬러그 생성 → 파일명 확정. 이 키워드는 H1·도입부·썸네일 alt 에 동일 형태로 들어간다.
4. 세션 ID 생성 → 프로파일 로드 → AI 쿼리 제안 → 사용자 승인 → Tavily 검색 (≤6 쿼리)
5. 심화 키워드 1~2회 (선택, 총 Tavily 호출 ≤8)
6. **검색 맞춤 Q&A** 를 한 번에 출력하고 사용자 답변 대기
7. `posts/YYYY-MM-DD-<핵심 키워드 슬러그>.md` 에 초안 + 인라인 출처 작성. **`## 이미지 메타` 블록은 이 단계에서 생성하지 않는다** — H3 피드백 완료 후 4단계에서 만든다.

### 2단계: 제목 + 초안 작성 → 자동 검수 루프 (사람 개입 없음)

1단계에서 받은 주제·키워드·Q&A·Tavily 결과를 토대로 **제목 + 본문 + ILJ 마커 + 인라인 출처까지 한 번에** 작성하고, 검수 sub-agent 루프로 자동 다듬는다.

#### 2-A. 작성자 호출 — Codex sub-agent (Pass 0)

본문 작성은 `Agent` 툴로 `codex:codex-rescue` sub-agent 에게 위임한다. Claude 의 한국어 작문이 직번역체 한계가 있어 Codex (GPT-5.5) 의 자연 한국어를 활용한다 (회귀 테스트에서 검증됨, 2026-05-14).

호출 시 메인 LLM (Claude) 이 1단계에서 받은 컨텍스트(Q&A 답변, Tavily 결과, 핵심 키워드·슬러그) 를 정리해 프롬프트에 박는다. 프롬프트 골격:

```
너는 한국어 블로그 작성자다. 다음 컨텍스트로 새 글을 작성해 파일에 직접 저장해라.

## 기준 문서 (cat 으로 먼저 다 읽어라)
- /Users/hmkim/Desktop/workspace/Git/auto-blog/CLAUDE.md
- /Users/hmkim/Desktop/workspace/Git/auto-blog/.claude/skills/blog-research/SKILL.md
- /Users/hmkim/.claude/projects/-Users-hmkim-Desktop-workspace-Git-auto-blog/memory/feedback_blog_natural_korean.md
- /Users/hmkim/.claude/projects/-Users-hmkim-Desktop-workspace-Git-auto-blog/memory/feedback_blog_korean_drafting.md
- /Users/hmkim/.claude/projects/-Users-hmkim-Desktop-workspace-Git-auto-blog/memory/feedback_blog_lowbrow_words.md
- /Users/hmkim/Desktop/workspace/Git/auto-blog/internal-links.md

## 글 정보
- 주제: <주제>
- 핵심 키워드 (H1·도입·alt 일관): <0.5단계 키워드>
- 파일 경로: posts/YYYY-MM-DD-<슬러그>.md
- 사용자 답변 (Q&A 카테고리별):
<Q&A 답변 정리>
- Tavily 검색 결과 (사실·수치·인용 출처):
<제목 — 핵심 한 줄 — URL 형식 목록>

## 작성 규칙
- CLAUDE.md `## 글 구조` / `## 도입부` / `## SEO` / `## 가독성` / `## 톤 가드` / `## 영어 용어 표기` 모두 적용
- 메모리 [feedback_blog_natural_korean] · [feedback_blog_korean_drafting] · [feedback_blog_lowbrow_words] 룰 능동 회피 (영어 직번역 / 구어 / 어색한 명사·동사 결합)
- 인라인 출처 `(출처: URL)` — CLAUDE.md `## 검색 결과 인용 규칙` (a)(b)(c) 케이스만
- internal-links.md 매칭 키워드 본문 첫 등장 자리에 `<!--ILJ-->` 마커
- `## 태그`, `## 인터럴 링크` 섹션 포함 (들어오는 링크 2개)
- `## 이미지 메타` 블록은 **제외** (3단계 카드 메타에서 자동 생성)
- 길이: 3,150~3,850자 (CLAUDE.md `## 분량` 룰)
- 본문 H2 직후에 `![alt](images/<슬러그>/section-N.webp)` 이미지 마커 박아 둔다 (마무리 H2 제외). H1 바로 아래에 thumb 마커.

## 자가 점검 (저장 전 통과)
1. "자리" / "굴려 보다" / "압축" / "결합 효과" / "한도에 닿다" / "강점이 있다" / "정가 옆에 우회로" 류 직번역체가 본문에 없는가?
2. 사용자 답변의 사실이 그대로 반영됐는가? (윤색·각색 X)
3. 인라인 출처·ILJ 마커·이미지 마커 다 들어갔는가?

다 통과해야 저장. 저장 후 "저장 완료" 만 출력.
```

저장 후 사용자에게는 "초안 작성 완료 (Codex), 자동 검수 루프 시작" 만 알린다. 본문 텍스트 출력하지 않는다.

#### 2-B. 검수 sub-agent 호출 — Pass 0 강제 reject

`Agent` 툴로 `general-purpose` sub-agent 를 호출해 `blog-review --judge` 결과를 받는다. 프롬프트 골격:

```
이 블로그 초안을 blog-review SKILL.md `--judge` 모드 규칙으로 검수해라.
파일: posts/YYYY-MM-DD-<슬러그>.md
CLAUDE.md · blog-review/SKILL.md 룰을 모두 적용한다.

**단계 컨텍스트 — SKIP 항목**: 본문 자동 루프 단계라 다음 결정론은 평가에서 SKIP (3단계 카드 메타에서 자동 처리됨):
- 9-c 썸네일 마커 부재
- 10-c 이미지 alt 부재 / 자리채우기 / 중복
- `## 이미지 메타` YAML 블록 부재
- 추가 체크 SEO_4자리_일관 의 썸네일 alt 자리도 미평가

출력은 SKILL.md 에 정의된 JSON 포맷 (score, verdict, axes, 결정론_위반, LLM_지적, 추가_체크).
```

**Pass 0 강제 reject 룰**: 검수 sub-agent 가 95+ 를 줘도 호출자(이 스킬)는 **무조건 reject 로 취급**. 모델이 자기 검수 우회를 못 하게 첫 패스는 항상 재작성 강제.

이 강제 reject 의 출력은 검수 sub-agent 의 JSON 그대로 (재작성 시 fail 항목 그대로 반영하기 위해).

#### 2-C. 재작성·재검수 루프 (Pass 1~3)

루프 시작. 한 번에 한 패스:

1. **재작성**: Pass N-1 의 JSON 의 `결정론_위반` + `LLM_지적` + `추가_체크` 항목을 모두 보고 본문을 다시 쓴다 (Edit 으로 파일 갱신). 동일 자리 지적은 자연 한국어 대안으로 치환.
2. **재검수**: 2-B 와 동일하게 `Agent` 로 검수 sub-agent 호출.
3. **판정**:
   - `verdict == "PASS"` (score ≥ 95 + 결정론 0 + 추가 체크 모두 OK) → 루프 종료, 2-D 로
   - Pass 3 까지 도달했는데도 FAIL → 마지막 상태로 진행 + 사용자에게 "3회 안에 95점 도달 못 함, 마지막 점수 N/100 으로 진행" 알림 + 2-D 로

루프 가드: 같은 fail 항목이 2회 연속 잡히면 재작성 LLM 이 그 자리에 대해 다른 대안을 시도하도록 강조.

#### 2-D. Codex sign-off (Pass Final)

Claude 자가 검수 루프가 끝나면 **Codex 외부 시선**으로 한 번 더 검토. `Agent` 툴로 `codex:codex-rescue` sub-agent 를 호출한다 (Codex plugin 필요, `/codex:setup` 으로 사전 설치·인증).

호출 예:

```
Agent(
  subagent_type="codex:codex-rescue",
  description="Codex sign-off blog review",
  prompt="이 블로그 글을 검수해라.
파일: posts/YYYY-MM-DD-<슬러그>.md
기준 문서를 먼저 cat 으로 읽어라:
- /Users/hmkim/Desktop/workspace/Git/auto-blog/CLAUDE.md
- /Users/hmkim/Desktop/workspace/Git/auto-blog/.claude/skills/blog-review/SKILL.md
큰 결함 (직번역체 / 비문 / 한자어 직역 / 영어식 명사구 / 키워드 강박 / 사실 오류 / 핵심 누락) 위주로 **있는 만큼 다 짚어라** (숫자 제한 없음).
세부 어법 지적은 생략 (그쪽은 Claude 자가 검수에서 이미 잡음). 출력은 항목별 한 줄. 결함 없으면 'OK' 만 출력.

**단계 컨텍스트 — SKIP 항목**: 본문 자동 루프 단계라 다음 결정론은 평가에서 SKIP (3단계 카드 메타 자동 생성에서 처리됨):
- 9-c 썸네일 마커 부재 (H1 바로 아래 ![alt](path))
- 10-c 이미지 alt 부재 / 자리채우기 / 중복
- `## 이미지 메타` YAML 블록 부재
- 본문 H2 직후 section-N 카드 마커 부재
이 자리는 결함으로 보고하지 마라.

**중요 — 검수 시작 전 사용자 메모리 카탈로그를 먼저 cat 으로 읽어 자연 한국어 판단 기준에 박아라** (sub-agent 컨텍스트에 메모리 자동 주입 안 됨):
- /Users/hmkim/.claude/projects/-Users-hmkim-Desktop-workspace-Git-auto-blog/memory/feedback_blog_natural_korean.md
- /Users/hmkim/.claude/projects/-Users-hmkim-Desktop-workspace-Git-auto-blog/memory/feedback_blog_korean_drafting.md
- /Users/hmkim/.claude/projects/-Users-hmkim-Desktop-workspace-Git-auto-blog/memory/feedback_blog_lowbrow_words.md

위 메모리에 직번역 동사·어순·구문 카탈로그 + 한국어 글쓰기 책 기준 판단 룰이 다 적혀 있다.

추가로 글에 다음이 있으면 별도 항목으로 짚어라:
- **사실 확인 의심**: 시점 표지(`2026년`, `현재`) 없는 정책·요금·기능 인용, 또는 출처 URL 이 1년 이상 됐을 가능성 (브런치·블로그·레딧 등 비공식 출처). 어떤 자리가 의심되는지 한 줄 + '재검색 권장' 표기."
)
```

- **Codex 가 OK 또는 사소한 지적만**: 완료. 3단계 (카드 메타) 로.
- **Codex 가 큰 결함 지적**: 한 번 더 재작성 (Claude) → 그대로 종료. **Codex 재호출하지 않음** (비용 통제).
- **Codex plugin 미설치 환경**: `Agent` 호출이 실패하면 sign-off 스킵, 사용자에게 알림.

Codex 의 출력은 항상 사용자에게 표시 (투명성).

#### 2-E. 루프 출력 요약 (사용자에게 보여줄 최종 알림)

```
✅ 자동 검수 루프 완료
파일: posts/YYYY-MM-DD-<슬러그>.md
- Pass 0 (강제 reject)
- Pass 1: 87/100
- Pass 2: 93/100
- Pass 3: 96/100 → PASS
- Codex sign-off: OK (큰 결함 없음)
다음 단계: 카드 메타 생성으로 진행
```

또는 한도 도달 시:

```
⚠ 자동 검수 루프 종료 (3회 한도)
파일: posts/YYYY-MM-DD-<슬러그>.md
- Pass 3 점수 92/100 (95 미달)
- 가장 낮은 축: SEO 첫 단락 14/20
- Codex sign-off: 큰 결함 2건 짚음 → 1회 재작성 적용
마지막 상태로 진행한다.
```

### 3단계: 카드 메타 자동 생성

검수 루프 완료 후 `/blog-research` SKILL.md 13단계 규칙을 따라 `## 이미지 메타` 블록을 자동 생성한다. **사용자 확인 단계 없음** (자동 루프 일관성).

- 팔레트 3색 (글 톤 보고 새로 결정, 직전 글과 겹치지 않게)
- thumb 1개 + section-N (마무리 제외 본문 H2 수만큼, 최대 4개)
- 각 카드 타이틀은 **검수 통과한 본문 H2 내용과 정렬**
- **alt 자동 작성** — 카드별 30~80자 한국어 묘사. thumb alt 에만 0.5단계 핵심 키워드 자연 포함, section-N alt 는 해당 H2 메시지 중심. 카드 간 alt 중복 금지.
- 본문 마크다운 `![alt](path)` 의 alt 자리도 같이 동기화 (Edit 으로 일괄 갱신).

### 4단계: 카드 이미지 생성

```
uv run scripts/render-cards.py posts/<파일>
```

생성 완료 후 파일 경로 안내.

### 5단계: X 아티클 요약 자동 생성 (Claude)

카드 렌더 완료 후, 메인 Claude 가 X(트위터) 아티클 업로드용 후킹 요약본을 1개 생성해 본문 파일 끝에 박는다. Codex 호출 X (시간·비용 통제, 카피라이팅 분량은 Claude 로 충분).

규칙:
- **길이 100~160자** (SEO description 분량)
- **후킹 톤** — 호기심 자극 + 구체 수치·디테일·갈등. 정보 평어체보다 결과·인사이트 한 줄 강조
- **전체 글 핵심 압축** — 잘하는 작업 분기, 의외 발견, 결론 한 줄
- 본문 톤(평서체)과 정렬, 1인칭 후크 1구절 허용
- 메모리 [feedback_blog_natural_korean] 자연 한국어 룰 적용
- 후보 3안 만들지 않음 (자동 흐름이라 1개 확정)

저장 형식 — `## 이미지 메타` 다음 (파일 맨 끝):

```markdown
## X 아티클 요약

<후킹 요약 1줄 또는 2줄>
```

워드프레스 본문에는 들어가지 않는 메타 영역 (`## 태그`, `## 이미지 메타` 와 동일). 사용자가 X 업로드 시 복사해서 쓴다.

## 규칙

- **2단계 자동 루프**: 사용자 개입 없음. 첫 패스는 무조건 reject, 이후 Pass 1~3 중 score ≥ 95 도달 시 통과. 한도 도달 시 마지막 상태로 진행.
- **Codex sign-off**: 루프 통과 후 1회만 호출. 큰 결함 잡으면 Claude 가 1회 재작성하고 종료 (Codex 재호출 X).
- **카드 메타 자동**: 사용자 확인 없이 한 번에 생성·동기화.
- **카드 이미지**: 카드 메타 생성 직후 자동 렌더.
- **`blog-review --fix` 자동 교정**은 사용하지 않는다 (자동 루프가 LLM 재작성으로 처리).
- Tavily 키(`TAVILY_API_KEY`)가 `.env` 에 없으면 1단계에서 중단.

## 에러 대응

- 1단계에서 사용자가 중단하면 2단계로 진행하지 않음
- 2단계 검수 sub-agent 호출 실패 시 1회 재시도, 그래도 실패하면 사용자에게 알림 후 수동 진행
- Codex 호출 실패 시 sign-off 스킵하고 3단계로 진행 + 사용자에게 알림
- 카드 렌더 실패 시 해당 카드만 재시도: `/blog-cards <파일> --only <key>`
