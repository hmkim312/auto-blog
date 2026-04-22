#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "replicate>=0.34",
#   "python-dotenv>=1.0",
#   "requests>=2.31",
# ]
# ///
"""
블로그 포스트의 이미지 프롬프트를 읽어 Replicate Flux schnell로 이미지 생성.

사용법:
  uv run scripts/generate-images.py posts/2026-04-22-docker-입문.md
  uv run scripts/generate-images.py                  # posts/ 최신 파일
  uv run scripts/generate-images.py --per-prompt 1   # 프롬프트당 1장만
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import replicate
import requests
from dotenv import load_dotenv

STYLE_SUFFIX = (
    "flat 2D illustration, soft pastel colors, minimal clean background, "
    "tech blog thumbnail, no text, no letters, no writing, 16:9"
)
MODEL = "black-forest-labs/flux-schnell"
ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
IMAGES_ROOT = POSTS_DIR / "images"

LABEL_TO_SLUG = {
    "대표 썸네일": "thumbnail",
    "썸네일": "thumbnail",
    "섹션 1 삽화": "section-1",
    "섹션 2 삽화": "section-2",
    "선택 섹션 삽화": "section-optional",
}


def latest_post() -> Path:
    md_files = sorted(
        (p for p in POSTS_DIR.glob("*.md")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not md_files:
        sys.exit(f"[error] posts/ 에 .md 파일이 없음")
    return md_files[0]


def parse_prompts(md: str) -> list[tuple[str, str]]:
    """마크다운에서 (label, prompt) 튜플 리스트 추출."""
    # 이미지 프롬프트 섹션만 잘라냄
    m = re.search(r"##\s*이미지\s*프롬프트.*$", md, re.DOTALL)
    if not m:
        return []
    section = m.group(0)

    # **label**\n> prompt 패턴
    pattern = re.compile(r"\*\*(.+?)\*\*\s*\n>\s*(.+?)(?=\n\s*\n|\Z)", re.DOTALL)
    results: list[tuple[str, str]] = []
    for match in pattern.finditer(section):
        label = match.group(1).strip()
        prompt = re.sub(r"\s+", " ", match.group(2)).strip()
        results.append((label, prompt))
    return results


def label_slug(label: str) -> str:
    if label in LABEL_TO_SLUG:
        return LABEL_TO_SLUG[label]
    # fallback: 알파벳/숫자/하이픈만
    s = re.sub(r"[^\w가-힣]+", "-", label).strip("-").lower()
    return s or "image"


def ensure_token() -> None:
    load_dotenv(ROOT / ".env")
    if not os.getenv("REPLICATE_API_TOKEN"):
        sys.exit("[error] REPLICATE_API_TOKEN 없음. .env 에 추가하세요")


def generate_for_prompt(prompt: str, n: int, out_dir: Path, base_name: str, retries: int = 3) -> list[Path]:
    full_prompt = f"{prompt}, {STYLE_SUFFIX}"
    print(f"  → {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
    for attempt in range(retries):
        try:
            output = replicate.run(
                MODEL,
                input={
                    "prompt": full_prompt,
                    "num_outputs": n,
                    "aspect_ratio": "16:9",
                    "output_format": "webp",
                    "output_quality": 90,
                    "go_fast": True,
                },
            )
            break
        except Exception as e:
            msg = str(e)
            if "429" in msg and attempt < retries - 1:
                wait = 15 * (attempt + 1)
                print(f"  [rate limit] {wait}초 대기 후 재시도... ({attempt + 1}/{retries})")
                time.sleep(wait)
            else:
                raise
    saved: list[Path] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, item in enumerate(output, 1):
        dest = out_dir / f"{base_name}-{idx}.webp"
        if hasattr(item, "read"):
            dest.write_bytes(item.read())
        else:
            resp = requests.get(str(item), timeout=60)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        saved.append(dest)
        print(f"    saved: {dest.relative_to(ROOT)}")
    return saved


def open_finder(path: Path) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="블로그 포스트용 이미지 생성 (Replicate Flux schnell)")
    parser.add_argument("post", nargs="?", help="대상 .md 파일 경로 (생략 시 posts/ 최신)")
    parser.add_argument("--per-prompt", type=int, default=3, help="프롬프트당 이미지 장수 (1~4, 기본 3)")
    parser.add_argument("--no-open", action="store_true", help="완료 후 Finder 열지 않음")
    args = parser.parse_args()

    if not 1 <= args.per_prompt <= 4:
        sys.exit("[error] --per-prompt 는 1~4 범위")

    ensure_token()

    post_path = Path(args.post).resolve() if args.post else latest_post()
    if not post_path.exists():
        sys.exit(f"[error] 파일 없음: {post_path}")

    md = post_path.read_text(encoding="utf-8")
    prompts = parse_prompts(md)
    if not prompts:
        sys.exit("[error] 이미지 프롬프트 섹션을 찾지 못함. '## 이미지 프롬프트' 블록 확인 필요")

    slug = post_path.stem
    out_dir = IMAGES_ROOT / slug

    print(f"[post] {post_path.relative_to(ROOT)}")
    print(f"[output] {out_dir.relative_to(ROOT)}")
    print(f"[model] {MODEL}  n={args.per_prompt}")
    print(f"[prompts] {len(prompts)}개")
    print()

    all_saved: list[Path] = []
    for i, (label, prompt) in enumerate(prompts):
        if i > 0:
            time.sleep(12)  # rate limit: burst=1, ~10s window
        base = label_slug(label)
        print(f"[{label}]")
        all_saved.extend(generate_for_prompt(prompt, args.per_prompt, out_dir, base))
        print()

    total_cost = 0.003 * len(all_saved)  # flux-schnell 기준 추정
    print(f"완료: {len(all_saved)}장, 추정 비용 ~${total_cost:.3f}")

    if not args.no_open:
        open_finder(out_dir)


if __name__ == "__main__":
    main()
