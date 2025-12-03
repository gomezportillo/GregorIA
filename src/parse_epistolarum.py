import re
import subprocess
from pathlib import Path

IN_PATH = "letters/epistolarum/"
OUT_PATH = "letters/txt/"

PDF_INPUT = IN_PATH + "Registri_Epistolarum.pdf"
TXT_INTERMEDIATE = OUT_PATH + "epistolarum.txt"
TXT_INTERMEDIATE_PARSED = OUT_PATH + "epistolarum_parsed.txt"
OUT_DIR = Path(OUT_PATH)

ROMAN_NUMERAL_MAP = {
    'I': 1,
    'V': 5,
    'X': 10,
    'L': 50,
    'C': 100,
    'D': 500,
    'M': 1000
}

def roman_to_int(roman: str) -> int:
    roman = roman.upper()
    total = 0
    prev_value = 0
    for char in reversed(roman):
        value = ROMAN_NUMERAL_MAP[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    return total


def extract_pdf_to_text():
    """Uses pdftotext to convert PDF to text."""
    OUT_DIR.mkdir(exist_ok=True)

    subprocess.run(
        [
            "pdftotext",
            "-layout",
            "-f",
            "5",  # las 4 primras paginas son ruido
            PDF_INPUT,
            TXT_INTERMEDIATE,
        ],
        check=True,
        stderr=subprocess.DEVNULL,  # oculta warnings
    )

def remove_split_footnotes_old(text: str) -> str:
    """
    Sometimes the footnote covers several pages and the current one has only a part

    Si mas de 3 lineas seguidas empiezan por +8 espacios --> nota a pie de pagina
    """
    HEADER_LINES = 10
    FOOTNOTE_INDENT = 9  # líneas que empiezan con +9 espacios son notas

    lines = text.splitlines()

    cleaned_lines = []

    # mantener las primeras HEADER_LINES líneas tal cual
    cleaned_lines.extend(lines[:HEADER_LINES])

    print(cleaned_lines)

    # procesar el resto
    for line in lines[HEADER_LINES:]:
        if line.startswith(" " * FOOTNOTE_INDENT):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def remove_split_footnotes(text: str) -> str:

    """
    Elimina bloques donde hay al menos 8 líneas seguidas que empiezan con >= 9 espacios
    """
    indent = 9
    min_consecutive = 3

    lines = text.splitlines()
    cleaned_lines = []

    # Buffer temporal para líneas indentadas consecutivas
    buffer = []

    for line in lines:
        if line.startswith(" " * indent):
            # Línea indentada: la añadimos al buffer
            buffer.append(line)
        else:
            # Línea no indentada:
            # Si el buffer tiene al menos min_consecutive líneas descartamos el buffer
            if len(buffer) >= min_consecutive:
                # print(buffer)
                # print \n--------------------------\n")
                pass
            else:
                cleaned_lines.extend(buffer)
            buffer = []
            # Añadimos la línea no indentada actual
            cleaned_lines.append(line)

    if len(buffer) >= min_consecutive:
        pass  # descartamos
    else:
        cleaned_lines.extend(buffer)

    return "\n".join(cleaned_lines)



def clear_text(text: str) -> str:
    """Text cleaning"""
    # Remove separator lines like ----- or ______
    text = re.sub(r"^[\—\=_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Remove superindex characters
    text = re.sub(r"[¹²³⁴⁵⁶⁷⁸⁹⁰]", "", text)

    # Remove any line containing 'Philip Schaff' (headers)
    text = re.sub(r"^.*Philip Schaff.*$", "", text, flags=re.MULTILINE | re.IGNORECASE)

    # Remove lines that only contain a number (page numbers)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Remove blocks of footnotes in the text
    pattern = re.compile(
        r"(?:\n|\A)"              # start at a newline or start of text
        r"( {7}\d{1,4} .*(?:\n"   # line starting with 7 spaces, number, space, text + newline
        r"(?:[^\S\r\n]*\S.*\n)*"  # 0 or more continuation lines (non-empty lines with optional leading spaces)
        r"\n)+)",                 # block ends at empty line (double newline)
        flags=re.MULTILINE,
    )
    text = pattern.sub("\n", text)

    # Buscar al principio de línea (^), opcionalmente espacios (\s*), luego número+b (\d{1,3}b)
    pattern = re.compile(r"^( *\d{1,3}b)", flags=re.MULTILINE)

    def replacer(match):
        length = len(match.group(0))  # longitud del match (espacios + número+b)
        return " " * length

    text = pattern.sub(replacer, text)

    # Remove split footnotes
    text = remove_split_footnotes(text)

    # Remove empty lines created by above removals
    # text = re.sub(r"\n\s*\n", "\n", text)

    # Reemplaza 3 o más saltos de línea (con posibles espacios) por solo un salto de línea
    # text = re.sub(r"\n(?:\s*\n){2,}", "\n", text)

    # Save text for debbuging
    with open(TXT_INTERMEDIATE_PARSED, "w", encoding="utf-8") as f:
        f.write(text)

    return text


def split_epistles(clean_text: str):
    """
    Splits letters using the headings: Book <RomanNumber>. and Epistle <RomanNumber>.
    Names files as epistle_<book_num>_<epistle_num>.txt
    """

    book_pattern = re.compile(r"^\s*Book\s+([IVXLCDM]+)\.", re.MULTILINE | re.IGNORECASE)
    epistle_pattern = re.compile(r"^\s*Epistle\s+([IVXLCDM]+)\.", re.MULTILINE | re.IGNORECASE)

    # Encuentra todas las ocurrencias de libros y epístolas con sus posiciones
    books = list(book_pattern.finditer(clean_text))
    epistles = list(epistle_pattern.finditer(clean_text))

    print(f"DEBUG: Found {len(books)} books")
    print(f"DEBUG: Found {len(epistles)} epistles")

    if not epistles:
        return

    # Índices de epístolas para cortar
    indices = [e.start() for e in epistles] + [len(clean_text)]

    # Puntero para libros
    current_book_index = 0
    current_book_pos = books[0].start() if books else -1
    current_book_num = roman_to_int(books[0].group(1)) if books else 0

    for i in range(len(epistles)):
        # Avanzar el puntero de libro si la epístola está después del siguiente libro
        while (current_book_index + 1 < len(books) and
               books[current_book_index + 1].start() < epistles[i].start()):
            current_book_index += 1
            current_book_pos = books[current_book_index].start()
            current_book_num = roman_to_int(books[current_book_index].group(1))

        start = indices[i]
        end = indices[i + 1]
        block = clean_text[start:end].strip()

        epistle_roman = epistles[i].group(1)
        epistle_num = roman_to_int(epistle_roman)

        filename = OUT_DIR / f"epistle_{current_book_num:02}_{epistle_num:03}.txt"
        filename.write_text(block, encoding="utf-8")

        # first_line = block.splitlines()[0] if block.splitlines() else "<empty>"
        # print(f"✓ Written {filename}  -- heading: {first_line}")


def main():
    print("→ Convirtiendo PDF a texto...")
    extract_pdf_to_text()

    print("→ Leyendo texto generado...")
    raw_text = Path(TXT_INTERMEDIATE).read_text(encoding="utf-8")

    print("→ Limpiando texto...")
    clean_text = clear_text(raw_text)

    print("→ Dividiendo epístolas...")
    split_epistles(clean_text)

    print("✔ Terminado.")


if __name__ == "__main__":
    main()
