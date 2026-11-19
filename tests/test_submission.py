"""Tests for the T4 submission bundle (Issue #5): AI journal, pitch, README.

Stdlib only (Python 3.11): re + html.parser. These tests enforce the contest
limits (skill 7.4) and the Facts Sheet rule (skill 7.8): numbers quoted in the
pitch must match business/strategy.md (the merged source of truth), and the
live URL must appear in both the pitch and the README.

Checks:
  AC1 business/ai_journal.md: <= 450 words; the 4 required headings; exactly 3
      numbered prompts under "## 3 prompturi bune"; >= 1 corrected AI mistake;
      the outside-resources line naming github-multi-agent-skill.txt v1.2.
  AC2 business/pitch.html: EXACTLY 5 <section class="slide">; the live URL and
      a 3-step "Cum testezi" present; every money number in the pitch equals
      the one in business/strategy.md; no external resources.
  AC3 README.md: live URL; a 3-step "how to test"; all 6 deliverable paths;
      the xlsx rebuild command; the verification command; the fake-data note.
"""
import os
import re
import unittest
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
JOURNAL = os.path.join(ROOT, "business", "ai_journal.md")
PITCH = os.path.join(ROOT, "business", "pitch.html")
README = os.path.join(ROOT, "README.md")
STRATEGY = os.path.join(ROOT, "business", "strategy.md")

LIVE_URL = "https://clarnuomandarina.github.io/salvabox-challenge-test/"
VERIFICATION_COMMAND = "python -m unittest discover -s tests -v"
# Numbers strategy.md states in prose; the pitch must quote the SAME ones
# (Facts Sheet consistency, skill 7.8). Revenue/cost totals (18000/6700) live in
# the xlsx, not strategy prose, so they are checked for internal consistency
# separately in test_revenue_cost_result_consistent.
MONEY_NUMBERS = ["4000", "20", "25%", "15", "11300"]
# Model assumptions (from strategy + xlsx Facts Sheet) used to recompute totals.
AVG_PRICE = 15          # RON/cutie
COMMISSION = 0.25       # 25%
BOXES_PER_MONTH = 4000
CAFES = 20
SUBSCRIPTION = 150      # RON/luna per cafe
EXPECTED_REVENUE = 18000
EXPECTED_COST = 6700
EXPECTED_RESULT = 11300
# The 6 deliverable file paths that must be listed in the README.
DELIVERABLE_PATHS = [
    "docs/index.html",
    "docs/app.js",
    "business/strategy.md",
    "business/financial_model.xlsx",
    "business/poster.html",
    "business/ai_journal.md",
    "business/pitch.html",
]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


