# SalvaBox - Strategie (date fictive)

## Problema
In fiecare seara cantinele si cafenelele din campus arunca mancare buna ramasa nevanduta, iar studentii cu buget mic nu stiu unde gasesc o masa ieftina. Se pierd bani si mancare in acelasi timp: partenerii inregistreaza risipa, iar studentii platesc pret intreg la restaurant. Nu exista azi un canal simplu prin care surplusul de seara sa ajunga rapid la cine are nevoie de el, filtrat dupa buget si dieta.

## Public
Studenti din campus cu buget limitat (tinta principala) care vor o masa calda ieftina si rapida. Pe partea de oferta: cantine, cafenele si bistrouri din jurul campusului care raman seara cu cutii de mancare nevanduta si vor sa recupereze o parte din cost in loc sa arunce.

## Solutia
O aplicatie web statica unde studentul filtreaza cutiile de surplus din seara curenta dupa buget si dieta, apoi rezerva una si primeste un cod de ridicare. Pretul mediu al unei cutii este 15 RON/cutie. Cafeneaua partenera incaseaza banii, iar SalvaBox retine un comision de 25% pe fiecare cutie vanduta. Fara backend greu, fara cont: totul se intampla in pagina, deci lansarea e rapida si costul de operare mic.

## Cum aducem clienti
Crestere ieftina, locala, in campus:
- Ambasadori studenti platiti care promoveaza in camine si la seminarii.
- Afise cu cod QR la intrarea in cantine si pe grupurile de an.
- Parteneriat direct cu cafenelele: ele isi trimit clientii proprii spre aplicatie ca sa isi vanda surplusul.
- Postari organice in grupurile de Facebook si Telegram ale facultatilor.
Modelul lunar porneste de la 4000 de cutii vandute si 20 de cafenele abonate. La un comision de 25% pe cutie plus abonamentele lunare, veniturile acopera hostingul, marketingul, taxele de plata si ambasadorii, cu un rezultat lunar de 10300 RON/luna (profit). Numerele vin direct din modelul financiar din business/financial_model.xlsx si se potrivesc cu afisul si cu pitch-ul.

## 3 pasi de pus in practica
1. Semnam primele 5 cafenele pilot din campus si incarcam ofertele lor de seara in aplicatie pentru doua saptamani de test.
2. Recrutam 6 ambasadori studenti si lipim afise cu QR in cantine ca sa aducem primele cateva sute de rezervari.
3. Masuram cutiile vandute si rata de ridicare, apoi ajustam pretul si comisionul si extindem catre urmatoarele cafenele daca rezultatul lunar ramane pozitiv.
