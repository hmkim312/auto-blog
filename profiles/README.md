# profiles

블로그 필자별 컨셉·톤·검색 취향을 담는 프로파일 파일. `/blog-research` 스킬이 실행 시 `--profile <name>` 인자로 지정된 파일을 읽어 쿼리 제안·초안 작성에 반영한다.

여러 명이 같은 리포를 공유할 수 있게 **공유 포맷(D형)** 으로 설계됐다. 실제 실행·글 저장은 각자 로컬에서 이루어진다.

## 사용

```
/blog-research uv 패키지 매니저 --profile hmkim
```

`--profile` 생략 시 기본값으로 동작한다 (CLAUDE.md의 `개발 입문자 6개월~1년` 기준).

## 스키마

### 필수 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | str | 프로파일 식별자. 파일명(`<name>.yml`)과 일치시킬 것 |
| `niche` | str | 블로그 니치 한 줄 요약 |
| `reader_level` | str | 대상 독자 레벨 (예: `개발 입문자 (6개월~1년)`) |

### 선택 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `persona` | str (multiline) | 1인칭 자유 서술. 초안의 "경험" 섹션 톤에 반영 |
| `tone` | str | 문체 힌트. 기본은 CLAUDE.md 규칙 |
| `publish_rhythm` | str | 발행 주기 메모 (시스템이 강제하지 않음, 메모용) |
| `preferred_topics` | list[str] | 자주 다루는 키워드 |
| `avoid_topics` | list[str] | 피할 주제 |
| `search_bias.region` | str | Tavily 검색 지역 힌트 (예: `KR`) |
| `search_bias.language` | str | Tavily 검색 언어 힌트 (예: `ko`) |
| `search_bias.recency_days` | int | 최신성 바이어스 메모. v1 에서는 LLM 이 쿼리 작성 시 참고 |

## 샘플

- [`hmkim.yml`](hmkim.yml) — AI 트렌드/기술 설명 하이브리드 프로파일
- [`wife.yml`](wife.yml) — 컨셉 미정 플레이스홀더

## 새 프로파일 만들기

1. `profiles/<이름>.yml` 생성
2. 최소 `name`, `niche`, `reader_level` 3개 필드 채움
3. 필요 시 `persona`/`tone`/`search_bias` 추가
4. `/blog-research <주제> --profile <이름>` 으로 실행
