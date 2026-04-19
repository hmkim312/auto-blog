# auto-blog

Claude Code로 티스토리 블로그 글 초안을 자동 생성하는 프로젝트.

## 사용법

```bash
/blog-post <주제>
```

질의응답 5개 → 마크다운 초안 생성 → 이미지 프롬프트 생성

생성된 파일은 `posts/` 폴더에 저장된다. (`posts/`는 `.gitignore`에 포함)

## 구조

```
auto-blog/
├── CLAUDE.md                        # 블로그 글쓰기 규칙
├── posts/                           # 생성된 글 (git 제외)
└── .claude/
    └── skills/
        └── blog-post/
            └── SKILL.md             # /blog-post 스킬
```
