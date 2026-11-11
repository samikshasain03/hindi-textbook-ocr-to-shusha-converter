"""Optional command-line helper; the normal screen is launched by start.ps1."""

import argparse
from pathlib import Path

from ocr import extract_hindi_text


if __name__ == "__main__":
    project_folder = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Extract Hindi from one textbook image.")
    parser.add_argument("image", nargs="?", type=Path,
                        default=project_folder / "samples" / "demo_hindi.png")
    parser.add_argument("--output", type=Path, default=project_folder / "extracted_hindi.txt")
    arguments = parser.parse_args()

    try:
        # Call the OCR function, then save Hindi using UTF-8 text encoding.
        text = extract_hindi_text(arguments.image)
        arguments.output.write_text(text, encoding="utf-8")
    except (RuntimeError, ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    print(f"Saved extracted text to: {arguments.output}")
    if not text:
        print("No text was found. Try a closer image of the text area.")
