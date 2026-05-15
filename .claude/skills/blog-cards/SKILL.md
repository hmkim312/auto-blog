---
name: blog-cards
description: 초안 끝의 `## 이미지 메타` YAML 블록을 HTML 템플릿으로 렌더해 posts/images/<slug>/*.webp 카드 생성.
argument-hint: "[파일] [--only <이름>]"
---

블로그 초안 끝의 YAML 메타 블록을 Playwright 헤드리스로 렌더해 카드형 이미지(1200x630, WebP) 를 만드는 스킬.

> **권장 모델:** Opus 4.7. 카드 메타 작성·alt 동기화 톤 품질 우선.

## 사용법

```
/blog-cards                              # posts/ 최신 파일
/blog-cards posts/2026-04-25-x.md        # 특정 파일
/blog-cards --only thumb                 # 특정 블록만 렌더
```

## 최초 1회 준비

```
uv run --with playwright python -m playwright install chromium
```

Chromium 을 ~/Library/Caches/ms-playwright 에 설치한다. 한 번만 하면 됨.

## 초안 메타 블록 형식

초안 끝(`## 태그` 다음)에 아래 골격을 둔다. **구체값(hex·문구·이모지)은 매번 글에 맞춰 새로 정한다 — 아래 placeholder 그대로 복사 금지**.

```yaml
## 이미지 메타

palette:
  base: "#<글 톤에 맞는 어두운 hex>"
  accent: "#<감정·강조 색>"
  highlight: "#<base 위에서 떠 보이는 밝은 색>"

thumb:
  template: <thumbnail|thumbnail-bold|thumbnail-stat|thumbnail-quote|thumbnail-magazine>
  # 템플릿별 필드는 아래 "템플릿" 절 참조

section-1:
  template: <section-* 중 하나>
  # 필드 동일

section-2:
  template: <section-* 중 하나>
```

블록 이름(`thumb`, `section-1` ~ `section-N`)이 출력 파일명이 된다 (`posts/images/<slug>/<key>.webp`). 본문 H2 수에 맞춰 동적 (마무리 H2 제외). 카드 수 자체에 코드 레벨 상한은 없다 — 본문 가독성 기준에서 결정.

## H2 메시지 → 슬롯 매핑 절차

CLAUDE.md `## 카드 콘텐츠 작성 원칙` 의 절차를 메타 작성 시점에 그대로 따른다. 양식 카탈로그는 슬롯 선택의 도구일 뿐이고, 메시지가 먼저다.

본문 H2 마다 다음 3단계를 한 번에 한 H2 씩 닫는다. 한 번에 N 개 슬롯을 토해내지 않는다.

1. 그 H2 섹션이 전하는 메시지를 한 문장으로 적는다.
2. 그 문장과 CLAUDE.md `## 카드 콘텐츠 작성 원칙` 의 양식별 적합도 표를 보고 양식 1개를 고른다. 양식이 메시지와 안 맞으면 양식을 바꾼다, 메시지를 비틀지 않는다.
3. 양식의 슬롯에 메시지 본질(동사·명사·수치)을 직접 적는다. 자리채움(카테고리 이름만, `이미지: section-N` 류) 금지.

thumb 카드는 H1 + 도입 정의 한 줄을 가지고 같은 3단계로 별도 수행한다.

## 템플릿 (썸네일 5종 + 섹션 10종)

### 배경 톤 (글 단위 통일)

한 글 안에서 카드 배경 톤은 모두 같은 그룹으로 통일한다. 다크면 다 다크, 라이트면 다 라이트, 컬러풀이면 다 컬러풀. 다크와 라이트, 스플릿을 한 글에 섞지 않는다.

시각 변주는 같은 톤 그룹 안에서 템플릿마다 다른 레이아웃·폰트 크기·아이콘·구성으로 주고, 배경 색 자체를 섞어 만들지 않는다. 글 전체의 통일된 인상을 우선한다.

아래 표의 "배경 정체성" 은 각 템플릿이 어떤 그룹에 속하는지 명세다. 한 글의 카드들은 한 그룹 안에서만 골라 쓴다.

| 그룹 | 템플릿 | 배경 정체성 |
|------|--------|------------|
| 다크 | `thumbnail`, `thumbnail-stat`, `section-hero`, `section-numbered`, `section-timeline`, `section-stat-grid` | base 다크 + accent 글로우 |
| 컬러풀 | `thumbnail-bold`, `section-callout` | accent → base 그라디언트, 임팩트형 |
| 라이트 | `thumbnail-quote`, `section-simple`, `section-flow` | highlight 배경 + base 텍스트, 종이/노트 톤 |
| 스플릿 | `thumbnail-magazine`, `section-split`, `section-compare` | 좌우 다른 배경, 잡지/대비형 |
| 코드 | `section-terminal` | 검정 터미널, 신호등 + 코드 라인 |

각 양식의 "잘 맞는 H2 메시지 형태"는 CLAUDE.md `## 카드 콘텐츠 작성 원칙` 표를 단일 출처로 본다. 아래 카탈로그는 시각·필드 명세이고, H2 메시지 적합도는 그 표가 결정한다.

### 썸네일 5종

- **thumbnail** — 비대칭 분할 (좌측 타이틀 + 우측 배지 사이드바), 다크. 일반·정보형. `kicker`(UPPERCASE), `icon`, `title`, `subtitle`, `badges[]`.
- **thumbnail-bold** — accent 그라디언트 풀블리드 + 글로우. 임팩트 한 줄 글, 결론형. `title` (필수), `subtitle`/`kicker`/`icon`/`badges` 선택.
- **thumbnail-stat** — 좌측 큰 수치 + 우측 타이틀, 다크. 핵심이 수치 1개일 때. `stat_value` (필수, 짧게 — "1.35x", "$41k"), `stat_label`/`stat_unit`/`title`/`subtitle`/`kicker`/`badges` 선택.
- **thumbnail-quote** — 큰 따옴표 + 한 줄, **highlight 라이트 배경 + base 텍스트**. 회고·감정·1인칭 후기. `title` (필수, 인용문 톤), `subtitle`/`attribution`/`badges` 선택.
- **thumbnail-magazine** — 좌측 accent 그라디언트 블록 + 우측 라이트 배경. 잡지 표지 톤, 시각 임팩트 큼. `kicker`, `title`, `label`, `subtitle`, `accent_text`, `meta[]`.

### 섹션 카드 10종

- **section-hero** — 행형 카드 N개 + 하단 요약 바, 다크. H3 가 카드 한 장 분량 설명일 때 (기본). `num`, `title`, `subtitle`, `cards[{icon,title,desc}]` (1~8개 자동 스케일), `footer{label,chips[]}`.
- **section-simple** — 풀쿼트, **highlight 라이트 배경 + base 텍스트**. H3 0~1개 + 한 문장 결론형. `title`, `subtitle`, `attribution`(UPPERCASE), `badges[]`.
- **section-numbered** — 큰 숫자 나열형, 다크. H3 가 명확한 순서·원칙·단계. `kicker`, `title`, `items[{title,desc}]` (3~8개 자동 스케일).
- **section-timeline** — 가로 단계 흐름 (마커 → 마커 → 마커), 다크. H3 들이 시간/버전/이전→이후 흐름. `kicker`, `title`, `subtitle`, `steps[{marker,title,desc}]` (이미 N개 동적).
- **section-split** — 좌측 accent 그라디언트(수치) + 우측 라이트(맥락). 한 수치가 섹션 중심. `stat_label`, `stat_value`, `stat_unit`, `title`, `points[]`.
- **section-stat-grid** — 수치 그리드, 다크. 수치 N개 (1~8개 자동 grid 배치 — 1~3개 1행, 4개 2x2, 5~6개 3x2, 7~8개 4x2). `kicker`, `title`, `subtitle`, `stats[{value,label,delta}]`.
- **section-compare** — A vs B 2컬럼. H3 정확히 2개 + 대립 구도. `title`, `subtitle`, `left{label,title,desc,bullets[],emph}`, `right{…,emph}` — `emph:true` 쪽이 강조 박스.
- **section-callout** — accent 그라디언트 풀블리드 + 좌측 흰 바. 함정·경고·결론형. `icon`, `tag`(UPPERCASE), `title`(메시지), `subtitle`, `attribution`(UPPERCASE).
- **section-terminal** — 검정 터미널 UI (신호등 + 코드 라인). 명령어/코드가 핵심인 섹션. `kicker`, `title`, `subtitle`, `prompt`(예: `~/projects $`), `bar_title`, `commands[{line, type}]`. type 은 `cmd`(명령어)/`out`(출력)/`ok`(✓)/`cmt`(주석). N개 자유.
- **section-flow** — 노드 → 화살표 → 노드 흐름도, **highlight 라이트 배경**. 파이프라인/아키텍처 흐름. `kicker`, `title`, `subtitle`, `nodes[{icon, label, desc, emph}]`, `footer`. N개 자유.

### 갯수 동적 처리

대부분의 섹션 템플릿이 N개 항목에 자동 스케일된다. CSS attribute selector(`body[data-count="N"]`) 로 폰트·padding 자동 축소.

| 템플릿 | 동적 범위 |
|--------|-----------|
| section-hero (cards) | 1~8개. 5+ 부터 폰트·padding 자동 축소 |
| section-numbered (items) | 1~8개. 6+ 부터 자동 축소 |
| section-stat-grid (stats) | 1~8개. grid 형태 자동 변경 (1행/2x2/3x2/4x2) + 폰트 축소 |
| section-timeline (steps) | N개 자유, grid columns 자동 분할 |
| section-terminal (commands) | N개 자유 |
| section-flow (nodes) | N개 자유 (3~6개 권장) |

### 선택 기준

H2 제목(섹션 목적), H3 개수·형태, H3 아래 설명문(수치·결론·시간 흐름)을 종합한다.

- H3 0~1 → `simple`/`callout`
- H3 정확히 2 → `compare` 후보
- H3 3+ 개념 설명 → `hero`/`numbered`
- H3 시간·버전 흐름 → `timeline`
- H3 파이프라인/연결 → `flow` (라이트)
- 수치 4개 이상 → `stat-grid`, 한 수치 중심 → `split`
- 결론형 단일 메시지 → `callout`/`simple`
- 명령어·코드 섹션 → `terminal`

## 팔레트 규칙

- 글의 톤에 맞춰 **hex 3색**(`base`/`accent`/`highlight`) 을 YAML 최상단에 직접 적는다. 프리셋 키워드는 호환용으로만 남아있다 (지정 시 자동 매핑).
- 형식:

  ```yaml
  palette:
    base: "#0E1B2E"
    accent: "#2ECC9E"
    highlight: "#C8F0E8"
  ```

- 색 고르는 기준:
  - **base** — 어두운 톤(#0F~#2F 채도). 다크 템플릿 배경.
  - **accent** — 글의 감정을 한 색으로 압축. 임팩트형 템플릿 배경, 다크 템플릿 강조색으로 함께 쓰임.
  - **highlight** — base 위에서 잘 떠 보이는 밝은 톤. 라이트 템플릿 배경 자체로 쓰이므로 너무 밝거나(#FFF) 너무 채도 없는(회색) 색은 피한다. 약간의 색감 있는 크림·민트·연하늘 톤이 자연스럽다.
- 같은 글의 카드가 여러 장일 때, 다크/라이트/컬러풀 템플릿을 섞어 고르면 한 팔레트 안에서도 시각 다양성이 살아난다.
- 포스트 내 **단일 팔레트 강제**. 블록별 `palette:` 는 무시된다 (스크립트가 차단).
- 지정 없거나 잘못된 형식이면 fallback으로 `indigo` 프리셋 적용.

## 실행 흐름

1. 대상 파일 결정 (인자 or 최신)
2. `## 이미지 메타` 블록 YAML 파싱
3. 각 키마다 템플릿 렌더 → Playwright 스크린샷 → Pillow 로 WebP 변환
4. `posts/images/<slug>/<key>.webp` 저장

## 호출 (내부)

`uv run scripts/render-cards.py [파일] [--only <key>]`

## 규칙

- 치수 1200x630 (OG 비율, DPR 2배로 실제 2400x1260)
- WebP 품질 92
- 한글 폰트 Pretendard (CDN 로드)
- 이모지 OS 네이티브 — 맥에서 Apple Color Emoji 렌더
