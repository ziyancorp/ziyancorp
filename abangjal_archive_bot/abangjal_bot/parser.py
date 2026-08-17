from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse


URL_RE = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
LABEL_RE = re.compile(r"^\s*(nama produk|judul|deskripsi|shopee|tiktok(?: shop)?|tokopedia|lazada|status)\s*:\s*(.*?)\s*$", re.IGNORECASE | re.MULTILINE)


@dataclass
class ProductDraft:
    title: str
    description: str
    shopee_url: str | None
    tiktok_url: str | None
    other_links: list[str]


def clean_url(url: str) -> str:
    return url.rstrip(".,;)>]")


def parse_caption(text: str) -> ProductDraft:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    labels: dict[str, str] = {}
    free_text: list[str] = []
    for line in lines:
        match = LABEL_RE.match(line)
        if match:
            key = match.group(1).lower().replace(" ", "_")
            labels[key] = match.group(2).strip()
        else:
            free_text.append(line)

    urls = [clean_url(url) for url in URL_RE.findall(text)]
    shopee = labels.get("shopee")
    tiktok = labels.get("tiktok") or labels.get("tiktok_shop")
    other: list[str] = []
    for url in urls:
        host = urlparse(url).netloc.lower()
        if "shopee" in host and not shopee:
            shopee = url
        elif ("tiktok" in host or "tiktokshop" in host) and not tiktok:
            tiktok = url
        elif url not in {shopee, tiktok}:
            other.append(url)

    title = labels.get("nama_produk") or labels.get("judul") or (free_text[0] if free_text else "Tanpa judul")
    description = labels.get("deskripsi") or " ".join(free_text[1:] if free_text and free_text[0] == title else free_text)
    if not description:
        description = title
    return ProductDraft(title=title[:500], description=description[:5000], shopee_url=shopee, tiktok_url=tiktok, other_links=other)


def safe_name(value: str, max_length: int = 80) -> str:
    value = re.sub(r"[^\w\- ]+", "", value, flags=re.UNICODE).strip().replace(" ", "-")
    return (value or "untitled")[:max_length]
