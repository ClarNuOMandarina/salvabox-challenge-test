# SalvaBox - Strategie (date fictive)

## Problema
In fiecare seara cantinele si cafenelele din campus arunca mancare buna ramasa nevanduta, iar studentii cu buget mic nu stiu unde gasesc o masa ieftina. Se pierd bani si mancare in acelasi timp: partenerii inregistreaza risipa, iar studentii platesc pret intreg la restaurant. Nu exista azi un canal simplu prin care surplusul de seara sa ajunga rapid la cine are nevoie de el, filtrat dupa buget si dieta.

## Public
Studenti din campus cu buget limitat (tinta principala) care vor o masa calda ieftina si rapida. Pe partea de oferta: cantine, cafenele si bistrouri din jurul campusului care raman seara cu cutii de mancare nevanduta si vor sa recupereze o parte din cost in loc sa arunce.

## Solutia
O aplicatie web statica unde studentul filtreaza cutiile de surplus din seara curenta dupa buget si dieta, apoi rezerva una si primeste un cod de ridicare. Pretul mediu al unei cutii este 15 RON/cutie, medie ponderata pentru luna 6: demo are cutii de 10-18 RON, iar din luna 6 apar si meniuri la 16-18 RON. La o medie de 13 RON, rezultatul recalculat din model (comision 13*0.25*4000 = 13000, plus 3000 abonamente, minus 6700 costuri) ramane pozitiv, 9300 RON/luna. Studentul plateste la tejghea cand ridica cutia, deci cafeneaua partenera incaseaza banii; SalvaBox nu proceseaza plati, ci factureaza lunar partenerului un comision de 25% pe fiecare cutie vanduta. MVP-ul demo e o pagina statica fara cont; urmatorul pas este un panou simplu prin care cafenelele isi incarca singure ofertele de seara.

## Cum aducem clienti
Crestere ieftina, locala, in campus:
- Ambasadori studenti platiti care promoveaza in camine si la seminarii.
- Afise cu cod QR la intrarea in cantine si pe grupurile de an.
- Parteneriat direct cu cafenelele: ele isi trimit clientii proprii spre aplicatie ca sa isi vanda surplusul.
- Postari organice in grupurile de Facebook si Telegram ale facultatilor.
Modelul financiar arata luna 6, dupa extindere: 4000 de cutii si 20 de cafenele abonate, adica 4000 / 20 / 22 zile = ~9 cutii pe cafenea pe zi, un surplus realist. La comision de 25% plus abonamente, veniturile acopera hostingul, marketingul, contabilitatea si ambasadorii, cu rezultat lunar inainte de impozit de 11300 RON/luna (profit). Numerele vin din business/financial_model.xlsx.

## 3 pasi de pus in practica
1. Semnam primele 5 cafenele pilot din campus si incarcam ofertele lor de seara in aplicatie pentru doua saptamani de test.
2. Recrutam 6 ambasadori studenti si lipim afise cu QR in cantine ca sa aducem primele cateva sute de rezervari.
3. Masuram cutiile vandute si rata de ridicare, apoi ajustam pretul si comisionul si extindem catre urmatoarele cafenele daca rezultatul lunar ramane pozitiv.
