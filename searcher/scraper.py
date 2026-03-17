from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Any

import requests
from bs4 import BeautifulSoup


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 12
MAX_POSTS = 25
MAX_VERIFY_POSTS = 12


@dataclass
class ScrapedPost:
    url: str
    post_date: date | None
    snippet: str


def _extract_profile_name(soup: BeautifulSoup, profile_url: str) -> str:
    if soup.title and soup.title.text.strip():
        return soup.title.text.strip().split("|")[0].strip()

    # Fallback to URL slug when title metadata is unavailable.
    slug = profile_url.rstrip("/").split("/")[-1]
    return slug.replace("-", " ").title() or "LinkedIn User"


def _normalize_post_url(href: str) -> str:
    if href.startswith("http"):
        return href
    return f"https://www.linkedin.com{href}"


def _parse_post_date(text: str) -> date | None:
    normalized = text.strip()
    if not normalized:
        return None

    # Common formats that may appear in snippets or embedded text.
    for pattern, fmt in [
        (r"\b\d{4}-\d{2}-\d{2}\b", "%Y-%m-%d"),
        (r"\b\d{2}/\d{2}/\d{4}\b", "%d/%m/%Y"),
        (r"\b\d{1,2} [A-Za-z]{3,9} \d{4}\b", "%d %B %Y"),
    ]:
        match = re.search(pattern, normalized)
        if not match:
            continue

        raw = match.group(0)
        try:
            if fmt == "%d %B %Y":
                # Try both short and long month names.
                try:
                    return datetime.strptime(raw, "%d %b %Y").date()
                except ValueError:
                    return datetime.strptime(raw, "%d %B %Y").date()
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    return None


def _normalize_for_match(text: str) -> str:
    lowered = text.lower()
    # Keep @ and #, normalize the rest to spaces for resilient phrase matching.
    cleaned = re.sub(r"[^a-z0-9@#]+", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def _matches_keyword(candidate_text: str, keyword: str) -> bool:
    raw_keyword = keyword.strip().lower()
    if not raw_keyword:
        return False

    mode = "keyword"
    if raw_keyword.startswith("@"):
        mode = "mention"
    elif raw_keyword.startswith("#"):
        mode = "hashtag"

    normalized_keyword = _normalize_for_match(raw_keyword).lstrip("#").lstrip("@").strip()
    if not normalized_keyword:
        return False

    normalized_candidate = _normalize_for_match(candidate_text)
    compact_keyword = normalized_keyword.replace(" ", "")

    if mode == "mention":
        mention_variants = [f"@{normalized_keyword}", f"@{compact_keyword}"]
        return any(re.search(rf"(^|\s){re.escape(v)}($|\s)", normalized_candidate) for v in mention_variants)

    if mode == "hashtag":
        hashtag_variants = [f"#{normalized_keyword}", f"#{compact_keyword}"]
        return any(re.search(rf"(^|\s){re.escape(v)}($|\s)", normalized_candidate) for v in hashtag_variants)

    # Keyword mode: match complete phrase boundary, not loose substring.
    if re.search(rf"\b{re.escape(normalized_keyword)}\b", normalized_candidate):
        return True

    # Also allow keyword typed without # to match hashtags in content.
    hashtag_variants = [f"#{normalized_keyword}", f"#{compact_keyword}"]
    return any(re.search(rf"(^|\s){re.escape(v)}($|\s)", normalized_candidate) for v in hashtag_variants)


def _post_contains_keyword_from_html(html_text: str, keyword: str) -> bool:
    soup = BeautifulSoup(html_text, "lxml")
    page_text = soup.get_text(" ", strip=True)
    return _matches_keyword(page_text, keyword)


def _verify_post_content(post_url: str, keyword: str) -> bool:
    try:
        response = requests.get(
            post_url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException:
        return False

    return _post_contains_keyword_from_html(response.text, keyword)


def scrape_linkedin_posts(profile_url: str, hashtag: str) -> dict[str, Any]:
    search_term = hashtag.lower().strip()

    response = requests.get(
        profile_url,
        headers=REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )
    if response.status_code == 999:
        raise RuntimeError("LinkedIn blocked automated access (HTTP 999). Try again with authenticated browser-based collection.")

    response.raise_for_status()

    html_lower = response.text.lower()
    if any(token in html_lower for token in ["authwall", "sign in", "join linkedin", "login"]):
        raise RuntimeError("LinkedIn returned a login/authwall page, so posts are not accessible in direct scraping mode.")

    soup = BeautifulSoup(response.text, "lxml")
    profile_name = _extract_profile_name(soup, profile_url)

    found_posts: list[ScrapedPost] = []
    seen_urls: set[str] = set()
    pending_posts: list[ScrapedPost] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        link_text = anchor.get_text(" ", strip=True)
        if "linkedin.com/posts/" not in href and "/posts/" not in href:
            continue

        # Include nearby text to approximate post description context.
        parent_text = anchor.parent.get_text(" ", strip=True) if anchor.parent else ""
        combined = f"{href} {link_text} {parent_text}"
        if not _matches_keyword(combined, search_term):
            continue

        post_url = _normalize_post_url(href)
        if post_url in seen_urls:
            continue

        seen_urls.add(post_url)
        snippet = re.sub(r"\s+", " ", link_text).strip()[:240]
        pending_posts.append(
            ScrapedPost(
                url=post_url,
                post_date=_parse_post_date(f"{href} {link_text}"),
                snippet=snippet,
            )
        )

        if len(pending_posts) >= MAX_POSTS:
            break

    # Stage 2: Open candidate post pages and verify keyword/mention/hashtag in page content.
    verified_count = 0
    for post in pending_posts:
        if verified_count >= MAX_VERIFY_POSTS:
            break

        if _verify_post_content(post.url, search_term):
            found_posts.append(post)
            verified_count += 1

    # Fallback: if no posts can be verified (auth/blocked), keep initial candidates instead of blank output.
    if not found_posts:
        found_posts = pending_posts

    return {
        "profile_name": profile_name,
        "profile_url": response.url,
        "hashtag": search_term,
        "total_posts": len(found_posts),
        "posts": [
            {"url": post.url, "date": post.post_date, "snippet": post.snippet}
            for post in found_posts
        ],
    }
