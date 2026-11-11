# Hindi Textbook OCR to Shusha

A local Python application that extracts Hindi text from clear textbook images and converts corrected Unicode Hindi into the legacy Shusha font encoding.

The complete workflow runs on the user's computer.

## Demo
<img width="1205" height="658" alt="Screenshot 2026-11-12 011126" src="https://github.com/user-attachments/assets/7e31658b-bac1-4ea8-be45-18e0fae9cc5c" />

<img width="507" height="386" alt="Screenshot 2026-11-12 011142" src="https://github.com/user-attachments/assets/2df6c2d0-a692-45b6-916c-b5161a886c61" />


## Features

- Upload a clear Hindi textbook image in JPG or PNG format.
- Extract Unicode Hindi using Tesseract OCR and its Hindi model.
- Correct OCR mistakes in an editable text area.
- Download the corrected Unicode Hindi text.
- Convert Hindi to Shusha with a hand-written mapping and ordering rules.
- Handle matras, supported half letters, conjuncts, numbers, and punctuation.
- Preserve unsupported Hindi instead of silently deleting it.
- Download the result as a Word document or raw Shusha keys.
- Process images locally without sending them to an external OCR service.

## How it works

```text
Textbook image
      ↓
Tesseract Hindi OCR
      ↓
Editable Unicode Hindi
      ↓
Unicode-to-Shusha converter
      ↓
Word document or raw Shusha keys
```

The application first extracts standard Unicode Hindi. The user can correct the text before conversion. The converter then reads Hindi in syllable groups and applies the Shusha mapping.

For example:

```text
भारत → Baart
```

`Baart` displays as `भारत` when a compatible Shusha font is applied.

## Technologies

- Python
- Streamlit
- Tesseract OCR
- pytesseract
- Pillow
- python-docx

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or newer
- Internet access during the first setup
- A compatible Shusha font for displaying the converted output

## Installation

Open PowerShell in the project folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

The setup script:

1. Creates a local Python environment in `.venv`.
2. Installs the packages from `requirements.txt`.
3. Installs Tesseract through Windows Package Manager if it is missing.
4. Downloads the official Hindi OCR model.
5. Checks that Hindi OCR is ready.

The local Python environment and Hindi model remain inside the project folder.

### Install the Shusha font

Download and install a compatible Shusha font before opening the converted Word document. The font is available from the [Abhivyakti Shusha font page](https://www.abhivyakti-hindi.org/abhi/hindi_shusha_fonts_dl_help.htm).

Open the downloaded `.ttf` file in Windows, select **Install**, and reopen Word if it was already running.

## Run the application

After setup, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Open the local address displayed in PowerShell, normally:

```text
http://127.0.0.1:8501
```

Keep PowerShell open while using the app. Press `Ctrl+C` to stop it.

## Using the application

1. Choose **Your image** and upload a JPG or PNG page.
2. Click **Extract Hindi text**.
3. Compare the extracted text with the image and correct any mistakes.
4. Click **Convert to Shusha**.
5. Review any conversion warnings.
6. Download the Word document or raw Shusha keys.

The **Sample page** option uses the included demonstration image. **Text only** allows direct conversion of pasted Hindi without OCR.

The Word download is recommended because it remembers which sections require Shusha and which must remain in a Unicode font. Plain `.txt` files cannot store font information.

## Project structure

```text
hindi-to-shusha/
├── app.py                    Streamlit interface and user workflow
├── ocr.py                    Image validation and Hindi OCR
├── converter.py              Unicode-to-Shusha conversion rules
├── shusha_map.py             Shusha character mapping tables
├── export.py                 Word document generation
├── run_ocr.py                Optional command-line OCR helper
├── setup.ps1                 First-time Windows setup
├── start.ps1                 Application launcher
├── requirements.txt          Python dependencies
├── .streamlit/
│   └── config.toml           Streamlit appearance and settings
├── docs/
│   └── images/               README screenshots
├── samples/
│   ├── demo_hindi.png        Clear Hindi sample image
│   └── demo_hindi.txt        Correct text for the sample
└── tests/
    ├── test_app.py           Interface workflow checks
    ├── test_converter.py     Conversion behavior checks
    ├── test_exports.py       Word export checks
    └── test_ocr.py           Image and OCR checks
```

## Main files

### `app.py`

Builds the interface, stores the current text between button clicks, prevents old results from being downloaded after an edit, and connects OCR, conversion, preview, and downloads.

### `ocr.py`

Finds the local Tesseract installation and Hindi model. It validates JPG and PNG images, applies phone-camera orientation, and returns editable Unicode Hindi.

### `shusha_map.py`

Contains mappings for vowels, consonants, matras, marks, numbers, half forms, supported conjuncts, and selected nukta letters. The mapping targets Shusha 1.5.

### `converter.py`

Reads the Hindi text in syllable groups. It chooses full letters, half forms, or documented conjuncts and moves the short `ि` matra before the relevant group. Unverified combinations remain Unicode and are reported for review.

### `export.py`

Creates a Word document with separate font runs. Converted keys use Shusha, while English and unsupported Hindi use a Unicode font.

## Command-line OCR

OCR can also be run without opening the Streamlit app:

```powershell
.\.venv\Scripts\python.exe run_ocr.py
```

To process another image:

```powershell
.\.venv\Scripts\python.exe run_ocr.py "path\to\page.jpg" --output "hindi.txt"
```

## Tests

Run the automated checks with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The test suite covers OCR input handling, real sample extraction, Unicode-to-Shusha conversion, mixed English and Hindi, unsupported character preservation, Word formatting, and interface state.

## Limitations

- Designed for clear printed Hindi; handwriting and noisy photographs are outside the current scope.
- Processes one JPG or PNG image at a time.
- Does not reproduce the original textbook layout.
- Different Shusha font versions may use different mappings.
- Some unverified combinations, including reph and `ढ़`, remain Unicode and produce a warning.
- The Shusha font must be installed on every computer that opens the converted Word document.

## Mapping reference

The converter starts from the published [Shusha 1.5 mapping by James Kass](https://www.unicode.org/mail-arch/unicode-ml/y2001-m11/0258.html), with additional rule-based handling for matras and documented joined forms.
