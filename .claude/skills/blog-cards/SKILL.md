---
name: blog-cards
description: 초안 끝의 `## 이미지 메타` YAML 블록을 HTML 템플릿으로 렌더해 posts/images/<slug>/*.webp 카드 생성. AI 이미지(/blog-images) 와 병행.
argument-hint: "[파일] [--only <이름>]"
---

블로그 초안 끝의 YAML 메타 블록을 Playwright 헤드리스로 렌더해 카드형 이미지(1200x630, WebP) 를 만드는 스킬. AI 생성 이미지(/blog-images) 와는 별개 경로.

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

초안 파일 끝 (기존 `## 이미지 프롬프트` 블록과 별개로) 아래 블록을 추가한다.

```markdown
## 이미지 메타

thumb:
  template: thumbnail       # thumbnail | section-hero | section-simple
  palette: indigo           # indigo | teal | rose | amber | slate | emerald
  icon: "🔒"
  title: "제목 (대)"
  subtitle: "부제목 한 줄"
  badges: ["배지1", "배지2", "배지3"]

section-1:
  template: section-hero
  palette: teal
  title: "섹션 제목"
  subtitle: "부제"
  cards:
    - icon: "⏱️"
      title: "카드1"
      desc: "짧은 설명"
    - icon: "📅"
      title: "카드2"
      desc: "짧은 설명"
    - icon: "🔄"
      title: "카드3"
      desc: "짧은 설명"
  footer:
    label: "요약"
    chips: ["칩1", "칩2", "칩3"]

section-2:
  template: section-simple
  palette: rose
  title: "경험 섹션 제목"
  subtitle: "부제"
  badges: ["배지1", "배지2"]
```

블록 이름(`thumb`, `section-1`, `section-2`)이 출력 파일명이 된다 (`posts/images/<slug>/thumb.webp`).

## 템플릿 6종

- **thumbnail** — 비대칭 분할 썸네일 (좌측 제목 큰 블록 + 우측 배지 세로 리스트). `kicker`(UPPERCASE 라벨), `icon`(이모지), `title`, `subtitle`, `badges[]`.
- **section-hero** — 넘버링 + 가로 행형 카드 3~4개 + 하단 요약 바. `num`(예 "01"), `title`, `subtitle`, `cards[{icon,title,desc}]`, `footer{label,chips[]}`.
- **section-simple** — 풀쿼트 스타일 (큰 따옴표 + 제목 + attribution 라인). 단일 선언/결론형 섹션. `title`, `subtitle`, `attribution`(UPPERCASE), `badges[]`.
- **section-numbered** — 큰 숫자 나열형. 순서·원칙·단계 3~5개. `kicker`, `title`, `items[{title,desc}]`.
- **section-split** — 좌우 수치+맥락 2분할. 한 수치가 중심일 때. `stat_label`, `stat_value`, `stat_unit`, `title`, `points[]` (2~3개).
- **section-compare** — A vs B 2컬럼 비교. `title`, `subtitle`, `left{label,title,desc,bullets[],emph}`, `right{…,emph}` — `emph:true` 쪽이 강조 박스.

## 팔레트 규칙

- 팔레트 프리셋: `indigo`, `teal`, `rose`, `amber`, `slate`, `emerald`
- 각 프리셋은 base(배경) + accent(포인트) + highlight(강조 텍스트) 3색 이내
- **포스트 내 단일 팔레트 강제**. YAML 최상단 `palette:` 키로 지정. 블록별 `palette:` 는 무시된다.
- 지정 없으면 `indigo` 기본

## 팔레트 규칙

- 팔레트 프리셋: `indigo`, `teal`, `rose`, `amber`, `slate`, `emerald`
- 각 프리셋은 base(배경) + accent(포인트) + highlight(강조 텍스트) 3색 이내로만 구성됨 — 3색 제한 룰 준수
- `palette` 생략 시 thumb 은 indigo, 섹션은 teal 기본

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
- AI 경로(/blog-images) 와 병행 가능. 초안에 두 블록 다 두면 각각 돌려도 됨
