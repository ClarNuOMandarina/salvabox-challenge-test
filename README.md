# SalvaBox

**Aplicatie live:** https://clarnuomandarina.github.io/salvabox-challenge-test/

Studentii din campus filtreaza cutiile cu mancare surplus din seara curenta
dupa buget si dieta, rezerva una si primesc un cod de ridicare. Aplicatie web
statica (HTML + CSS + JavaScript vanilla), fara backend, fara cont, fara plata
in aplicatie. Date fictive.

## Cum testezi in 3 pasi (cazul demo)

1. Deschide https://clarnuomandarina.github.io/salvabox-challenge-test/ si pune
   **pret maxim `15`** RON cu dieta **Vegetarian**, apoi apasa **Filtreaza**.
2. Apar **3 cutii** sortate crescator dupa pret: *Paste cu sos de rosii* 10 RON,
   *Tocanita de legume cu orez* 12 RON, *Curry de naut vegan* 14 RON.
3. Apasa **Rezerva** la prima cutie: primesti un cod de ridicare `SB-####` si
   numarul de cutii ramase scade cu 1.

## Cele 6 livrabile

| # | Livrabil | Cale |
|---|----------|------|
| 1 | Aplicatia web (app) | `docs/index.html`, `docs/style.css`, `docs/app.js` |
| 2 | Strategia (1 pagina) | `business/strategy.md` |
| 3 | Model financiar (formule) | `business/financial_model.xlsx` (sursa: `tools/build_model.py`) |
| 4 | Afis promotional | `business/poster.html` |
| 5 | Jurnal AI | `business/ai_journal.md` |
| 6 | Pitch (5 slide-uri) | `business/pitch.html` |

## Cum reconstruiesti modelul financiar

Modelul `.xlsx` este generat deterministic din Python stdlib (fara `openpyxl`):

```
python tools/build_model.py
```

Comanda scrie `business/financial_model.xlsx`: ipotezele sunt numere tipizate,
iar fiecare celula de cost / venit / rezultat este o formula `<f>`.

## Verificare

Ruleaza toata suita de teste (Python 3.11 stdlib, fara dependinte externe):

```
python -m unittest discover -s tests -v
```

Testele verifica aplicatia, modelul (formule + numerele recalculate), afisul si
limitele de contest ale livrabilelor (jurnal, pitch, README).

## Note

- **Date false.** Toate datele (cutii, preturi, cafenele, numerele din model)
  sunt fictive, pentru demo. Nu exista date personale reale, parole sau secrete
  in prompturi, Issues sau fisiere.
- **Reguli de contest.** Proiectul a fost construit de la zero in timpul
  sprintului. Singura resursa pregatita din afara este scheletul de coordonare
  multi-agent `github-multi-agent-skill.txt v1.2`, listat in jurnalul AI
  (`business/ai_journal.md`); nu s-a folosit niciun alt sablon extern.
