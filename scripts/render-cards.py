#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2", "playwright", "pyyaml", "pillow"]
# ///
"""초안의 `## 이미지 메타` YAML 블록을 HTML 템플릿으로 렌더해 WebP 생성."""
from __future__ import annotations

import argparse
import asyncio
import io
import re
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "cards"
POSTS_DIR = ROOT / "posts"

PALETTES = {
    "indigo":  {"base": "#1e1b4b", "accent": "#6366f1", "highlight": "#a78bfa"},
    "teal":    {"base": "#042f2e", "accent": "#14b8a6", "highlight": "#5eead4"},
    "rose":    {"base": "#4c0519", "accent": "#f43f5e", "highlight": "#fda4af"},
    "amber":   {"base": "#451a03", "accent": "#f59e0b", "highlight": "#fcd34d"},
    "slate":   {"base": "#0f172a", "accent": "#64748b", "highlight": "#cbd5e1"},
    "emerald": {"base": "#022c22", "accent": "#10b981", "highlight": "#6ee7b7"},
}

META_HEADER = re.compile(r"^## 이미지 메타\s*$", re.M)


def latest_post() -> Path:
    mds = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mds:
        sys.exit("[error] posts/ 에 마크다운이 없다")
    return mds[0]


def extract_meta(md_path: Path) -> dict:
    text = md_path.read_text()
    m = META_HEADER.search(text)
    if not m:
        sys.exit(f"[error] '## 이미지 메타' 블록을 {md_path.name} 에서 못 찾았다")
    rest = text[m.end():]
    stop = re.search(r"^## ", rest, re.M)
    yaml_text = rest[:stop.start()] if stop else rest
    yaml_text = yaml_text.strip()
    if yaml_text.startswith("```"):
        lines = yaml_text.splitlines()
        if lines[0].startswith("```") and lines[-1].startswith("```"):
            yaml_text = "\n".join(lines[1:-1])
    data = yaml.safe_load(yaml_text)
    if not isinstance(data, dict):
        sys.exit("[error] 이미지 메타가 dict 형태가 아니다")
    return data


def render_html(env: Environment, template_name: str, context: dict) -> str:
    tpl = env.get_template(f"{template_name}.html")
    return tpl.render(**context)


async def render_one(page, html: str, out_path: Path, width: int = 1200, height: int = 630) -> None:
    await page.set_viewport_size({"width": width, "height": height})
    await page.set_content(html, wait_until="networkidle")
    png = await page.screenshot(
        type="png",
        omit_background=False,
        clip={"x": 0, "y": 0, "width": width, "height": height},
    )
    Image.open(io.BytesIO(png)).convert("RGB").save(out_path, format="WEBP", quality=92, method=6)


async def main_async(md_path: Path, only: str | None) -> None:
    meta = extract_meta(md_path)
    slug = md_path.stem
    out_dir = POSTS_DIR / "images" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # 포스트 단위 단일 팔레트: top-level `palette` 우선
    # - dict 형태 {base, accent, highlight} 면 그대로 사용 (AI가 글 내용 보고 정한 색상)
    # - 문자열이면 PALETTES 프리셋 키로 lookup (하위 호환)
    post_palette = meta.pop("palette", None)
    if not post_palette:
        for spec in meta.values():
            if isinstance(spec, dict) and spec.get("palette"):
                post_palette = spec["palette"]
                break
    if isinstance(post_palette, dict):
        palette_colors = {
            "base": post_palette.get("base", "#1e1b4b"),
            "accent": post_palette.get("accent", "#6366f1"),
            "highlight": post_palette.get("highlight", "#a78bfa"),
        }
        print(f"[palette] custom {palette_colors}")
    else:
        key = post_palette or "indigo"
        palette_colors = PALETTES.get(key, PALETTES["indigo"])
        print(f"[palette] preset '{key}' 적용")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )

    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        context = await browser.new_context(device_scale_factor=1)
        page = await context.new_page()
        for name, spec in meta.items():
            if only and only != name:
                continue
            if not isinstance(spec, dict):
                print(f"[skip] {name}: dict 아님")
                continue
            spec.pop("palette", None)  # 블록별 팔레트는 무시 (포스트 내 색상 통일)
            template = spec.pop("template", "thumbnail")
            ctx = {**palette_colors, **spec}
            html = render_html(env, template, ctx)
            out = out_dir / f"{name}.webp"
            print(f"[render] {name} → {out.relative_to(ROOT)} (template={template})")
            await render_one(page, html, out)
        await browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="YAML 이미지 메타 → HTML 템플릿 → WebP 렌더")
    ap.add_argument("post", nargs="?", help="posts/*.md 경로 (생략 시 최신)")
    ap.add_argument("--only", help="특정 블록만 렌더 (예: thumb)")
    args = ap.parse_args()
    md = Path(args.post).resolve() if args.post else latest_post()
    if not md.exists():
        sys.exit(f"[error] 파일 없음: {md}")
    asyncio.run(main_async(md, args.only))
    print("[done]")


if __name__ == "__main__":
    main()
