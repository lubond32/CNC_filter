""" 
Zadanie pre chat.openai.com
===========================

Vygeneruj zdrojový program v jazyku Python 3 s nasledujúcou špecifikáciou:

Vytvor zdrojový program s názvom 'cncfilter.py' pod Python 3, čo bude spúšťaný z príkazového riadku s parametrami:
-i [inputfilename], názov vstupného súboru, napr. 'source.cnc ',
-o [outputfilename], názov výstupného súboru, napr. 'target.cnc',
-z [deepZ]  číselná hodnota posledného vnorenia 'Z'. 'deepZ' musí byť zadaná buď ako celé číslo, alebo číslo s oddeľovačom desatinného miesta ".".

Ak vstupné parametre nebudú v príkaze pre spustenie programu uvedené , program po spustení  požiada používateľa o ich zadanie. Ak meno výstupného súboru nebude zadané cez '-o' parameter, program ponúkne defaultný názov vytvorený z názvu vstupného súboru pridaním reťazca "_OUTPUT".
Na  začiatku nech program overí, či zadaný vstupný súbor existuje a či obsahuje G-kód (typické príkazy pre G-kod sú napr. 'T', 'G', 'M' príkazy, alebo iné). Ak je podozrenie, že vstupný súbor G-kódy neobsahuje, nech na to program používateľa upozorní a požiada ho o potvrdenie alebo zmenu názvu.

Program má robiť nasledovné:
Otvorí vstupný súbor s G-kódmi a bude ho čítať riadok po riadku analyzovať a ich prípadným prekopírovaním vytvorí nový výstupný súbor - a to tak, že ponechá zo vstupného súboru len žiadúce 'ENABLED' riadkové oblasti a 'CONTROL' riadky. Čo inými slovami znamená, že pri generovaní výstupného súboru sa odfiltrujú nežiadúce 'DASABLED' riadkové oblasti. 

Program preto musí najskôr identifikovať ENABLED oblasti, DISABLED oblasti a CONTROL riadky. DISABLED oblasti do výstupného súboru program neprekopíruje! Identifikácia ENABLED oblasti je dôležitá aj preto, lebo ukočuje prípadnú predchádzajúcu DISABLED oblasť.

Pravidlá pre identifikáciu OBLASTÍ:

1/ Pre obe oblasti (ENABLED aj DISABLED) platí, že sú to súvislé a po sebe nasledujúce riadky. 

2/ Okrem bodu 1 pre ENABLED oblasť  platí:
- ENABLED oblasť začína riadkom ktorý začína výrazom "G0" alebo obsahuje "Z" príkaz "G1Z-deepZ", kde deepZ je zadaná hodnota. Ak sa narazí na takýto riadok, tak sa potom hľadá koniec ENABLED oblasti, ktorá:
- končí riadkom (v rátane tohoto riadku), ktorý je buď úplne posledným riadkom vstupného súboru, alebo je to riadok ktorý je pred prvým riadkom najbližšej nasledujúcej DISABLED skupiny, a to podľa toho čo nastane skôr.

2/ Okrem bodu 1 pre DISABLED oblasť navyše platí:
- oblasť začína riadkom začínajúcim s príkazom 'G1' a súčasne tento riadok obsahuje "Z" príkaz ktorý je iný než "Z-deepZ", kde deepZ je zadaná  hodnota. Ak sa narazí na takýto riadok, tak sa potom hľadá koniec DISABLED oblasti, ktorá:
- končí riadkom (v rátane tohoto riadku), ktorý je buď úplne posledný riadok súboru, alebo je to riadok ktorý je pred prvým riadkom najbližšej nasledujúcej ENABLED skupiny, a to podľa toho čo nastane skôr.

Pre CONTROL riadky platí:
- riadok nie je súčasťou ani ENABLED oblasti, ani DISABLED oblasti a súčasne platí, že riadok začína špeciálnym príkazom "T" alebo "M". 
"""

import sys
import os


def parse_args(args):
    input_file = None
    output_file = None
    deep_z = None

    i = 0
    while i < len(args):
        if args[i] == '-i':
            if i + 1 < len(args):
                input_file = args[i + 1]
            i += 2
        elif args[i] == '-o':
            if i + 1 < len(args):
                output_file = args[i + 1]
            i += 2
        elif args[i] == '-z':
            if i + 1 < len(args):
                try:
                    deep_z = float(args[i + 1])  # Konvertuje zadané číslo na desatinné
                except ValueError:
                    print("Invalid value for -z parameter. Please provide a valid number.")
                    sys.exit(1)
            i += 2
        else:
            i += 1
            
    return input_file, output_file, deep_z


def get_input_file():
    input_file = input("Enter input file name: ")
    while not os.path.exists(input_file):
        print("File does not exist.")
        input_file = input("Enter input file name: ")
    return input_file


def get_output_file(input_file):
    if input_file:
        base_name = os.path.splitext(input_file)[0]
        return base_name + "_OUTPUT.cnc"
    else:
        return input("Enter output file name: ")


def check_gcode(input_file):
    with open(input_file, 'r') as file:
        for line in file:
            if any(cmd in line for cmd in ['T', 'G', 'M']):
                return True
    return False

def process_file(input_file, output_file, deep_z):
    in_enabled_area = False
    with open(input_file, 'r') as in_file, open(output_file, 'w') as out_file:
        for line in in_file:
            if line.startswith(('G0', f'G1Z-{deep_z}')):
                in_enabled_area = True
                out_file.write(line)
            elif line.startswith('G1') and 'Z' in line and not line.startswith(f'G1Z-{deep_z}'):
                out_file.write("; " + line)  # Zaremuje riadky z DISABLED oblastí
                in_enabled_area = False
            elif in_enabled_area or any(cmd in line for cmd in ['T', 'M']):
                out_file.write(line)
            else:
                out_file.write("; " + line)  # Zaremuje riadky z DISABLED oblastí

def main():
    input_file, output_file, deep_z = parse_args(sys.argv[1:])

    if not input_file:
        input_file = get_input_file()

    if not check_gcode(input_file):
        choice = input("The input file does not seem to contain G-code. Continue? (y/n): ")
        if choice.lower() != 'y':
            return

    if not output_file:
        output_file = get_output_file(input_file)

    process_file(input_file, output_file, deep_z)
    print(f"Filtered G-code saved to {output_file}")


if __name__ == "__main__":
    main()
