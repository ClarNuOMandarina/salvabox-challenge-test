# Jurnal AI - SalvaBox (date fictive)

## Unelte folosite
- **Claude (prin Kiro)** - modelul AI, rulat in stratul multi-agent Kiro Crew
  (un Coordonator + mai multi Session Agent pe aceeasi echipa).
- **GitHub + gh CLI** - singura sursa de adevar a coordonarii: Issues, etichete,
  PR-uri, review-uri si merge (`gh.exe` + `git`).
- **GitHub Pages** - publicarea aplicatiei statice din `docs/` la un link public.
- **Python 3.11 (stdlib)** - testele (`unittest`) si generarea `.xlsx` cu `zipfile`.
- **Excel** - folosit DOAR ca sa confirmam ca `financial_model.xlsx` se deschide
  fara reparatii si ca formulele recalculeaza aceleasi numere ca testul.

## 3 prompturi bune
1. "Pure function `filterBoxes(boxes, maxPrice, diet)`: keeps `price <= maxPrice`
   and `left > 0`; `oricare` keeps all diets, `vegetarian` keeps vegetarian AND
   vegan, `vegan` keeps vegan only; sorted by price ascending. It must not touch
   the DOM."
2. "Build `tools/build_model.py` (Python 3.11 stdlib, zipfile, no openpyxl) that
   writes `business/financial_model.xlsx` with one sheet and sections
   Ipoteze/Costuri/Venituri/Rezultat. Assumptions are typed numbers; every cost,
   revenue and result cell is an `<f>` formula with a cached `<v>` value. Set
   `fullCalcOnLoad=1`; valid OOXML Excel opens without a repair prompt."
3. "Make the inline SVG illustration genuinely nice (food box, leaf, campus),
   clean typography, good contrast. Romanian text without diacritics is fine.
   No external resources (no CDN, no fonts)."

## Greseli AI corectate
- **Regula dietei (T1).** AI-ul risca sa excluda cutiile vegane cand filtrul e
  "vegetarian". **Verificat:** am oglindit regula in Python in `test_app.py` si
  am verificat de mana cazul demo (max 15 RON + vegetarian -> 3 cutii). **Fix:**
  `vegetarian` pastreaza vegetarian SI vegan; testul cade altfel.
- **Fluxul banilor se contrazicea (T2, prins la review).** Strategia spunea
  "cafeneaua incaseaza banii", dar modelul taxa SalvaBox cu un fee de 3% pe tot
  GMV-ul. **Verificat:** in app-ul live plata e la tejghea, fara plata online,
  deci SalvaBox nu proceseaza plati. **Fix:** am scos fee-ul pe GMV, am pus un
  cost real "contabilitate + facturare" si am reconstruit xlsx-ul (rezultat
  10300 -> 11300 RON/luna) peste tot.
- **Volum fara cadru de timp (T2, prins la review).** "4000 cutii, 20 cafenele"
  parea sa contrazica pilotul de 5 cafenele. **Verificat:** 4000/20/22 zile =
  ~9 cutii/cafenea/zi. **Fix:** am numit explicit "luna 6, dupa extindere".
- **Pretul "8 lei" copiat din brief (T3, prins la review).** **Verificat:** fata
  de `docs/app.js`, cea mai ieftina cutie disponibila e 10 RON. **Fix:** "de la
  10 lei" pe afis, plus un test care citeste minimul din app si cade la
  nepotrivire.
- **Buton gresit (review).** README/pitch ziceau "Filtreaza"; real e "Cauta
  cutii". **Fix:** corectat; test pe `#searchBtn`.

## Resurse din afara
- `github-multi-agent-skill.txt v1.2` - schelet de coordonare multi-agent
  (unealta pregatita, nu continut de proiect). Niciun alt sablon extern.
