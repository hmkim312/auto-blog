#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.31",
#   "python-dotenv>=1.0",
# ]
# ///
"""
Tavily 웹 검색 어댑터. /blog-research 스킬이 호출한다.

사용법:
  BLOG_RESEARCH_SESSION_ID=<id> uv run scripts/tavily-search.py --query "..."
  BLOG_RESEARCH_SESSION_ID=smoke uv run scripts/tavily-search.py --query "test" --dry-run

스킬은 세션 단위 하드 카운터로 1 run 당 Tavily 호출 ≤8 을 보장한다.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUDGET_FILE = ROOT / ".omc" / "state" / "tavily-budget.json"
FIXTURE_FILE = ROOT / "scripts" / "fixtures" / "tavily-dry-run.json"
TAVILY_ENDPOINT = "https://api.tavily.com/search"

EXIT_MISSING_TOKEN = 1
EXIT_HTTP_ERROR = 2
EXIT_RATE_LIMIT = 3
EXIT_BUDGET_EXCEEDED = 4
EXIT_MISSING_SESSION = 5


def log(msg: str) -> None:
    """진행 로그는 stderr 로 (stdout 은 JSON 전용)."""
    print(msg, file=sys.stderr)


def load_budget(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        log(f"[warn] budget 파일 파싱 실패, 새로 시작: {path}")
        return {}


def save_budget(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def check_and_reserve_budget(budget_file: Path, session_id: str, budget_max: int) -> dict:
    """
    세션 카운터를 조회. count >= budget_max 면 exit 4.
    예약은 하지 않는다 (실제 증가는 호출 성공 후).
    """
    data = load_budget(budget_file)
    entry = data.get(session_id, {"count": 0, "started_at": datetime.now(timezone.utc).isoformat()})
    if entry["count"] >= budget_max:
        log(f"[error] budget exceeded ({entry['count']}/{budget_max}) for session {session_id}")
        sys.exit(EXIT_BUDGET_EXCEEDED)
    return data


def commit_budget(budget_file: Path, session_id: str, data: dict) -> dict:
    """호출 성공 시 count +1. 데이터 갱신 후 반환."""
    entry = data.get(session_id, {"count": 0, "started_at": datetime.now(timezone.utc).isoformat()})
    entry["count"] = int(entry.get("count", 0)) + 1
    data[session_id] = entry
    save_budget(budget_file, data)
    return entry


def build_tavily_payload(args: argparse.Namespace, api_key: str) -> dict:
    query = args.query
    if args.language or args.region:
        hints = []
        if args.language:
            hints.append(f"language: {args.language}")
        if args.region:
            hints.append(f"region: {args.region}")
        query = f"{query} ({', '.join(hints)})"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": args.search_depth,
        "max_results": args.max_results,
        "include_answer": bool(args.include_answer),
    }
    return payload


def call_tavily(payload: dict, retries: int = 2) -> dict:
    """429 발생 시 15초 간격 최대 2회 재시도."""
    for attempt in range(retries + 1):
        try:
            resp = requests.post(TAVILY_ENDPOINT, json=payload, timeout=30)
        except requests.RequestException as exc:
            log(f"[error] 네트워크 오류: {exc}")
            sys.exit(EXIT_HTTP_ERROR)
        if resp.status_code == 429:
            if attempt < retries:
                wait = 15 * (attempt + 1)
                log(f"[rate limit] {wait}s 대기 후 재시도 ({attempt + 1}/{retries})")
                time.sleep(wait)
                continue
            log(f"[error] Tavily rate limit 초과 (재시도 소진)")
            sys.exit(EXIT_RATE_LIMIT)
        if not resp.ok:
            snippet = resp.text[:300]
            log(f"[error] Tavily HTTP {resp.status_code}: {snippet}")
            sys.exit(EXIT_HTTP_ERROR)
        try:
            return resp.json()
        except json.JSONDecodeError:
            log(f"[error] Tavily 응답 JSON 파싱 실패: {resp.text[:300]}")
            sys.exit(EXIT_HTTP_ERROR)
    sys.exit(EXIT_HTTP_ERROR)


def summarize_results(raw: dict, max_results: int) -> list[dict]:
    items = raw.get("results", []) or []
    summarized = []
    for item in items[:max_results]:
        content = item.get("content", "") or ""
        snippet = content.strip().replace("\n", " ")
        if len(snippet) > 200:
            snippet = snippet[:197].rstrip() + "..."
        summarized.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": snippet,
            "score": item.get("score"),
            "published_date": item.get("published_date"),
        })
    return summarized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tavily 웹 검색 어댑터 (블로그 리서치용)")
    parser.add_argument("--query", required=True, help="검색어 (한국어/영어)")
    parser.add_argument("--max-results", type=int, default=10, help="반환 결과 개수 (1~10)")
    parser.add_argument("--search-depth", choices=["basic", "advanced"], default="basic")
    parser.add_argument("--include-answer", action="store_true", help="Tavily LLM 요약 포함")
    parser.add_argument("--language", default=None, help="검색 쿼리 언어 힌트 (예: ko)")
    parser.add_argument("--region", default=None, help="검색 쿼리 지역 힌트 (예: KR)")
    parser.add_argument("--dry-run", action="store_true", help="fixture 반환 (네트워크·카운터 없음)")
    parser.add_argument(
        "--budget-file",
        type=Path,
        default=DEFAULT_BUDGET_FILE,
        help="세션 카운터 JSON 파일",
    )
    parser.add_argument("--budget-max", type=int, default=8, help="세션당 허용 호출 횟수 상한")
    args = parser.parse_args()

    if not args.query.strip():
        parser.error("--query 는 비어 있을 수 없다")
    if not 1 <= args.max_results <= 10:
        parser.error("--max-results 는 1~10 범위")
    return args


def main() -> None:
    args = parse_args()

    if args.dry_run:
        if not FIXTURE_FILE.exists():
            log(f"[error] fixture 없음: {FIXTURE_FILE}")
            sys.exit(EXIT_HTTP_ERROR)
        fixture = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
        fixture["budget"] = {"dry_run": True}
        print(json.dumps(fixture, indent=2, ensure_ascii=False))
        return

    session_id = os.getenv("BLOG_RESEARCH_SESSION_ID")
    if not session_id:
        log("[error] BLOG_RESEARCH_SESSION_ID 없음. 스킬이 세션 ID를 주입하지 않았다.")
        sys.exit(EXIT_MISSING_SESSION)

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        log("[error] TAVILY_API_KEY 없음. .env 에 추가하세요")
        sys.exit(EXIT_MISSING_TOKEN)

    budget_data = check_and_reserve_budget(args.budget_file, session_id, args.budget_max)

    payload = build_tavily_payload(args, api_key)
    raw = call_tavily(payload)

    entry = commit_budget(args.budget_file, session_id, budget_data)

    output = {
        "query": args.query,
        "count": len(raw.get("results", []) or []),
        "results": summarize_results(raw, args.max_results),
        "budget": {
            "used": entry["count"],
            "max": args.budget_max,
            "session": session_id,
        },
    }
    if args.include_answer:
        output["answer"] = raw.get("answer", "")

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
