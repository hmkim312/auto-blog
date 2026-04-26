---
name: blog-cards
description: 초안 끝의 `## 이미지 메타` YAML 블록을 HTML 템플릿으로 렌더해 posts/images/<slug>/*.webp 카드 생성.
argument-hint: "[파일] [--only <이름>]"
---

블로그 초안 끝의 YAML 메타 블록을 Playwright 헤드리스로 렌더해 카드형 이미지(1200x630, WebP) 를 만드는 스킬.

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
  template: <thumbnail|thumbnail-bold|thumbnail-stat|thumbnail-quote>
  # 템플릿별 필드는 아래 "템플릿 12종" 절 참조

section-1:
  template: <section-* 8종 중 하나>
  # 필드 동일

section-2:
  template: <section-* 8종 중 하나>
```

블록 이름(`thumb`, `section-1` ~ `section-N`, 최대 `section-4`)이 출력 파일명이 된다 (`posts/images/<slug>/<key>.webp`). 카드 총 수 1+N, 캡 5장. 본문 H2 수에 맞춰 동적 (마무리 H2 제외).

## 템플릿 12종 (썸네일 4 + 섹션 8)

**썸네일 — 글 톤에 맞춰 1개 고르기**

- **thumbnail** — 비대칭 분할 (좌측 타이틀 + 우측 배지 사이드바). 일반·정보형. `kicker`(UPPERCASE), `icon`, `title`, `subtitle`, `badges[]`.
- **thumbnail-bold** — 풀블리드 큰 타이틀. 임팩트 한 줄 글, 결론형. `title` (필수), `subtitle`/`kicker`/`icon`/`badges` 선택.
- **thumbnail-stat** — 좌측 큰 수치 + 우측 타이틀. 핵심이 수치 1개일 때. `stat_value` (필수, 짧게 — "1.35x", "$41k"), `stat_label`/`stat_unit`/`title`/`subtitle`/`kicker`/`badges` 선택.
- **thumbnail-quote** — 큰 따옴표 + 한 줄. 회고·감정·1인칭 후기. `title` (필수, 인용문 톤), `subtitle`/`attribution`/`badges` 선택.

**섹션 카드 — H2 + 그 아래 H3 + H3 아래 설명문을 종합해 1개 고르기**

- **section-hero** — 행형 카드 3~4개 + 하단 요약 바. H3 3~4개 + 각 H3 가 카드 한 장 분량 설명일 때 (기본). `num`, `title`, `subtitle`, `cards[{icon,title,desc}]`, `footer{label,chips[]}`.
- **section-simple** — 풀쿼트 (큰 따옴표 + 제목 + attribution). H3 0~1개 + 한 문장 결론형. `title`, `subtitle`, `attribution`(UPPERCASE), `badges[]`.
- **section-numbered** — 큰 숫자 나열형. H3 3~5개가 명확한 순서·원칙·단계. `kicker`, `title`, `items[{title,desc}]`.
- **section-timeline** — 가로 단계 흐름 (마커 → 마커 → 마커). H3 들이 시간/버전/이전→이후 흐름. `kicker`, `title`, `subtitle`, `steps[{marker,title,desc}]` (3~5개).
- **section-split** — 좌우 수치+맥락 2분할. 한 수치가 섹션 중심. `stat_label`, `stat_value`, `stat_unit`, `title`, `points[]` (2~3개).
- **section-stat-grid** — 2x2 수치 그리드. 수치 4개 가까이 (벤치마크·요금·통계). `kicker`, `title`, `subtitle`, `stats[{value,label,delta}]` (정확히 4개).
- **section-compare** — A vs B 2컬럼. H3 정확히 2개 + 대립 구도. `title`, `subtitle`, `left{label,title,desc,bullets[],emph}`, `right{…,emph}` — `emph:true` 쪽이 강조 박스.
- **section-callout** — 단일 경고·핵심 메시지 1개로 모이는 섹션 (함정·경고·결론형). `icon`, `tag`(UPPERCASE), `title`(메시지), `subtitle`, `attribution`(UPPERCASE).

**선택 기준** — H2 제목(섹션 목적), H3 개수·형태, H3 아래 설명문(수치·결론·시간 흐름)을 종합. H3 0~1 → `simple`/`callout`, H3 정확히 2 → `compare` 후보, H3 3~5 → `hero`/`numbered`/`timeline` 중 키워드(번호/시간) 보고. 본문에 수치 4개 이상이면 `stat-grid`, 한 수치 중심이면 `split`. 결론형 단일 메시지면 `callout`/`simple`.

## 팔레트 규칙

- 글의 톤에 맞춰 **hex 3색**(`base`/`accent`/`highlight`) 을 YAML 최상단에 직접 적는다. 프리셋 키워드는 호환용으로만 남아있다 (지정 시 자동 매핑).
- 형식:

  ```yaml
  palette:
    base: "#0F1419"
    accent: "#FF8A3D"
    highlight: "#F5D9B5"
  ```

- 색 고르는 기준:
  - **base** — 어두운 톤(#0F~#1F 채도) 가 가독성에 유리. 너무 검지 않게.
  - **accent** — 글의 감정을 한 색으로 압축 (압박·경고 = 오렌지/빨강, 성장 = 그린, 트렌드 = 보라/파랑, 회고 = 무채색).
  - **highlight** — base 위에서 잘 떠 보이는 밝은 톤. accent 와 너무 가깝지 않게.
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
