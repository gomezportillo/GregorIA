import re
import subprocess
from pathlib import Path

BASE_PATH = "letters/epistolarum/"
PDF_INPUT = BASE_PATH + "Registri_Epistolarum.pdf"
TXT_INTERMEDIATE = BASE_PATH + "txt/epistolarum.txt"
OUT_DIR = Path(BASE_PATH + "txt/")


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


def basic_clean(text: str) -> str:
    """Light cleaning, non-destructive."""
    # Remove separator lines like ----- or ______
    text = re.sub(r"^[\-\=_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Remove superindex characters ¹²³⁴...
    text = re.sub(r"[¹²³⁴⁵⁶⁷⁸⁹⁰]", "", text)

    # Remove very common header/footer lines if they repeat (placeholder pattern)
    text = re.sub(r"^Page \\d+.*$", "", text, flags=re.MULTILINE)

    # Remove any line containing 'Philip Schaff' (headers)
    text = re.sub(r"^.*Philip Schaff.*$", "", text, flags=re.MULTILINE | re.IGNORECASE)

    # Remove lines that only contain a number (page numbers)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Remove blocks of footnotes in the text.
    pattern = re.compile(
        r"(?:\n|\A)"  # start at a newline or start of text
        r"( {7}\d{1,4} .*(?:\n"  # line starting with 7 spaces, number, space, text + newline
        r"(?:[^\S\r\n]*\S.*\n)*"  # 0 or more continuation lines (non-empty lines with optional leading spaces)
        r"\n)+)",  # block ends at empty line (double newline)
        flags=re.MULTILINE,
    )
    text = pattern.sub("\n", text)

    # Buscar al principio de línea (^), opcionalmente espacios (\s*), luego número+b (\d{1,3}b)
    pattern = re.compile(r"^( *\d{1,3}b)", flags=re.MULTILINE)

    def replacer(match):
        length = len(match.group(0))  # longitud del match (espacios + número+b)
        return " " * length

    text = pattern.sub(replacer, text)

    # Remove empty lines created by above removals
    # text = re.sub(r"\n\s*\n", "\n", text)

    # Reemplaza 3 o más saltos de línea (con posibles espacios) por solo un salto de línea
    text = re.sub(r"\n(?:\s*\n){2,}", "\n", text)

    return text


def split_epistles(clean_text: str):
    """
    Splits letters using the headings: Epistle XXX.
    """

    # Regex: ^Epistle <romannumerals> [optional dot]  (multiline & case-insensitive)
    epistle_pattern = re.compile(r"^\s*Epistle\s+[IVXLCDM]+\.", re.MULTILINE | re.IGNORECASE)

    matches = list(epistle_pattern.finditer(clean_text))
    print(f"DEBUG: Found {len(matches)} epistle headings.")

    if not matches:
        return

    # Build indices (start positions) for slicing
    indices = [m.start() for m in matches] + [len(clean_text)]

    for i in range(len(indices) - 1):
        start = indices[i]
        end = indices[i + 1]
        block = clean_text[start:end].strip()

        out_file = OUT_DIR / f"epistle_{i + 1:03}.txt"
        out_file.write_text(block, encoding="utf-8")

        # show the actual heading written (first line)
        first_line = block.splitlines()[0] if block.splitlines() else "<empty>"
        # print(f"✓ Written {out_file}  -- heading: {first_line}")


def main():
    print("→ Convirtiendo PDF a texto...")
    extract_pdf_to_text()

    print("→ Leyendo texto generado...")
    raw_text = Path(TXT_INTERMEDIATE).read_text(encoding="utf-8")

    print("→ Limpiando texto...")
    clean_text = basic_clean(raw_text)

    print("→ Dividiendo epístolas...")
    split_epistles(clean_text)

    print("✔ Terminado.")


if __name__ == "__main__":
    main()