class _VisibleText(HTMLParser):
    """Collect <section class="slide"> count and visible (non-CSS) text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slide_count = 0
        self.href_values = []
        self.src_values = []
        self._skip = 0
        self._parts = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "section" and "slide" in (d.get("class") or "").split():
            self.slide_count += 1
        if "href" in d:
            self.href_values.append(d["href"])
        if "src" in d:
            self.src_values.append(d["src"])
        if tag in ("style", "script"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0:
            self._parts.append(data)

    @property
    def visible_text(self):
        return re.sub(r"\s+", " ", " ".join(self._parts)).strip()


class FilesExistTest(unittest.TestCase):
    def test_all_three_exist_and_nonempty(self):
        for p in (JOURNAL, PITCH, README):
            self.assertTrue(os.path.isfile(p), f"{p} must exist")
            self.assertGreater(os.path.getsize(p), 200, f"{p} is too small")


class AiJournalTest(unittest.TestCase):
    """AC1: AI journal limits and structure."""

    def test_word_count_under_450(self):
        words = [w for w in re.split(r"\s+", _read(JOURNAL).strip()) if w]
        self.assertLessEqual(
            len(words), 450, f"ai_journal.md must be <= 450 words, got {len(words)}"
        )

    def test_required_headings(self):
        raw = _read(JOURNAL)
        for h in (
            "## Unelte folosite",
            "## 3 prompturi bune",
            "## Greseli AI corectate",
            "## Resurse din afara",
        ):
            self.assertIn(h, raw, f"ai_journal.md must contain heading '{h}'")

    def test_exactly_three_numbered_prompts(self):
        raw = _read(JOURNAL)
        m = re.search(
            r"##\s*3 prompturi bune\s*(.*?)(?:\n##\s|\Z)", raw, re.S
        )
        self.assertIsNotNone(m, "could not find the '## 3 prompturi bune' section")
        section = m.group(1)
        numbered = re.findall(r"(?m)^\s*(\d+)\.\s+\S", section)
        self.assertEqual(
            numbered,
            ["1", "2", "3"],
            f"the prompts section must have exactly 3 numbered prompts, got {numbered}",
        )

    def test_at_least_one_corrected_mistake(self):
        raw = _read(JOURNAL)
        m = re.search(
            r"##\s*Greseli AI corectate\s*(.*?)(?:\n##\s|\Z)", raw, re.S
        )
        self.assertIsNotNone(m, "could not find '## Greseli AI corectate'")
        section = m.group(1).lower()
        # Each corrected mistake shows: how it was checked + the fix.
        self.assertIn("verificat", section, "must show how the AI output was checked")
        self.assertIn("fix", section, "must show the fix")
        bullets = re.findall(r"(?m)^\s*-\s+\S", section)
        self.assertGreaterEqual(
            len(bullets), 1, "must list at least one corrected AI mistake"
        )

    def test_outside_resources_line(self):
        raw = _read(JOURNAL)
        self.assertRegex(
            raw,
            r"github-multi-agent-skill\.txt\s*v1\.2",
            "the outside-resources section must name github-multi-agent-skill.txt v1.2",
        )


class PitchTest(unittest.TestCase):
    """AC2: pitch structure, live URL, how-to-test, number consistency."""

    def _parse(self):
        p = _VisibleText()
        p.feed(_read(PITCH))
        return p

    def test_exactly_five_slides(self):
        raw = _read(PITCH)
        count = len(re.findall(r'<section\b[^>]*class="[^"]*\bslide\b[^"]*"', raw))
        self.assertEqual(count, 5, f"pitch must have EXACTLY 5 slides, got {count}")
        # Cross-check via the HTML parser.
        self.assertEqual(self._parse().slide_count, 5)

    def test_one_slide_per_printed_page(self):
        raw = _read(PITCH)
        self.assertRegex(
            raw,
            r"@page\s*\{[^}]*size\s*:\s*1280px\s+720px",
            "pitch @page must set size: 1280px 720px (16:9)",
        )
        self.assertRegex(
            raw, r"@page\s*\{[^}]*margin\s*:\s*0", "pitch @page must set margin: 0"
        )
        self.assertRegex(
            raw,
            r"break-after\s*:\s*page",
            "slides must break-after: page (one slide per printed page)",
        )

    def test_live_url_present(self):
        self.assertIn(LIVE_URL, self._parse().visible_text,
                      "pitch must show the live URL")

    def test_how_to_test_three_steps(self):
        p = self._parse()
        self.assertRegex(
            p.visible_text.lower(),
            r"cum testezi",
            "pitch must include a 'Cum testezi' section",
        )
        raw = _read(PITCH)
        m = re.search(r"<ol\b[^>]*>(.*?)</ol>", raw, re.S | re.I)
        self.assertIsNotNone(m, "pitch 'how to test' must be an ordered <ol> list")
        steps = re.findall(r"<li\b", m.group(1), re.I)
        self.assertEqual(len(steps), 3, f"'Cum testezi' must have 3 steps, got {len(steps)}")

    def test_numbers_match_strategy(self):
        pitch_text = self._parse().visible_text
        strat = _read(STRATEGY)
        for n in MONEY_NUMBERS:
            self.assertIn(n, strat, f"strategy.md must contain the number {n}")
            self.assertIn(
                n, pitch_text, f"pitch must quote the same number {n} as strategy.md"
            )

    def test_revenue_cost_result_consistent(self):
        """The pitch's revenue/cost/result (from the xlsx Facts Sheet) must be
        internally consistent and equal the result strategy.md states."""
        commission = AVG_PRICE * COMMISSION * BOXES_PER_MONTH  # 15000
        subscriptions = CAFES * SUBSCRIPTION                   # 3000
        revenue = commission + subscriptions                   # 18000
        self.assertEqual(revenue, EXPECTED_REVENUE)
        self.assertEqual(revenue - EXPECTED_COST, EXPECTED_RESULT)  # 18000-6700=11300
        self.assertIn(
            str(EXPECTED_RESULT), _read(STRATEGY),
            "strategy.md must state the monthly result 11300",
        )
        pitch_text = self._parse().visible_text
        for n in (str(EXPECTED_REVENUE), str(EXPECTED_COST), str(EXPECTED_RESULT)):
            self.assertIn(n, pitch_text, f"pitch must show the number {n}")

    def test_no_external_resources(self):
        p = self._parse()
        for ref in p.src_values + p.href_values:
            if re.match(r"https?://", ref, re.I):
                self.assertEqual(
                    ref, LIVE_URL,
                    f"the only allowed external URL in the pitch is the live URL, got {ref}",
                )
        self.assertNotRegex(_read(PITCH), r"@import", "no external @import in the pitch")
        self.assertNotRegex(
            _read(PITCH), r"url\(\s*['\"]?https?://", "no external url() in the pitch CSS"
        )


class ReadmeTest(unittest.TestCase):
    """AC3: README has the live URL, how-to-test, deliverables, rebuild + verify."""

    def test_live_url(self):
        self.assertIn(LIVE_URL, _read(README), "README must show the live URL")

    def test_three_step_how_to_test(self):
        raw = _read(README).lower()
        self.assertIn("3 pasi", raw, "README must describe how to test in 3 steps")
        self.assertRegex(raw, r"(?m)^1\.\s", "README how-to-test needs numbered step 1")
        self.assertRegex(raw, r"(?m)^2\.\s", "README how-to-test needs numbered step 2")
        self.assertRegex(raw, r"(?m)^3\.\s", "README how-to-test needs numbered step 3")

    def test_lists_six_deliverable_paths(self):
        raw = _read(README)
        for path in DELIVERABLE_PATHS:
            self.assertIn(path, raw, f"README must list deliverable path {path}")

    def test_xlsx_rebuild_command(self):
        self.assertIn(
            "python tools/build_model.py",
            _read(README),
            "README must show how to rebuild the xlsx",
        )

    def test_verification_command(self):
        self.assertIn(
            VERIFICATION_COMMAND, _read(README), "README must show the verification command"
        )

    def test_fake_data_note(self):
        raw = _read(README).lower()
        self.assertTrue(
            ("date false" in raw) or ("date fictive" in raw),
            "README must carry a fake-data note",
        )


if __name__ == "__main__":
    unittest.main()
