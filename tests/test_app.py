import json
import os
import re
import unittest
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


def read(name):
    with open(os.path.join(DOCS, name), "r", encoding="utf-8") as f:
        return f.read()


class FormParser(HTMLParser):
    """Collect element ids, labels (for=), input/select tags, and resource links."""

    def __init__(self):
        super().__init__()
        self.ids = set()
        self.label_for = set()
        self.inputs = []          # list of (tag, id)
        self.html_lang = None
        self.has_viewport = False
        self.title_parts = []
        self._in_title = False
        self.linked_css = set()
        self.linked_js = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html" and "lang" in a:
            self.html_lang = a["lang"]
        if tag == "meta" and a.get("name") == "viewport":
            self.has_viewport = True
        if tag == "title":
            self._in_title = True
        if tag == "label" and "for" in a:
            self.label_for.add(a["for"])
        if tag in ("input", "select", "textarea"):
            self.inputs.append((tag, a.get("id")))
        if tag == "link" and a.get("rel") == "stylesheet" and a.get("href"):
            self.linked_css.add(a["href"])
        if tag == "script" and a.get("src"):
            self.linked_js.add(a["src"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)


def extract_boxes(js_text):
    m = re.search(r"/\*BOXES_START\*/(.*?)/\*BOXES_END\*/", js_text, re.DOTALL)
    if not m:
        raise AssertionError("BOXES markers not found in app.js")
    return json.loads(m.group(1).strip())


def filter_boxes(boxes, max_price, diet):
    """Python mirror of the AC3 rule in app.js."""
    limit = float(max_price)
    out = []
    for b in boxes:
        if b["left"] <= 0:
            continue
        if b["price"] > limit:
            continue
        if diet == "oricare":
            ok = True
        elif diet == "vegetarian":
            ok = b["diet"] in ("vegetarian", "vegan")
        elif diet == "vegan":
            ok = b["diet"] == "vegan"
        else:
            ok = False
        if ok:
            out.append(b)
    out.sort(key=lambda b: b["price"])
    return out


class TestIndexHtml(unittest.TestCase):
    """Acceptance Criterion 1 + 6 (HTML structure, labels, no external resources)."""

    @classmethod
    def setUpClass(cls):
        cls.html = read("index.html")
        p = FormParser()
        p.feed(cls.html)
        cls.p = p

    def test_lang_ro(self):
        self.assertEqual(self.p.html_lang, "ro")

    def test_viewport(self):
        self.assertTrue(self.p.has_viewport, "missing meta viewport")

    def test_title(self):
        self.assertIn("SalvaBox", "".join(self.p.title_parts))

    def test_required_ids(self):
        for req in ("maxPrice", "diet", "results", "emptyState", "reservation"):
            self.assertIn(req, self.p.ids, "missing element id #%s" % req)

    def test_inputs_labelled(self):
        for tag, _id in self.p.inputs:
            self.assertIsNotNone(_id, "an %s has no id, cannot be labelled" % tag)
            self.assertIn(_id, self.p.label_for, "input #%s has no <label for>" % _id)

    def test_links_relative(self):
        self.assertIn("style.css", self.p.linked_css)
        self.assertIn("app.js", self.p.linked_js)
        for href in self.p.linked_css | self.p.linked_js:
            self.assertFalse(href.startswith(("http://", "https://", "//")),
                             "resource %s is not relative" % href)

    def test_no_external_resources(self):
        # AC6: no http:// or external https:// resources anywhere in docs HTML.
        self.assertNotIn("http://", self.html)
        self.assertNotIn("https://", self.html)


class TestAppJs(unittest.TestCase):
    """Acceptance Criterion 2 + 3 (data shape, pure filter rule, demo case)."""

    @classmethod
    def setUpClass(cls):
        cls.js = read("app.js")
        cls.boxes = extract_boxes(cls.js)

    def test_no_external_resources_in_js(self):
        self.assertNotIn("http://", self.js)
        self.assertNotIn("https://", self.js)

    def test_filter_function_exists(self):
        self.assertRegex(self.js, r"function\s+filterBoxes\s*\(")

    def test_boxes_shape(self):
        self.assertGreaterEqual(len(self.boxes), 6, "need >= 6 boxes")
        valid_diets = {"vegan", "vegetarian", "omnivor"}
        zero_left_seen = False
        for b in self.boxes:
            for key in ("id", "cafeteria", "dish", "diet", "price", "pickup", "left"):
                self.assertIn(key, b, "box missing key %s" % key)
            self.assertIn(b["diet"], valid_diets, "bad diet %s" % b["diet"])
            self.assertGreaterEqual(b["price"], 0)
            self.assertGreaterEqual(b["left"], 0)
            if b["left"] == 0:
                zero_left_seen = True
        self.assertTrue(zero_left_seen, "need at least one box with left: 0")

    def test_demo_case(self):
        # AC5 demo: maxPrice=15, diet=vegetarian -> >= 2 boxes.
        res = filter_boxes(self.boxes, 15, "vegetarian")
        self.assertGreaterEqual(len(res), 2, "demo case must return >= 2 boxes")
        prices = [b["price"] for b in res]
        self.assertEqual(prices, sorted(prices), "results must be sorted ascending")
        for b in res:
            self.assertLessEqual(b["price"], 15)
            self.assertGreater(b["left"], 0)
            self.assertIn(b["diet"], ("vegetarian", "vegan"))

    def test_filter_rules(self):
        # oricare keeps all diets (that pass price/left); vegan keeps vegan only.
        all_boxes = filter_boxes(self.boxes, 1000, "oricare")
        available = [b for b in self.boxes if b["left"] > 0]
        self.assertEqual(len(all_boxes), len(available))
        vegan_only = filter_boxes(self.boxes, 1000, "vegan")
        self.assertTrue(all(b["diet"] == "vegan" for b in vegan_only))
        # left == 0 is always excluded
        self.assertTrue(all(b["left"] > 0 for b in all_boxes))


if __name__ == "__main__":
    unittest.main()
