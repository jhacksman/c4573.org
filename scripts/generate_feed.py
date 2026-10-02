#!/usr/bin/env python3
"""Generate RSS from the published cards in blog/index.html (standard library only)."""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://c4573.org"
ATOM = "http://www.w3.org/2005/Atom"
MONTHS = "January February March April May June July August September October November December".split()
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass(frozen=True)
class Post:
    title: str
    url: str
    description: str
    published: datetime


class BlogIndex(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards = []
        self.card = None
        self.capture = None
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.capture:
            if tag not in VOID_TAGS:
                self.depth += 1
            if self.capture == "title" and tag == "a":
                self.card["href"] = attrs.get("href", "")
            return
        classes = attrs.get("class", "").split()
        if tag == "article" and "product-card" in classes:
            if self.card is not None:
                raise ValueError("Nested blog cards are not supported")
            self.card = {}
        if self.card is not None:
            field = None
            if tag == "h3":
                field = "title"
            elif tag == "p" and "one-liner" in classes:
                field = "description"
            elif tag == "div" and "meta" in classes:
                field = "date"
            if field:
                self.capture, self.depth, self.parts = field, 1, []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if self.capture:
            self.depth -= 1
            if self.depth == 0:
                self.card[self.capture] = " ".join("".join(self.parts).split())
                self.capture = None
        elif tag == "article" and self.card is not None:
            self.cards.append(self.card)
            self.card = None

    def handle_data(self, data):
        if self.capture:
            self.parts.append(data)


class CanonicalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.urls.append(attrs.get("href"))


def read_posts(root):
    index = BlogIndex()
    index.feed((root / "blog/index.html").read_text(encoding="utf-8"))
    if not index.cards or index.card is not None:
        raise ValueError("Blog index must contain complete published article cards")
    posts, seen = [], set()
    for card in index.cards:
        if any(not card.get(key) for key in ("title", "href", "description", "date")):
            raise ValueError(f"Incomplete blog card: {card}")
        href = card["href"]
        if not re.fullmatch(r"/blog/[a-z0-9-]+\.html", href):
            raise ValueError(f"Unexpected article path: {href}")
        url = SITE + href
        canonical = CanonicalLinks()
        canonical.feed((root / href.lstrip("/")).read_text(encoding="utf-8"))
        if canonical.urls != [url]:
            raise ValueError(f"Expected one canonical link to {url}: {canonical.urls}")
        if url in seen:
            raise ValueError(f"Duplicate article: {url}")
        seen.add(url)
        date = card["date"].split("·", 1)[0].strip()
        match = re.fullmatch(r"([A-Za-z]+) (\d{1,2}), (\d{4})", date)
        if not match or match[1] not in MONTHS:
            raise ValueError(f"Invalid publication date for {url}: {date}")
        published = datetime(int(match[3]), MONTHS.index(match[1]) + 1,
                             int(match[2]), tzinfo=timezone.utc)
        posts.append(Post(card["title"], url, card["description"], published))
    return sorted(posts, key=lambda post: (-post.published.timestamp(), post.url))


def render_feed(posts):
    ET.register_namespace("atom", ATOM)
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    for name, value in (("title", "c4573.org — Blog"), ("link", SITE + "/blog/"),
                        ("description", "Essays on technofeudalism, acceleration, and owning your tools."),
                        ("language", "en")):
        ET.SubElement(channel, name).text = value
    ET.SubElement(channel, f"{{{ATOM}}}link", {
        "href": SITE + "/feed.xml", "rel": "self", "type": "application/rss+xml"})
    for post in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post.title
        ET.SubElement(item, "link").text = post.url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = post.url
        ET.SubElement(item, "pubDate").text = format_datetime(post.published, usegmt=True)
        # RSS descriptions are HTML: escape plain text before XML serialization.
        ET.SubElement(item, "description").text = escape(post.description, quote=False)
    ET.indent(rss, space="  ")
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True) + b"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if feed.xml needs regeneration")
    args = parser.parse_args()
    try:
        output = render_feed(read_posts(ROOT))
        target = ROOT / "feed.xml"
        if args.check:
            if not target.exists() or target.read_bytes() != output:
                parser.exit(1, "feed.xml is stale; run python3 scripts/generate_feed.py\n")
            print("feed.xml is up to date")
        else:
            target.write_bytes(output)
            print("Generated feed.xml")
    except (ValueError, OSError) as error:
        parser.exit(1, f"Cannot generate feed: {error}\n")


if __name__ == "__main__":
    main()
