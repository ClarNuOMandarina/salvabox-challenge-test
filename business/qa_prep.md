# SalvaBox - Pregatire Q&A juriu (date fictive)

Toate cifrele vin din business/financial_model.xlsx.

1. De ce ar plati o cafenea 25% pe mancare pe care oricum ar arunca-o?
Pentru ca alternativa este 0 RON: cutia aruncata nu aduce nimic. La o cutie medie de 15 RON, cafeneaua incaseaza 15 RON la tejghea si ne plateste 3,75 RON comision (25%), deci ii raman 11,25 RON pe o cutie care altfel era pierdere. Comisionul se plateste doar pe cutii efectiv vandute.

2. Cat costa sa ajungi la 20 de cafenele platitoare si cum arata ramparea luna 1 -> 6?
Pornim cu 5 cafenele pilot (luna 1) si crestem la 20 pana in luna 6. Lunile 1-5 sunt pe pierdere, asumat: luna 1, cu 5 cafenele si ~9 cutii/cafenea/zi x 22 zile = 990 cutii, venit 990*15*0,25 + 5*150 = 4462,5 RON fata de 6700 RON costuri, deci circa -2237,5 RON/luna. Pragul de rentabilitate cu 20 cafenele abonate: (6700 - 3000) / (15*0,25) = ~987 cutii/luna. Pierderea e acoperita din economiile fondatorilor si o bursa de start-up studentesc (ipoteza).

3. Ce facem daca studentii cumpara doar cutii de 10 RON?
Recalculam din model cu pret mediu 10 RON: comision 10*0,25*4000 = 10000 RON plus 3000 RON abonamente = 13000 RON venituri, minus 6700 RON costuri = 6300 RON/luna profit. Ramane pozitiv chiar in scenariul cel mai ieftin.

4. Cum gestionezi no-show-urile si facturarea comisionului fara plata in aplicatie?
Studentul plateste la tejghea cand ridica cutia; cafeneaua verifica codul SB-#### si tine o lista zilnica pe hartie cu cutiile ridicate. Facturam comisionul lunar doar pe cutiile confirmate ca ridicate; un no-show inseamna cutie nevanduta, deci 0 comision. Panoul de cafenea care inregistreaza automat ridicarile este pasul urmator (deja in strategie). Riscul financiar sta la cafenea.

5. De ce nu si-ar face cafeneaua un simplu grup de WhatsApp?
Un grup ajunge doar la clientii proprii. SalvaBox aduna surplusul din 20 de cafenele intr-un loc, cu filtrare dupa buget si dieta si cod de ridicare, si distribuie cererea a 4000 de cutii/luna in tot campusul - lucru pe care un grup izolat nu il face.