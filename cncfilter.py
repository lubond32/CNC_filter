""" 
cncfilter.py - redukčný Python 3 skript.
Program cncfilter.py slúži na filtrovanie prechodov v súboroch obsahujúcich
CNC G-kód. Filtruje nežiaduce časti kódu na základe zadaných parametrov 
a vytvára nový súbor obsahujúci len žiadúce časti.
"""
import sys
import os


def parse_args(args):
    """
    Spracováva argumenty príkazového riadku a vracia tuple obsahujúci hodnoty vstupného súboru, výstupného súboru a hĺbky Z.
    """
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
                    print("Neplatná hodnota pre parameter -z. Prosím, zadajte platné číslo.")
                    sys.exit(1)
            i += 2
        elif args[i] == '-h':
            print_help()
            sys.exit(0)
        else:
            i += 1

    return input_file, output_file, deep_z


def print_help():
    """
    Vypisuje nápovedu s možnosťami spustenia programu a vysvetlením jednotlivých parametrov.
    """
    print("Použitie: python cncfilter.py [-i vstupny_subor] [-o vystupny_subor] [-z hlbka_z] [-h]")
    print("Možnosti:")
    print("  -i vstupny_subor    Určuje vstupný súbor.")
    print("  -o vystupny_subor   Určuje výstupný súbor.")
    print("  -z hlbka_z          Určuje hodnotu pre hĺbku Z.")
    print("  -h                  Zobrazí túto nápovedu.")


def get_input_file():
    """
    Získava názov vstupného súboru od používateľa a kontroluje, či súbor existuje.
    """
    input_file = input("Zadajte názov vstupného súboru: ")
    while not os.path.exists(input_file):
        print("Súbor neexistuje.")
        input_file = input("Zadajte názov vstupného súboru: ")
    return input_file


def get_output_file(input_file):
    """
    Generuje názov výstupného súboru na základe názvu vstupného súboru.
    """
    if input_file:
        base_name = os.path.splitext(input_file)[0]
        return base_name + "_OUTPUT.cnc"
    else:
        return input("Zadajte názov výstupného súboru: ")


def check_gcode(input_file):
    """
    Kontroluje, či vstupný súbor obsahuje G-kód.
    """
    with open(input_file, 'r') as file:
        for line in file:
            if any(cmd in line for cmd in ['T', 'G', 'M']):
                return True
    return False


def process_file(input_file, output_file, deep_z):
    """
    Spracúva vstupný súbor s G-kódom a vytvára výstupný súbor s filtrovanými G-kódmi.
    """
    n=0
    in_enabled_area = True
    with open(input_file, 'r') as in_file, open(output_file, 'w') as out_file:
        for line in in_file:
            n=n+1
            if line.startswith(f'G1Z') and not line.startswith(f'G1Z-{deep_z}'):
                out_file.write("; " + line)  # Zaremuje riadky z DISABLED oblastí
                in_enabled_area = False
            elif line.startswith(f'G1Z-{deep_z}'):
                out_file.write(line)
                in_enabled_area = True
            elif in_enabled_area and line.startswith('G0'):
                out_file.write(line)
            elif in_enabled_area or any(cmd in line for cmd in ['T', 'M']):
                out_file.write(line)
            else:
                out_file.write("; "  + line)  # Zaremuje riadky z DISABLED oblastí


def main():
    input_file, output_file, deep_z = parse_args(sys.argv[1:])

    while not input_file or not output_file or deep_z is None:
        print("Chýbajú jedno alebo viacero vstupných parametrov.")
        choice = input("Chcete zadať chýbajúce parametre (y) alebo ukončiť program (n)? ")
        if choice.lower() == 'n':
            sys.exit(0)
        if not input_file:
            input_file = get_input_file()
        if not output_file:
            output_file = get_output_file(input_file)
        if deep_z is None:
            deep_z_input = input("Zadajte hodnotu pre hĺbku Z: ")
            try:
                deep_z = float(deep_z_input)
            except ValueError:
                print("Neplatná hodnota pre hĺbku Z. Prosím, zadajte platné číslo.")

    if not check_gcode(input_file):
        choice = input("Zdá sa, že vstupný súbor neobsahuje G-kód. Pokračovať? (y/n): ")
        if choice.lower() != 'y':
            return
    
    print
    print(f"vstup:  {input_file}")
    print(f"vystup: {output_file}")
    print(f"deep_z: {deep_z}")
    print

    process_file(input_file, output_file, deep_z)
    print(f"Vyfiltrovaný G-kód bol uložený do súboru {output_file}")


if __name__ == "__main__":
    main()
