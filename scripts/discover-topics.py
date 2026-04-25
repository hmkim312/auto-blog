#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "feedparser",
#   "beautifulsoup4",
# ]
# ///
"""AI 블로그 주제 후보 수집기.

각 소스에서 최근 항목을 긁어 표준 JSON 배열로 stdout 에 출력한다.
실패한 소스는 stderr 에 경고만 남기고 계속 진행한다.

스코어링·필터링·랭킹은 호출자(LLM) 가 한다. 이 스크립트는 raw 수집만.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
import time
from dataclasses import asdict, dataclass
from typing import Callable

import feedparser
import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (auto-blog discover/1.0)"
TIMEOUT = 15


@dataclass
class Item:
    source: str
    title: str
    url: str
    summary: str = ""
    published: str = ""
    extra: dict | None = None


def warn(msg: str) -> None:
    print(f"[discover] {msg}", file=sys.stderr)


def _get(url: str) -> requests.Response:
    return requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)


def fetch_hn(hours: int = 48, limit: int = 30) -> list[Item]:
    cutoff = int(time.time()) - hours * 3600
    url = (
        "https://hn.algolia.com/api/v1/search"
        f"?tags=story&numericFilters=created_at_i>{cutoff}"
        "&query=AI%20OR%20LLM%20OR%20agent%20OR%20Claude%20OR%20GPT"
        "&hitsPerPage=50"
    )
    r = _get(url)
    r.raise_for_status()
    hits = r.json().get("hits", [])
    hits.sort(key=lambda h: h.get("points", 0), reverse=True)
    items: list[Item] = []
    for h in hits[:limit]:
        items.append(
            Item(
                source="hackernews",
                title=h.get("title") or "",
                url=h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                summary=f"{h.get('points', 0)} points · {h.get('num_comments', 0)} comments",
                published=h.get("created_at", ""),
            )
        )
    return items


def fetch_github_trending(language: str | None = None, limit: int = 20) -> list[Item]:
    url = "https://github.com/trending"
    if language:
        url += f"/{language}"
    url += "?since=daily"
    r = _get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items: list[Item] = []
    for art in soup.select("article.Box-row")[:limit]:
        h2 = art.select_one("h2 a")
        if not h2:
            continue
        repo = h2.get_text(strip=True).replace("\n", "").replace(" ", "")
        href = "https://github.com" + (h2.get("href") or "")
        desc_el = art.select_one("p")
        desc = desc_el.get_text(strip=True) if desc_el else ""
        stars_el = art.select_one("a.Link--muted")
        stars = stars_el.get_text(strip=True) if stars_el else ""
        items.append(
            Item(
                source="github_trending",
                title=repo,
                url=href,
                summary=(desc + (f" · ★{stars}" if stars else "")).strip(),
            )
        )
    return items


def fetch_anthropic_news(limit: int = 10) -> list[Item]:
    r = _get("https://www.anthropic.com/news")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    seen: set[str] = set()
    items: list[Item] = []
    for a in soup.select('a[href^="/news/"]'):
        href = a.get("href") or ""
        if href in seen or href in {"/news/", "/news"}:
            continue
        seen.add(href)
        title = a.get_text(" ", strip=True)
        if not title or len(title) < 6:
            continue
        items.append(
            Item(
                source="anthropic_news",
                title=title,
                url="https://www.anthropic.com" + href,
            )
        )
        if len(items) >= limit:
            break
    return items


def fetch_rss(source: str, url: str, limit: int = 15) -> list[Item]:
    feed = feedparser.parse(url)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"RSS parse failed: {feed.bozo_exception}")
    items: list[Item] = []
    for e in feed.entries[:limit]:
        summary = (getattr(e, "summary", "") or "")[:240]
        items.append(
            Item(
                source=source,
                title=getattr(e, "title", "") or "",
                url=getattr(e, "link", "") or "",
                summary=summary,
                published=getattr(e, "published", "") or getattr(e, "updated", ""),
            )
        )
    return items


SOURCES: list[tuple[str, Callable[[], list[Item]]]] = [
    ("hackernews", lambda: fetch_hn(hours=48, limit=30)),
    ("github_trending_python", lambda: fetch_github_trending("python", limit=15)),
    ("github_trending_typescript", lambda: fetch_github_trending("typescript", limit=10)),
    ("arxiv_cs_ai", lambda: fetch_rss("arxiv_cs_ai", "https://rss.arxiv.org/rss/cs.AI", limit=15)),
    ("openai_blog", lambda: fetch_rss("openai_blog", "https://openai.com/blog/rss.xml", limit=10)),
    ("anthropic_news", lambda: fetch_anthropic_news(limit=10)),
    ("deepmind_blog", lambda: fetch_rss("deepmind_blog", "https://blog.google/technology/google-deepmind/rss/", limit=10)),
    ("geeknews", lambda: fetch_rss("geeknews", "https://news.hada.io/rss/news", limit=20)),
]


def gather() -> list[Item]:
    out: list[Item] = []
    with cf.ThreadPoolExecutor(max_workers=len(SOURCES)) as ex:
        futures = {ex.submit(fn): name for name, fn in SOURCES}
        for fut in cf.as_completed(futures):
            name = futures[fut]
            try:
                items = fut.result()
                warn(f"{name}: {len(items)} items")
                out.extend(items)
            except Exception as e:
                warn(f"{name}: FAILED ({e})")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="AI blog topic candidate collector")
    p.add_argument("--pretty", action="store_true", help="pretty-print JSON output")
    args = p.parse_args()

    items = gather()
    payload = [asdict(i) for i in items]
    if args.pretty:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    warn(f"total: {len(payload)} items from {len(SOURCES)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
