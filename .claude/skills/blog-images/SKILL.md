---
name: blog-images
description: 블로그 초안의 이미지 프롬프트를 Replicate Flux schnell로 실제 이미지 생성, posts/images/<slug>/ 에 저장
argument-hint: [파일경로] [--per-prompt N] [--no-open]
---

블로그 포스트 하단의 `## 이미지 프롬프트` 섹션을 파싱해 Replicate Flux schnell로 실제 이미지를 생성하는 스킬.

## 사용법

```
/blog-images                                          # posts/ 최신 파일
/blog-images posts/2026-04-22-docker-입문.md          # 특정 파일
/blog-images --per-prompt 1                           # 프롬프트당 1장만
/blog-images <파일> --no-open                         # Finder 열지 않음
```

## 전제 조건

1. Replicate 계정 + API 토큰 발급 (https://replicate.com/account/api-tokens)
2. 프로젝트 루트에 `.env` 파일:
   ```
   REPLICATE_API_TOKEN=r8_xxx...
   ```
3. `uv` 설치됨 (`brew install uv` 등)
4. 대상 `.md` 파일 하단에 `## 이미지 프롬프트` 섹션 존재

## 실행 흐름

### 1단계: 인자 파싱
- 첫 번째 위치 인자가 `.md` 경로면 해당 파일 대상
- 없으면 `posts/` 하위에서 수정 시각 가장 최근 `.md` 선택
- `--per-prompt N` (1~4, 기본 3) — 프롬프트당 생성 장수
- `--no-open` — 완료 후 Finder 자동 오픈 비활성

### 2단계: 스크립트 실행

Bash 툴로 아래 명령 실행 (백그라운드 아님, 2~30초 소요):

```bash
uv run scripts/generate-images.py [인자들]
```

### 3단계: 결과 보고

스크립트 출력을 사용자에게 그대로 전달.
저장 위치: `posts/images/<파일명-stem>/` 예:
```
posts/images/2026-04-22-docker-입문/
├── thumbnail-1.webp
├── thumbnail-2.webp
├── thumbnail-3.webp
├── section-1-1.webp
├── ...
```

완료 후 Finder 자동 오픈 (macOS, `--no-open` 없을 때).

## 모델 고정 사항

- 모델: `black-forest-labs/flux-schnell`
- 비율: 16:9
- 포맷: WebP, quality 90
- 스타일 suffix 자동 부착: `flat 2D illustration, soft pastel colors, minimal clean background, tech blog thumbnail, no text, no letters, no writing, 16:9`

## 비용 안내

- flux-schnell 장당 약 $0.003
- 기본 3개 프롬프트 × 3장 = 9장 ≈ $0.027/글
- 실행 종료 시 추정 비용 출력됨

## 규칙

- **이미지에 텍스트를 절대 넣지 않는다** — 스타일 suffix에 `no text, no letters` 박혀 있음. 프롬프트에 "logo", "label", "word" 같은 단어가 있으면 결과가 깨지므로 블로그 초안 작성 시 영문 프롬프트에서도 텍스트 요구를 피할 것.
- 프롬프트는 영문으로 작성 (한글 프롬프트도 동작은 하지만 품질 편차 큼).
- 재생성: 마음에 안 들면 `/blog-images --per-prompt 3` 다시 돌려서 덮어쓰기 (동일 파일명).
- 생성된 이미지는 `posts/` 안에 있어 gitignore 처리됨 (공개 안 됨). 티스토리에는 수동 드래그 업로드.

## 에러 대응

- `REPLICATE_API_TOKEN 없음` → `.env` 확인
- `이미지 프롬프트 섹션을 찾지 못함` → 초안 하단에 `## 이미지 프롬프트` 블록 있는지 확인
- Replicate API 에러 (rate limit, 크레딧 부족 등) → 메시지 그대로 사용자에게 전달
