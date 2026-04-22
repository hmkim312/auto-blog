# auto-blog

Claude Code로 티스토리 블로그 글 초안을 자동 생성하는 프로젝트.

## 사용법

### 가장 빠른 흐름

```bash
/blog <주제>        # 초안 생성 + 자동 검수/교정 한 번에
/blog-images        # 이미지 생성 (수동 호출, 비용 때문에 분리)
```

### 단계별 실행

```bash
/blog-post <주제>   # 9문 질의응답 → 마크다운 초안 + 이미지 프롬프트 생성
/blog-review        # CLAUDE.md 규칙 자가 검수, --fix 로 자동 교정
/blog-images        # 프롬프트를 실제 이미지로 (Replicate recraft-v3)
```

생성된 글은 `posts/YYYY-MM-DD-<슬러그>.md`, 이미지는 `posts/images/<슬러그>/*.webp`. 모두 `.gitignore`에 포함됨. 티스토리에는 수동 드래그 업로드.

## 사전 준비

- Claude Code
- Python + `uv` (이미지 생성용)
- Replicate 계정 + API 토큰 (이미지 생성 시)
- `.env` 파일에 `REPLICATE_API_TOKEN=r8_...` (`.env.example` 참고)

## 구조

```
auto-blog/
├── CLAUDE.md                     # 블로그 글쓰기 규칙 (진리의 원천)
├── AGENTS.md                     # 프로젝트 구조/컨벤션 (AI용)
├── posts/                        # 생성된 글·이미지 (gitignore)
├── scripts/
│   └── generate-images.py        # Replicate 호출 스크립트
└── .claude/skills/
    ├── blog/                     # 초안+검수 묶음
    ├── blog-post/                # 초안 생성
    ├── blog-review/              # 자가 검수
    └── blog-images/              # 이미지 생성
```
