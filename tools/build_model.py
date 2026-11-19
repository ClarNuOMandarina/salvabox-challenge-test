#!/usr/bin/env python3
"""Build business/financial_model.xlsx for SalvaBox using only the Python
3.11 standard library (zipfile), no openpyxl.

The workbook has a single sheet "Model" with four sections:
  Ipoteze  (assumptions, typed numbers)
  Costuri  (costs, every value is a formula)
  Venituri (revenues, every value is a formula)
  Rezultat (result, a formula)

Every cost/revenue/result value cell carries an XML <f> formula. A cached
<v> value (computed by the pure-Python evaluator below) is stored next to
each <f> so viewers that do not recalculate still show the numbers. The
workbook sets fullCalcOnLoad="1" so Excel/Sheets recompute on open.

Output is byte-identical on every run: all zip entries use a fixed
timestamp and fixed order.

Toate datele sunt fictive (fake data only), unitatile sunt RON/luna.
"""
import os
import sys
import zipfile

# --------------------------------------------------------------------------
# Model definition. Each row is (cell_ref, label, kind, value_or_formula).
#   kind "num"     -> typed number assumption (Ipoteze)
#   kind "formula" -> value cell with an XML formula (Costuri/Venituri/Rezultat)
#   kind "head"    -> section heading (text only, column A)
# Column A holds labels (inline strings); column B holds numbers/formulas.
# --------------------------------------------------------------------------

# Assumptions (typed numbers). Keyed by cell ref in column B.
ASSUMPTIONS = {
    "B4": 15,     # Pret pe cutie (RON/cutie)
    "B5": 0.25,   # Comision partener (fractie)
    "B6": 4000,   # Cutii vandute pe luna (cutii/luna)
    "B7": 20,     # Cafenele abonate (nr)
    "B8": 150,    # Abonament cafenea (RON/luna)
    "B9": 0.03,   # Taxa procesare plati (fractie din GMV)
    "B10": 6,     # Ambasadori studenti (nr)
    "B11": 500,   # Plata pe ambasador (RON/luna)
    "B12": 400,   # Hosting (RON/luna)
    "B13": 2500,  # Marketing (RON/luna)
}

# Rows in display order: (ref_or_None, label, kind, formula_or_None)
ROWS = [
    (None, "Model financiar SalvaBox (RON/luna) - date fictive", "head", None),
    (None, "", "head", None),
    (None, "Ipoteze", "head", None),
    ("B4", "Pret pe cutie (RON/cutie)", "num", None),
    ("B5", "Comision partener (fractie)", "num", None),
    ("B6", "Cutii vandute pe luna (cutii/luna)", "num", None),
    ("B7", "Cafenele abonate (nr)", "num", None),
    ("B8", "Abonament cafenea (RON/luna)", "num", None),
    ("B9", "Taxa procesare plati (fractie din GMV)", "num", None),
    ("B10", "Ambasadori studenti (nr)", "num", None),
    ("B11", "Plata pe ambasador (RON/luna)", "num", None),
    ("B12", "Hosting (RON/luna)", "num", None),
    ("B13", "Marketing (RON/luna)", "num", None),
    (None, "", "head", None),
    (None, "Venituri", "head", None),
    ("B16", "GMV cutii (RON/luna)", "formula", "B4*B6"),
    ("B17", "Venit din comision (RON/luna)", "formula", "B4*B5*B6"),
    ("B18", "Venit din abonamente (RON/luna)", "formula", "B7*B8"),
    ("B19", "Venituri totale (RON/luna)", "formula", "SUM(B17:B18)"),
    (None, "", "head", None),
    (None, "Costuri", "head", None),
    ("B22", "Hosting (RON/luna)", "formula", "B12"),
    ("B23", "Marketing (RON/luna)", "formula", "B13"),
    ("B24", "Taxe procesare plati (RON/luna)", "formula", "B16*B9"),
    ("B25", "Ambasadori studenti (RON/luna)", "formula", "B10*B11"),
    ("B26", "Costuri totale (RON/luna)", "formula", "SUM(B22:B25)"),
    (None, "", "head", None),
    (None, "Rezultat", "head", None),
    ("B29", "Rezultat lunar (profit) (RON/luna)", "formula", "B19-B26"),
]

FORMULAS = {ref: f for (ref, _lbl, kind, f) in ROWS if kind == "formula"}


# --------------------------------------------------------------------------
# Pure-Python formula evaluator (cell refs, + - * /, SUM ranges).
# Used to cache <v> values and to let the test recompute independently.
# --------------------------------------------------------------------------
def _col_to_idx(col):
    idx = 0
    for ch in col:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx


def _split_ref(ref):
    i = 0
    while i < len(ref) and ref[i].isalpha():
        i += 1
    return ref[:i], int(ref[i:])


def _expand_range(rng):
    start, end = rng.split(":")
    c1, r1 = _split_ref(start)
    c2, r2 = _split_ref(end)
    ci1, ci2 = _col_to_idx(c1), _col_to_idx(c2)
    refs = []
    for ci in range(min(ci1, ci2), max(ci1, ci2) + 1):
        col = chr(ord("A") + ci - 1)  # single-letter cols are enough here
        for r in range(min(r1, r2), max(r1, r2) + 1):
            refs.append(f"{col}{r}")
    return refs


