"""Tests for business/poster.html (Issue #4, T3 promo poster).

Checks Acceptance Criteria 1-3 using html.parser + regex only (Python 3.11
stdlib). Tests cannot render HTML/SVG, so they assert on the source: the
required @page rule, Romanian text, a short headline, an audience/benefit
sub-line, an inline <svg> image, the exact call-to-action, the live URL as
both visible text and a link, and the absence of any external resource.
"""
import os
import re
import unittest
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
POSTER = os.path.join(HERE, "..", "business", "poster.html")
APP_JS = os.path.join(HERE, "..", "docs", "app.js")
LIVE_URL = "https://clarnuomandarina.github.io/salvabox-challenge-test/"


class _Collector(HTMLParser):
    """Collect tags, attributes and visible text from the poster."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.attrs_by_tag = {}
        self.html_lang = None
        self.href_values = []
        self.src_values = []
        self._skip_depth = 0  # inside <style>/<script>: not visible text
        self._text_parts = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs_by_tag.setdefault(tag, []).append(dict(attrs))
        d = dict(attrs)
        if tag == "html" and "lang" in d:
            self.html_lang = d["lang"]
        if "href" in d:
            self.href_values.append(d["href"])
        if "src" in d:
            self.src_values.append(d["src"])
        if tag in ("style", "script"):
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._text_parts.append(data)

    @property
    def visible_text(self):
        return re.sub(r"\s+", " ", " ".join(self._text_parts)).strip()


def _load():
    with open(POSTER, "r", encoding="utf-8") as fh:
        raw = fh.read()
    parser = _Collector()
    parser.feed(raw)
    return raw, parser


class PosterFileTest(unittest.TestCase):
    def test_poster_exists_and_nonempty(self):
        self.assertTrue(os.path.isfile(POSTER), "business/poster.html must exist")
        self.assertGreater(os.path.getsize(POSTER), 200, "poster.html is too small")


class AcceptanceCriterion1Test(unittest.TestCase):
    """AC1: A4 portrait page, prints on 1 page, Romanian."""

    def test_a4_portrait_page_rule(self):
        raw, _ = _load()
        # @page { size: A4 portrait; margin: 0 } (tolerant of spacing/order)
        self.assertRegex(
            raw,
            r"@page\s*\{[^}]*size\s*:\s*A4\s+portrait",
            "poster must set @page size: A4 portrait",
        )
        self.assertRegex(
            raw,
            r"@page\s*\{[^}]*margin\s*:\s*0",
            "poster @page must set margin: 0",
        )

    def test_language_is_romanian(self):
        _, p = _load()
        self.assertEqual(p.html_lang, "ro", '<html lang="ro"> is required')


class AcceptanceCriterion2Test(unittest.TestCase):
    """AC2: headline, sub-line, inline SVG, CTA, live URL (text + link)."""

    def test_headline_present_and_short(self):
        _, p = _load()
        h1 = p.attrs_by_tag.get("h1")
        self.assertIsNotNone(h1, "poster needs an <h1> headline message")
        # Extract headline text from the raw source between <h1> and </h1>.
        raw, _ = _load()
        m = re.search(r"<h1\b[^>]*>(.*?)</h1>", raw, re.S | re.I)
        self.assertIsNotNone(m, "could not find <h1>...</h1>")
        text = re.sub(r"<[^>]+>", " ", m.group(1))
        words = [w for w in re.split(r"\s+", text.strip()) if w]
        self.assertTrue(words, "headline must contain words")
        self.assertLessEqual(
            len(words), 12, f"headline must be <= 12 words, got {len(words)}: {words}"
        )

    def test_subline_names_audience_and_benefit(self):
        raw, _ = _load()
        m = re.search(r'<p\b[^>]*class="[^"]*subline[^"]*"[^>]*>(.*?)</p>', raw, re.S | re.I)
        self.assertIsNotNone(m, "poster needs a sub-line paragraph (class 'subline')")
        sub = re.sub(r"<[^>]+>", " ", m.group(1)).lower()
        # audience: students / campus; benefit: reserve a box, save / less waste
        self.assertIn("student", sub, "sub-line must name the audience (studenti)")
        self.assertTrue(
            ("cutie" in sub) or ("rezerv" in sub),
            "sub-line must state the offer/benefit (rezerva o cutie)",
        )

    def test_inline_svg_image(self):
        _, p = _load()
        self.assertIn("svg", p.tags, "poster image must be an inline <svg>")

    def test_call_to_action_exact(self):
        _, p = _load()
        self.assertIn(
            "Incearca acum!",
            p.visible_text,
            "poster must contain the call to action text 'Incearca acum!'",
        )

    def test_live_url_as_visible_text(self):
        _, p = _load()
        self.assertIn(
            LIVE_URL,
            p.visible_text,
            "live URL must appear as visible text on the poster",
        )

    def test_live_url_as_link(self):
        _, p = _load()
        self.assertIn(
            LIVE_URL,
            p.href_values,
            "live URL must be a link (href) on the poster",
        )


class AcceptanceCriterion3Test(unittest.TestCase):
    """AC3: no external resources except the live URL link; no real logos."""

    def test_no_external_src(self):
        _, p = _load()
        for src in p.src_values:
            self.assertFalse(
                re.match(r"https?://", src, re.I),
                f"external src is forbidden: {src}",
            )

    def test_only_allowed_external_href_is_live_url(self):
        _, p = _load()
        for href in p.href_values:
            if re.match(r"https?://", href, re.I):
                self.assertEqual(
                    href,
                    LIVE_URL,
                    f"the only allowed external href is the live URL, got: {href}",
                )

    def test_no_external_css_or_font_imports(self):
        raw, _ = _load()
        self.assertNotRegex(
            raw, r"@import", "no @import of external stylesheets/fonts"
        )
        self.assertNotRegex(
            raw,
            r"url\(\s*['\"]?https?://",
            "no external url() references in CSS",
        )


class PriceMatchesAppTest(unittest.TestCase):
    """The poster's 'de la N lei' price must match the cheapest AVAILABLE box
    in the merged app (docs/app.js). Read-only use of a file outside the
    Issue's Allowed Files is allowed per the Coordinator's [COORD:REVIEW]."""

    def _min_available_price(self):
        with open(APP_JS, "r", encoding="utf-8") as fh:
            src = fh.read()
        m = re.search(r"/\*BOXES_START\*/(.*?)/\*BOXES_END\*/", src, re.S)
        self.assertIsNotNone(
            m, "could not find /*BOXES_START*/.../*BOXES_END*/ in docs/app.js"
        )
        import json

        boxes = json.loads(m.group(1))
        available = [b["price"] for b in boxes if b.get("left", 0) > 0]
        self.assertTrue(available, "docs/app.js has no available boxes (left > 0)")
        return min(available)

    def test_price_matches_min_available_box(self):
        raw, _ = _load()
        m = re.search(r"de la\s+(\d+)\s+lei", raw, re.I)
        self.assertIsNotNone(
            m, "poster must state a 'de la N lei' price"
        )
        poster_price = int(m.group(1))
        expected = self._min_available_price()
        self.assertEqual(
            poster_price,
            expected,
            "poster 'de la N lei' (%d) must equal the cheapest available box "
            "in docs/app.js (%d)" % (poster_price, expected),
        )


if __name__ == "__main__":
    unittest.main()
