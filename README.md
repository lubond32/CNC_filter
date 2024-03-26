# cncfilter.py
redukčný Python 3 skript

## Popis

Program `cncfilter.py` slúži na filtrovanie súborov obsahujúcich CNC G-kód. Filtruje nežiaduce časti kódu na základe zadaných parametrov a vytvára nový súbor obsahujúci len žiadúce časti.  

Primárnym cieľom je odfiltrovať zo súboru všetky pracovné pohyby súvisiace s frézovaním na **nefinálnom** vnorení nástroja. Nový súbor bude obsahovať len pracovné pohyby s finálnym vnorením v osi Z. Tu pozri [príklad použitia](#príklad-použitia).

## Spúšťanie programu

``
python cncfilter.py [-i vstupny_subor] [-o vystupny_subor] [-z hlbka_z] [-h]
``


## Parametre

- `-i vstupny_subor`: Určuje vstupný súbor s CNC G-kódom.
- `-o výstupny_subor`: Určuje názov výstupného súboru, kam bude uložený filtrovaný kód. Ak nie je zadaný, použije sa predvolený názov s apendovaným reťazcom "_OUTPUT".
- `-z hlbka_z`: Určuje hĺbku vnorenia Z, ktorá sa použije na filtrovanie pracovných pohybov finálneho vnorenia. Môže byť zadaná buď ako celé číslo alebo ako číslo s desatinným miestom oddeleným bodkou ".".
- `-h`: Zobrazí nápovedu s možnosťami spustenia programu.

## Funkcionalita

1. Program najprv spracuje a overí zadané parametre.
2. Ak chýbajú nejaké parametre, program požiada používateľa o ich zadanie alebo ponúkne možnosť zobraziť nápovedu.
3. Kontroluje, či zadaný vstupný súbor existuje a obsahuje CNC G-kód. Ak nie, program upozorní používateľa a požiada ho o potvrdenie alebo zmenu názvu súboru.
4. Na základe zadaných parametrov filtrovaných pracovných pohybov (ENABLED a DISABLED oblastí) a hĺbky Z, program spracuje vstupný súbor a vytvorí výstupný súbor obsahujúci len žiadúce časti kódu.
5. Nežiaduce časti kódu (DISABLED oblasti) sú zaremované a vložené do výstupného súboru vo forme komentárov.

### ENABLED / DISABLED oblasti
Termíny `ENABLED` oblasť a `DISABLED` oblasť vznikli v pocese definície zadania a sú použité pre označenie častí z pôvodného cnc-kódu, ktoré sa majú alebo nemajú preniesť do výstupného súboru s novým cnc-kódom.  

- `ENABLED` oblasti,  
  ako aj riadky s riadiacimi kódmi `M` a `T` sa do výstupného súboru prenášajú nezmenené.  

- `DISABLED` oblasti  
  kvôli prehľadnosti sa do výstupého súboru riadky z DISABLED oblastí prenášajú, ale zaremované. Teda pred každý riadok z DISABLED oblasti sa vloží (prepdonuje) REM-reťazec `"; "`. Vo výkone výstupného kódu sa tieto riadky nachádzajú len formálne a pri výkone kódu (frézovaní) sa v konečnom dôsledku neuplatňujú.

### Riadková analýza
Vstupný súbor s pôvodným cnc-kódom sa analyzuje riadok po riadku. Ohľadne identifikácie, či sa jedná o riadok z ENABLED alebo z DISABLED oblasti, je kľúčová identifikácia riadkov s pracovným pohybom vnorenia, a to či je hodnota vnorenia rovná alebo rôzna od požadovanej hodnoty `{hlbka_z}`:

- Ak riadok kódu začína príkazom pracovného pohybu `G1` so zmenou v Z-súradnici  `"G1Z-{hlbka_z}"`, napr. v príklade uvedenom nižšie je to reťazec "G1Z-11", potom tento riadok je začiatkom (alebo súčasťou už identifikovanej) **ENABLED** oblasti. Riadok sa do výstupného súboru skopíruje nezmenený. Zároveň sa nastaví interný status oblasti na `True`.  
  
- Ak riadok kódu začína príkazom pracovného pohybu `G1`, ale so zmenou v Z-súradnici na hodnotu inú než je finálne vnorenie - vo výraze `"G1Z-"{niečo}` je `{niečo} <> {hlbka_z}`, napr. v príklade uvedenom nižšie je to reťazec "G1Z-5.5", potom tento riadok je začiatkom (alebo súčasťou už identifikovanej) **DISABLED** oblasti. Riadok sa do výstupného súboru prenesie zaremovaný. Zároveň sa nastaví interný status oblasti na `False`, aby bolo zrejmé že aj nasledujúce riadky majú byť vo výstupnom kóde zaremované - a to dovtedy, kým sa nenarazí na ENABLED oblasť.  
  
- Ak riadok kódu začína iným príkazom, ale je nastavený status oblasti na `True` - t.j. identifikovaná je momentálne ENABLED oblasť, tak sa takýto riadok do výstupného súboru skopíruje nezmenený.  


## Popis funkcií

- `parse_args(args)`: Spracováva argumenty príkazového riadku a vracia tuple obsahujúcu meno vstupného súboru, meno výstupného súboru a hodnotu finálnej hĺbky Z.
- `print_help()`: Vypisuje nápovedu s možnosťami spustenia programu a vysvetlením jednotlivých parametrov.
- `get_input_file()`: Získava názov vstupného súboru od používateľa a kontroluje, či súbor existuje.
- `get_output_file(input_file)`: Generuje názov výstupného súboru na základe názvu vstupného súboru.
- `check_gcode(input_file)`: Kontroluje, či vstupný súbor obsahuje CNC G-kód.
- `process_file(input_file, output_file, deep_z)`: Spracúva vstupný súbor s CNC G-kódom a vytvára výstupný súbor s filtrovanými G-kódmi.
- `main()`: Hlavná funkcia programu, ktorá riadi celý proces spracovania.

## Príklad použitia  

Predpokladajme pôvodný cnc-kód pre 2,5D frézu, v ktorom je naprogramované rezanie `10 mm hrubého` materiálu, ale na 2 vnorenia. Pričom prvé vnorenie nástroja reže materiál len do polovice jeho hrúbky (napr. -5.5 mm) a až to druhé (finálne) vnorenie do hĺbky `-11 mm` prereže materál úplne. Počas finálneho vnorenia môžu byť v kóde naprogramované aj mostíky.  

**Poznámka k mostíkom:**  
- Mostíky sú miesta, kde na určitej dĺžke v dráhe frézy materiál nie je úplne prerezaný. 
- Majú význam hlavne pri frézovaní menších tvarov. 
- Ich úlohou je udržať odrezanú časť v príreze, aby sa po odrezaní tento diel neposunul a tak prípadne nekolidoval s rezným nástrojom frézy.  

Problémom pri frézovaní je veľmi často to, že po vykonaní kódu zostane v rezných drážkach trieska, ktorú niekedy nie je jednoduché dodatočne vyčistiť. Preto je často potrebné drážky prečistiť ďalším prechodom frézky. Lenže - keďže má pôvodný kód až 2 vnorenia, tak jeho vykonanie trvá pomerne dlho a prvý prechod (nefinálne vnorenie) je zbytočný.

Potrebujeme preto nový cnc-kód, ktorý je v istých častiach totožný s pôvodným kódom, mal by však obsahovať len kódy z finálnych vnorení. Pre samotné vybratia triesky z drážok prvé vnorenie nepotrebujeme, frézka sa môže vnárať rovno do finálnej hĺbky.

Preto pôvodný kód necháme upraviť skriptom `cncfilter.py`. Skript z neho odfiltruje všetky pracovné pohyby prvého vnorenia resp. vnorení (ak ich je viacej) - teda tých, ktoré nerežú do materiálu v jeho plnej hrúbke. 

Príklad spustenia tvorby nového kódu:  
    ```
    python cncfilter.py -i povodnykod.cnc -o cistiacikod.cnc -z 11
    ```  

Vytvorí sa nový súbor *cistiacikod.cnc*, ktorý bude obsahovať len riadky s kódom súvisiacim s finálnym vnorením, teda do hĺbky 11 mm.  

**Mostíky finálneho prechodu zostávajú:**  

Čiastočné vynárania a opätovné následné vnárania sa nástroja pri vytváraní mostíkov 
- nie sú deklarované ako pracovné pohyby (kód G1), ale
- sú deklarované ako nepracovné pohyby s kódom G0 a preto
  - nemenia status oblasti.
- Takže mostíky 
  - sú súčasťou 'požadovaných' oblastí a 
  - zostávajú v novom kóde nezmenené.