def evaluate(cells):
    """cells: {ref: ('num', number)} or {ref: ('formula', formula_str)}.
    Returns {ref: float} with every formula resolved. Supports cell refs,
    + - * / ( ), and SUM(range)."""
    resolved = {}

    def val(ref):
        if ref in resolved:
            return resolved[ref]
        kind, payload = cells[ref]
        if kind == "num":
            resolved[ref] = float(payload)
            return resolved[ref]
        resolved[ref] = _eval_formula(payload)
        return resolved[ref]

    def _eval_formula(expr):
        expr = expr.strip()
        # Resolve SUM(range) first.
        while "SUM(" in expr:
            start = expr.index("SUM(")
            depth = 0
            j = start + 4
            while j < len(expr):
                if expr[j] == "(":
                    depth += 1
                elif expr[j] == ")":
                    if depth == 0:
                        break
                    depth -= 1
                j += 1
            inner = expr[start + 4:j]
            total = sum(val(r) for r in _expand_range(inner))
            expr = expr[:start] + repr(total) + expr[j + 1:]
        # Replace remaining cell refs with their values.
        out = []
        i = 0
        while i < len(expr):
            ch = expr[i]
            if ch.isalpha():
                k = i
                while k < len(expr) and (expr[k].isalpha() or expr[k].isdigit()):
                    k += 1
                token = expr[i:k]
                out.append(repr(val(token)))
                i = k
            else:
                out.append(ch)
                i += 1
        safe = "".join(out)
        allowed = set("0123456789.+-*/() eE")
        if not set(safe) <= allowed:
            raise ValueError(f"unsafe token in formula: {expr!r}")
        return float(eval(safe, {"__builtins__": {}}, {}))

    for ref in cells:
        val(ref)
    return resolved


def compute_values():
    cells = {ref: ("num", v) for ref, v in ASSUMPTIONS.items()}
    for ref, f in FORMULAS.items():
        cells[ref] = ("formula", f)
    return evaluate(cells)


def _fmt(v):
    """Render a cached numeric value compactly (int when whole)."""
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return repr(v)


# --------------------------------------------------------------------------
# XML parts.
# --------------------------------------------------------------------------
def _sheet_xml():
    values = compute_values()
    # Group rows by row number.
    row_cells = {}
    for ref, label, kind, formula in ROWS:
        if kind == "head":
            continue
        _col, rnum = _split_ref(ref)
        row_cells.setdefault(rnum, []).append((ref, label, kind, formula))
    # Also place section/heading labels in column A.
    # Build A-column label map by walking ROWS with an implicit row counter.
    a_labels = {}
    rnum = 1
    for ref, label, kind, formula in ROWS:
        if kind == "head":
            if label:
                a_labels[rnum] = label
            rnum += 1
        else:
            _col, rr = _split_ref(ref)
            rnum = rr
            a_labels[rnum] = label
            rnum += 1

    all_rows = sorted(set(list(a_labels.keys()) + list(row_cells.keys())))
    parts = []
    for r in all_rows:
        cells_xml = []
        if r in a_labels:
            text = a_labels[r]
            text = (text.replace("&", "&amp;").replace("<", "&lt;")
                        .replace(">", "&gt;"))
            cells_xml.append(
                f'<c r="A{r}" t="inlineStr"><is><t xml:space="preserve">'
                f'{text}</t></is></c>')
        for ref, label, kind, formula in row_cells.get(r, []):
            if kind == "num":
                v = ASSUMPTIONS[ref]
                cells_xml.append(f'<c r="{ref}"><v>{_fmt(float(v))}</v></c>')
            else:  # formula
                cached = _fmt(values[ref])
                cells_xml.append(
                    f'<c r="{ref}"><f>{formula}</f><v>{cached}</v></c>')
        parts.append(f'<row r="{r}">' + "".join(cells_xml) + "</row>")
    sheet_data = "".join(parts)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<cols><col min="1" max="1" width="42" customWidth="1"/>'
        '<col min="2" max="2" width="18" customWidth="1"/></cols>'
        f'<sheetData>{sheet_data}</sheetData></worksheet>')


CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
    '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    '</Types>')

ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
    '</Relationships>')

WORKBOOK = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '<sheets><sheet name="Model" sheetId="1" r:id="rId1"/></sheets>'
    '<calcPr fullCalcOnLoad="1"/></workbook>')

WORKBOOK_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '</Relationships>')

STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
    '<borders count="1"><border/></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>')

# Fixed order of parts (name, content). Fixed timestamp -> byte-identical.
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def build(path):
    parts = [
        ("[Content_Types].xml", CONTENT_TYPES),
        ("_rels/.rels", ROOT_RELS),
        ("xl/workbook.xml", WORKBOOK),
        ("xl/_rels/workbook.xml.rels", WORKBOOK_RELS),
        ("xl/worksheets/sheet1.xml", _sheet_xml()),
        ("xl/styles.xml", STYLES),
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in parts:
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data.encode("utf-8"))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, os.pardir, "business", "financial_model.xlsx")
    out = os.path.normpath(out)
    build(out)
    vals = compute_values()
    print("Rezultat lunar (B29) =", _fmt(vals["B29"]), "RON/luna")
    print("wrote", out)


if __name__ == "__main__":
    main()
