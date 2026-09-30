"""RSS regression checks; run with python3 -m unittest discover -s tests -v."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts import generate_feed as feed


class Links(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "link"):
            self.links.append((tag, dict(attrs)))


class FeedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "blog").mkdir()

    def write_blog(self, cards):
        (self.root / "blog/index.html").write_text("".join(
            f'<article class="product-card"><h3><a href="/blog/{slug}.html">{title}</a></h3>'
            f'<p class="one-liner">{summary}</p><div class="meta"><span>{date}</span>'
            ' · <span>Audio available</span></div></article>'
            for slug, title, summary, date in cards), encoding="utf-8")
        for slug, *_ in cards:
            (self.root / f"blog/{slug}.html").write_text(
                f'<link rel="canonical" href="{feed.SITE}/blog/{slug}.html">', encoding="utf-8")

    def test_added_posts_sort_by_date_with_stable_ties(self):
        cards = [("old", "Old", "Summary", "February 15, 2026")]
        self.write_blog(cards)
        original = feed.read_posts(self.root)[0]
        cards += [("z-new", "New", "Summary", "September 30, 2026"),
                  ("a-new", "Also new", "Summary", "September 30, 2026")]
        self.write_blog(cards)
        posts = feed.read_posts(self.root)
        self.assertEqual([p.title for p in posts], ["Also new", "New", "Old"])
        self.assertEqual(posts[-1], original)
        self.assertEqual(feed.render_feed(posts), feed.render_feed(feed.read_posts(self.root)))
        items = ET.fromstring(feed.render_feed(posts)).findall("channel/item")
        self.assertEqual(items[-1].findtext("guid"), original.url)
        self.assertEqual(parsedate_to_datetime(items[0].findtext("pubDate")),
                         datetime(2026, 9, 30, tzinfo=timezone.utc))

    def test_entities_unicode_nested_markup_and_html_description(self):
        self.write_blog([("escaping", 'A &amp; <em>B</em> &lt; C — “test”',
                          'Read &lt;code&gt; &amp; enjoy <br/>]]> café.', "March 1, 2026")])
        post = feed.read_posts(self.root)[0]
        item = ET.fromstring(feed.render_feed([post])).find("channel/item")
        self.assertEqual(item.findtext("title"), 'A & B < C — “test”')
        self.assertEqual(unescape(item.findtext("description")), 'Read <code> & enjoy ]]> café.')
        self.assertIn('&lt;code&gt;', item.findtext("description"))

    def test_rejects_incomplete_invalid_or_duplicate_cards(self):
        for card in [("test", "", "Summary", "March 1, 2026"),
                     ("test", "Title", "", "March 1, 2026"),
                     ("test", "Title", "Summary", "February 30, 2026"),
                     ("test", "Title", "Summary", "Yesterday")]:
            with self.subTest(card=card):
                self.write_blog([card])
                with self.assertRaises(ValueError):
                    feed.read_posts(self.root)
        card = ("test", "Title", "Summary", "March 1, 2026")
        self.write_blog([card, card])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            feed.read_posts(self.root)

    def test_rejects_missing_page_and_wrong_canonical(self):
        self.write_blog([("test", "Title", "Summary", "March 1, 2026")])
        page = self.root / "blog/test.html"
        page.write_text('<link rel="canonical" href="https://example.com/test">')
        with self.assertRaisesRegex(ValueError, "canonical"):
            feed.read_posts(self.root)
        page.unlink()
        with self.assertRaises(FileNotFoundError):
            feed.read_posts(self.root)

    def test_check_detects_new_and_edited_articles_without_writing(self):
        cards = [("test", "Title", "Summary", "March 1, 2026")]
        self.write_blog(cards)
        with patch.object(feed, "ROOT", self.root), patch.object(sys, "argv", ["generate_feed.py"]):
            feed.main()
        original = (self.root / "feed.xml").read_bytes()
        for changed in [[("test", "Title", "Edited summary", "March 1, 2026")],
                        cards + [("new", "New", "Summary", "March 2, 2026")]]:
            self.write_blog(changed)
            with patch.object(feed, "ROOT", self.root), patch.object(sys, "argv", ["generate_feed.py", "--check"]):
                with self.assertRaises(SystemExit) as error:
                    feed.main()
                self.assertEqual(error.exception.code, 1)
            self.assertEqual((self.root / "feed.xml").read_bytes(), original)

    def test_committed_feed_matches_published_articles(self):
        posts = feed.read_posts(feed.ROOT)
        committed = (feed.ROOT / "feed.xml").read_bytes()
        self.assertEqual(committed, feed.render_feed(posts))
        rss = ET.fromstring(committed)
        self.assertEqual(rss.attrib, {"version": "2.0"})
        channel = rss.find("channel")
        for field in ("title", "link", "description", "language"):
            self.assertTrue(channel.findtext(field))
        self.assertEqual(channel.find(f"{{{feed.ATOM}}}link").attrib,
                         {"href": feed.SITE + "/feed.xml", "rel": "self", "type": "application/rss+xml"})
        items = channel.findall("item")
        self.assertEqual(len(items), len(posts))
        self.assertEqual(len({item.findtext("guid") for item in items}), len(posts))
        for item, post in zip(items, posts):
            self.assertEqual(item.findtext("link"), post.url)
            self.assertEqual(item.findtext("guid"), post.url)
            self.assertEqual(item.find("guid").get("isPermaLink"), "true")
            self.assertEqual(parsedate_to_datetime(item.findtext("pubDate")), post.published)
            self.assertEqual(unescape(item.findtext("description")), post.description)
        subprocess.run([sys.executable, str(feed.ROOT / "scripts/generate_feed.py"), "--check"], check=True)

    def test_feed_discovery_and_subscription_links(self):
        paths = [feed.ROOT / "index.html", feed.ROOT / "about.html",
                 *sorted((feed.ROOT / "blog").glob("*.html"))]
        for path in paths:
            with self.subTest(page=path.name):
                links = Links(path.read_text(encoding="utf-8")).links
                self.assertEqual(sum(tag == "link" and attrs.get("rel") == "alternate"
                                     and attrs.get("type") == "application/rss+xml"
                                     and attrs.get("href") == feed.SITE + "/feed.xml"
                                     for tag, attrs in links), 1)
                self.assertTrue(any(tag == "a" and attrs.get("href") == "/feed.xml"
                                    for tag, attrs in links))


if __name__ == "__main__":
    unittest.main()
