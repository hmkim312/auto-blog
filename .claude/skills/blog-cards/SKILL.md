---
name: blog-cards
description: 초안 끝의 `## 이미지 메타` YAML 블록을 HTML 템플릿으로 렌더해 posts/images/<slug>/*.webp 카드 생성
argument-hint: "[파일] [--only <이름>]"
---

블로그 초안의 YAML 메타를 Playwright 헤드리스로 렌더해 카드형 WebP (1200x630) 를 만든다. 카드 콘텐츠 작성 원칙은 CLAUDE.md `## 15. 카드 콘텐츠`. 이 파일은 양식·필드·팔레트 명세 단일 출처.

권장 모델: Opus 4.7.

## 사용법

```
/blog-cards                              # posts/ 최신 파일
/blog-cards posts/2026-04-25-x.md        # 특정 파일
/blog-cards --only thumb                 # 특정 블록만
```

## 최초 1 회 준비

```
uv run --with playwright python -m playwright install chromium
```

## 초안 메타 블록 형식

초안 끝 (`## 태그` 다음) 에 둔다. **구체값 (hex·문구) 은 매번 글에 맞게**.

```yaml
## 이미지 메타

palette:
  base: "#<글 톤에 맞는 어두운 hex>"
  accent: "#<감정·강조 색>"
  highlight: "#<base 위에서 떠 보이는 밝은 색>"

thumb:
  template: <thumbnail|thumbnail-bold|thumbnail-stat|thumbnail-quote|thumbnail-magazine>
  alt: "..."
  # 템플릿별 필드는 아래 카탈로그

section-1:
  template: <section-* 중 하나>
  alt: "..."

section-2:
  ...
```

블록 이름 (`thumb`, `section-1` ~ `section-N`) 이 출력 파일명 (`posts/images/<slug>/<key>.webp`). 본문 H2 수에 맞춰 동적 (마무리 H2 제외).

## H2 메시지 → 슬롯 매핑

CLAUDE.md `## 15. 카드 콘텐츠` 원칙대로. 본문 H2 마다 한 번에 한 H2 씩:

1. 그 섹션이 전하는 메시지를 한 문장으로 적는다.
2. 그 문장과 아래 카탈로그 "잘 맞는 H2 메시지 형태" 표를 보고 양식 1 개 선택. 양식이 메시지와 안 맞으면 양식을 바꾼다.
3. 양식 슬롯에 메시지 본질 (동사·명사·수치) 직접 적기. 자리채움 X.

thumb 는 H1 + 도입 정의 한 줄로 같은 절차 별도 수행.

## 배경 톤 (글 단위 통일)

한 글의 카드 배경은 모두 같은 그룹. 다크면 다 다크, 라이트면 다 라이트, 컬러풀이면 다 컬러풀. 시각 변주는 같은 그룹 안에서 레이아웃·폰트·아이콘으로.

| 그룹 | 템플릿 |
|------|--------|
| 다크 | `thumbnail`, `thumbnail-stat`, `section-hero`, `section-numbered`, `section-timeline`, `section-stat-grid` |
| 컬러풀 | `thumbnail-bold`, `section-callout` |
| 라이트 | `thumbnail-quote`, `section-simple`, `section-flow` |
| 스플릿 | `thumbnail-magazine`, `section-split`, `section-compare` |
| 코드 | `section-terminal` |

## 카탈로그

### 썸네일 5 종

| 템플릿 | 잘 맞는 H2 메시지 | 필드 |
|--------|------------------|------|
| `thumbnail` | 일반·정보형 | `kicker`, `icon`, `title`, `subtitle`, `badges[]` |
| `thumbnail-bold` | 임팩트 한 줄, 결론형 | `title`(필수), `subtitle`/`kicker`/`icon`/`badges` |
| `thumbnail-stat` | 핵심이 수치 1 개 | `stat_value`(필수, 짧게), `stat_label`/`stat_unit`/`title`/... |
| `thumbnail-quote` | 회고·감정·1인칭 | `title`(인용문 톤), `subtitle`/`attribution`/`badges` |
| `thumbnail-magazine` | 잡지 표지, 시각 임팩트 | `kicker`, `title`, `label`, `subtitle`, `accent_text`, `meta[]` |

### 섹션 카드 10 종

| 템플릿 | 잘 맞는 H2 메시지 | 필드 |
|--------|------------------|------|
| `section-hero` | H3 가 카드 한 장 분량 N 개 | `num`, `title`, `subtitle`, `cards[{icon,title,desc}]`(1~8), `footer{label,chips[]}` |
| `section-simple` | H3 0~1, 결론 한 문장 | `title`, `subtitle`, `attribution`, `badges[]` |
| `section-numbered` | 순서·원칙·단계 명확 | `kicker`, `title`, `items[{title,desc}]`(3~8) |
| `section-timeline` | 시간·버전·이전→이후 | `kicker`, `title`, `subtitle`, `steps[{marker,title,desc}]` |
| `section-split` | 한 수치가 섹션 중심 | `stat_label`, `stat_value`, `stat_unit`, `title`, `points[]` |
| `section-stat-grid` | 수치 4+ 개 | `kicker`, `title`, `subtitle`, `stats[{value,label,delta}]`(1~8) |
| `section-compare` | H3 정확히 2 개 + 대립 | `title`, `subtitle`, `left{label,title,desc,bullets[],emph}`, `right{...,emph}` |
| `section-callout` | 함정·경고·결론 단일 | `icon`, `tag`, `title`, `subtitle`, `attribution` |
| `section-terminal` | 명령어·코드 핵심 | `kicker`, `title`, `subtitle`, `prompt`, `bar_title`, `commands[{line,type}]` (type: cmd/out/ok/cmt) |
| `section-flow` | 파이프라인·노드 흐름 | `kicker`, `title`, `subtitle`, `nodes[{icon,label,desc,emph}]`, `footer` |

### N 개 동적 처리

CSS `body[data-count="N"]` selector 로 폰트·padding 자동 축소.

| 템플릿 | 동적 범위 |
|--------|----------|
| `section-hero` (cards) | 1~8. 5+ 부터 자동 축소 |
| `section-numbered` (items) | 1~8. 6+ 자동 축소 |
| `section-stat-grid` (stats) | 1~8. grid 형태 자동 (1행/2x2/3x2/4x2) |
| `section-timeline` (steps) | N 개 자유 |
| `section-terminal` (commands) | N 개 자유 |
| `section-flow` (nodes) | N 개 자유 (3~6 권장) |

## 팔레트

- `palette` 는 hex 3 색 (`base`/`accent`/`highlight`). 매 글 직접 정한다 (프리셋 X).
- **포스트 내 단일 팔레트 강제**. 블록별 `palette:` 무시 (스크립트 차단).
- 색 기준:
  - `base` — 어두운 톤 (#0F~#2F 채도). 다크 템플릿 배경.
  - `accent` — 글의 감정 한 색. 임팩트 템플릿 배경, 다크 강조색.
  - `highlight` — base 위에서 떠 보이는 밝은 톤. 라이트 템플릿 배경. 너무 밝거나 (#FFF) 채도 없는 회색 X. 크림·민트·연하늘.
- **직전 글 hex 그대로 가져오지 않는다**. 겹치면 변형.
- 지정 없거나 잘못된 형식이면 fallback `indigo` 프리셋.

## 문구 길이 가이드

- 카드 제목·배지 8~14 자. 더 길면 잘림.
- `badges` 4~6 개 권장.
- `section-compare` 는 `emph: true` 를 결론 쪽에 권장.

## alt 텍스트

CLAUDE.md `## 11 이미지 alt` 룰:
- 카드별 30~80 자 한국어. 자리채움 (`이미지: 썸네일`) X.
- thumb 1 장에만 핵심 키워드 자연 포함. section-N alt 는 해당 H2 메시지 중심.
- 카드 간 같은 alt 두 번 이상 X.
- 본문 마크다운 `![alt](path)` 의 alt 도 YAML 의 alt 와 동일 (12단계 Edit 동기화).

## 실행 흐름

1. 대상 파일 결정 (인자 or 최신)
2. `## 이미지 메타` YAML 파싱
3. 각 키마다 템플릿 렌더 → Playwright 스크린샷 → Pillow WebP 변환
4. `posts/images/<slug>/<key>.webp` 저장

내부 호출: `uv run scripts/render-cards.py [파일] [--only <key>]`

## 규칙

- 치수 1200x630 (OG 비율, DPR 2배 → 실제 2400x1260).
- WebP 품질 92.
- 한글 폰트 Pretendard (CDN).
- 이모지 OS 네이티브 (맥에서 Apple Color Emoji).
