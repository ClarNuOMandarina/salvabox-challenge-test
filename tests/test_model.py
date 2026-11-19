"""Tests for the SalvaBox financial model (Issue #3 / T2).

Checks, per the Acceptance Criteria:
  - tools/build_model.py rebuilds a byte-identical xlsx into a temp dir
    (compared to the committed business/financial_model.xlsx).
  - the xlsx is a valid OOXML package (all required parts present).
  - every Costuri/Venituri/Rezultat value cell holds an <f> formula.
  - the formulas, evaluated independently in Python, give the monthly
    result that strategy.md quotes.
  - strategy.md has exactly the required headings, stays <= 450 words,
    and quotes the box price, the commission and the monthly result.

Python 3.11 standard library only.
"""
import importlib.util
import os
import re
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDER = os.path.join(ROOT, "tools", "build_model.py")
XLSX = os.path.join(ROOT, "business", "financial_model.xlsx")
STRATEGY = os.path.join(ROOT, "business", "strategy.md")

REQUIRED_PARTS = [
    "[Content_Types].xml",
    "_rels/.rels",
    "xl/workbook.xml",
    "xl/_rels/workbook.xml.rels",
    "xl/worksheets/sheet1.xml",
    "xl/styles.xml",
]

# Value cells that MUST carry a formula (Venituri/Costuri/Rezultat).
FORMULA_CELLS = [
    "B16", "B17", "B18", "B19",   # Venituri
    "B22", "B23", "B24", "B25", "B26",  # Costuri
    "B29",  # Rezultat
]


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_model", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ModelXlsxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = _load_builder()
        with open(XLSX, "rb") as fh:
            cls.committed_bytes = fh.read()
        with zipfile.ZipFile(XLSX) as zf:
            cls.sheet = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
            cls.names = zf.namelist()
            cls.workbook = zf.read("xl/workbook.xml").decode("utf-8")

    def test_required_parts_present(self):
        for part in REQUIRED_PARTS:
            self.assertIn(part, self.names, f"missing OOXML part {part}")

    def test_valid_zip(self):
        with zipfile.ZipFile(XLSX) as zf:
            self.assertIsNone(zf.testzip(), "corrupt zip entry")

    def test_full_calc_on_load(self):
        self.assertIn('fullCalcOnLoad="1"', self.workbook)

    def test_single_sheet_named_model(self):
        self.assertIn('name="Model"', self.workbook)

    def test_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "financial_model.xlsx")
            self.builder.build(out)
            with open(out, "rb") as fh:
                rebuilt = fh.read()
        self.assertEqual(
            rebuilt, self.committed_bytes,
            "committed xlsx is not byte-identical to a fresh build; "
            "re-run tools/build_model.py and commit the result")

    def test_value_cells_are_formulas(self):
        for ref in FORMULA_CELLS:
            pat = re.compile(
                r'<c r="%s"[^>]*>\s*<f>[^<]+</f>' % re.escape(ref))
            self.assertRegex(
                self.sheet, pat,
                f"cell {ref} must hold an <f> formula, not a typed number")

    def test_formulas_have_cached_values(self):
        # A cached <v> next to each <f> so non-recalc viewers show numbers.
        for ref in FORMULA_CELLS:
            pat = re.compile(
                r'<c r="%s"[^>]*>\s*<f>[^<]+</f>\s*<v>[^<]+</v>'
                % re.escape(ref))
            self.assertRegex(
                self.sheet, pat, f"cell {ref} missing cached <v> value")

    def test_assumptions_are_typed_numbers(self):
        # Assumption cells must NOT carry a formula.
        for ref in ("B4", "B5", "B6", "B7", "B8"):
            pat = re.compile(r'<c r="%s"[^>]*>\s*<f>' % re.escape(ref))
            self.assertNotRegex(
                self.sheet, pat, f"assumption {ref} must be a typed number")

    def test_result_matches_independent_python(self):
        values = self.builder.compute_values()
        # Independent recomputation of the result from the assumptions.
        # Money flow: cafeneaua incaseaza GMV; SalvaBox NU proceseaza plati,
        # deci nu exista taxa pe GMV. B9 este contabilitate + facturare (cost fix).
        a = self.builder.ASSUMPTIONS
        revenue = a["B4"] * a["B5"] * a["B6"] + a["B7"] * a["B8"]
        costs = a["B12"] + a["B13"] + a["B9"] + a["B10"] * a["B11"]
        expected = revenue - costs
        self.assertAlmostEqual(values["B29"], expected, places=6)

    def test_result_matches_strategy_quote(self):
        values = self.builder.compute_values()
        result = int(round(values["B29"]))
        with open(STRATEGY, encoding="utf-8") as fh:
            text = fh.read()
        digits = {int(m.replace(".", "").replace(",", ""))
                  for m in re.findall(r"\d[\d.,]*", text)}
        self.assertIn(
            result, digits,
            f"strategy.md must quote the monthly result {result} RON/luna")


class StrategyTest(unittest.TestCase):
    REQUIRED_HEADINGS = [
        "## Problema",
        "## Public",
        "## Solutia",
        "## Cum aducem clienti",
        "## 3 pasi de pus in practica",
    ]

    @classmethod
    def setUpClass(cls):
        with open(STRATEGY, encoding="utf-8") as fh:
            cls.text = fh.read()

    def test_headings_present_in_order(self):
        last = -1
        for h in self.REQUIRED_HEADINGS:
            idx = self.text.find("\n" + h) if self.text.find("\n" + h) >= 0 \
                else (0 if self.text.startswith(h) else -1)
            self.assertGreaterEqual(
                idx, 0, f"missing heading {h!r}")
            self.assertGreater(idx, last, f"heading {h!r} out of order")
            last = idx

    def test_word_count_under_limit(self):
        words = re.findall(r"\S+", self.text)
        self.assertLessEqual(
            len(words), 450, f"strategy has {len(words)} words (max 450)")

    def test_exactly_three_steps(self):
        # The "3 pasi" section is a numbered list of exactly 3 items.
        tail = self.text.split("## 3 pasi de pus in practica", 1)[1]
        steps = re.findall(r"(?m)^\s*\d+\.\s+\S", tail)
        self.assertEqual(
            len(steps), 3, f"expected exactly 3 numbered steps, got {len(steps)}")

    def test_quotes_price_and_commission(self):
        builder_spec = importlib.util.spec_from_file_location(
            "build_model2", BUILDER)
        mod = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(mod)
        price = int(mod.ASSUMPTIONS["B4"])
        commission_pct = int(round(mod.ASSUMPTIONS["B5"] * 100))
        digits = {int(m.replace(".", "").replace(",", ""))
                  for m in re.findall(r"\d[\d.,]*", self.text)}
        self.assertIn(price, digits, "strategy must quote the box price")
        self.assertIn(commission_pct, digits,
                      "strategy must quote the commission percentage")


if __name__ == "__main__":
    unittest.main()
