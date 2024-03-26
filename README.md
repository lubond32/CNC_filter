# cncfilter.py
redukčný Python 3 skript

## Popis

Program `cncfilter.py` slúži na filtrovanie súborov obsahujúcich CNC G-kód. Filtruje nežiaduce časti kódu na základe zadaných parametrov a vytvára nový súbor obsahujúci len žiadúce časti.  

Primárnym cieľom bolo odfiltrovať zo súboru všetky pracovné pohyby súvisiace s frézovaním na **nefinálnom** vnorení nástroja. Nový súbor bude obsahovať len pracovné pohyby s finálnym vnorením v osi Z.


## Spúšťanie programu

``bash
python cncfilter.py [-i vstupny_subor] [-o vystupny_subor] [-z hlbka_z] [-h]
``


## Parametre

- `-i vstupny_subor`: Určuje vstupný súbor s CNC G-kódom.
- `-o vystupny_subor`: Určuje názov výstupného súboru, kam bude uložený filtrovaný kód. Ak nie je zadaný, použije sa predvolený názov s pridaným "_OUTPUT".
- `-z hlbka_z`: Určuje hĺbku vnorenia Z, ktorá sa použije na filtrovanie pracovných pohybov finálneho vnorenia. Môže byť zadaná buď ako celé číslo alebo ako číslo s desatinným miestom oddeleným bodkou ".".
- `-h`: Zobrazí nápovedu s možnosťami spustenia programu.

## Funkcionalita

1. Program najprv spracuje a overí zadané parametre.
2. Ak chýbajú nejaké parametre, program požiada používateľa o ich zadanie alebo ponúkne možnosť zobraziť nápovedu.
3. Kontroluje, či zadaný vstupný súbor existuje a obsahuje CNC G-kód. Ak nie, program upozorní používateľa a požiada ho o potvrdenie alebo zmenu názvu súboru.
4. Na základe zadaných parametrov filtrovaných pracovných pohybov (ENABLED a DISABLED oblastí) a hĺbky Z, program spracuje vstupný súbor a vytvorí výstupný súbor obsahujúci len žiadúce časti kódu.
5. Nežiaduce časti kódu (DISABLED oblasti) sú zaremované a vložené do výstupného súboru vo forme komentárov.

### ENABLED / DISABLED oblasti
Termíny `ENABLED` oblasť a `DISABLED` oblasť vznikli v pocese definície zadania a sú použité pre akési označenie častí z pôvodného cnc-kódu, ktoré sa májú alebo nemajú preniesť do výstupného súboru s novým cnc-kódom.  

- `ENABLED` oblasti,  
  ako aj riadky s riadiacimi kódmi `M` a `T` sa do výstupného súboru prenášajú nezmenené.  

- `DISABLED` oblasti  
  kvôli prehľadnosti sa do výstupého súboru riadky z DISABLED oblastí prenášajú, ale zaremované. Teda pred každý riadok z DISABLED oblasti sa vloží (prepdonuje) REM-reťazec `"; "`. Vo výkone výstupného kódu sa teda tieto riadky nachádzajú zaremované a pri výkone tohoto kódu sa v konečnom dôsledku neuplatňujú.

### Riadková analýza
Vstupný súbor s pôvodným cnc-kódom sa analyzuje riadok po riadku. Ohľadne identifikácie, či sa jedná o riadok z ENABLED alebo z DISABLED oblasti, je kľúčová identifikácia riadkov s pracovným pohybom vnorenia, a to či je hjodnota vnorenia rovná alebo rôzna od požadovanej hodnoty `{hlbka_z}`:

- Ak riadok kódu začína príkazom pracovného pohybu `G1` so zmenou v Z-súradnici  `"G1Z-"{hlbka_z}`, napr. v našom príklade uvedenom nižšie je to reťazec "G1Z-11", potom tento riadok je začiatkom (alebo súčasťou už identifikovanej) **ENABLED** oblasti. Riadok sa do výstupného súboru skopíruje nezmenený. Zároveň sa nastaví interný status oblasti na `True`.  
  
- Ak riadok kódu začína príkazom pracovného pohybu `G1`, ale so zmenou v Z-súradnici na hodnotu iného než finálneho vnorenia - vo výraze `"G1Z-"{niečo}` je `{niečo} <> {hlbka_z}`, napr. v našom príklade uvedenom nižšie je to reťazec "G1Z-5.5", potom tento riadok je začiatkom (alebo súčasťou už identifikovanej) **DISABLED** oblasti. Riadok sa do výstupného súboru prenesie zaremovaný. Zároveň sa nastaví interný status oblasti na `False`, aby bolo zrejmé že aj nasledujúce riadky majú bý vo výstupnom kóde odfiltrované (remované).  
  
- Ak riadok kódu začína iným príkazom, ale je nastavený status oblasti na `True` - t.j. identifikovaná je momentálne ENABLED oblasť, tiež sa takýto riadok do výstupného súboru kopíruje nezmenený.  


## Popis funkcií

- `parse_args(args)`: Spracováva argumenty príkazového riadku a vracia tuple obsahujúcu meno vstupného súboru, meno výstupného súboru a hodnotu finálnej hĺbky Z.
- `print_help()`: Vypisuje nápovedu s možnosťami spustenia programu a vysvetlením jednotlivých parametrov.
- `get_input_file()`: Získava názov vstupného súboru od používateľa a kontroluje, či súbor existuje.
- `get_output_file(input_file)`: Generuje názov výstupného súboru na základe názvu vstupného súboru.
- `check_gcode(input_file)`: Kontroluje, či vstupný súbor obsahuje CNC G-kód.
- `process_file(input_file, output_file, deep_z)`: Spracúva vstupný súbor s CNC G-kódom a vytvára výstupný súbor s filtrovanými G-kódmi.
- `main()`: Hlavná funkcia programu, ktorá riadi celý proces spracovania.

## Príklad použitia  

Predpokladajme pôvodný cnc-kód pre 2,5D frézu, v ktorom je naprogramované rezanie `10mm hrubého materiálu` na 2 vnorenia. Pričom prvé vnorenie reže materiál len do polovice jeho hrubky (napr. -5 mm) a až to druhé (finálne) vnorenie nástroja do hĺbky `-11mm` prereže materál úplne. Počas finálneho vnorenia sú v kóde naprogramované a mostíky, t.j. miesta kde na určitej dĺžke v dráhe frézy materiál nie je úplne prerezaný.

Samotný kód nie je problém. Problémom je, že po vykponaní kódu zostane v rezných drážkach zbytok odrezaného materiálu (trieska), ktorý nie je jednoduche z drážky vysať. Je potrebné drážky prečistiť ďalším prechodom frézky. Lenže - keďže má pôvodný kód až 2 vnorenia, tak jeho vykonanie trvá pomerne dlho.

Potrebujeme preto nový kód, ktorý je v zásade totožný s pôvodným cnc-kódom, ale musí obsahovať len kódy z finálneho vnorenia. Pre samotné vybratia triesky z drážok prvé vnorenie nepotrebujeme.

Preto pôvodný kód upravíme pomocou skriptu `cncfilter.py`. Skript z neho odfiltruje všetky pracovné pohyby prvého vnorenia resp. vnorení (ak ich je viacej) - teda tých, ktoré nerežú do materiálu v jeho plnej hrúbke. 

Pôvodný kod potom volá nasledovne

- 
