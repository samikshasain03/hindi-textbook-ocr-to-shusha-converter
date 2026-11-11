"""Read Unicode Hindi text from clear JPG and PNG textbook images."""

import os
import shutil
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError


PROJECT_FOLDER = Path(__file__).resolve().parent


def _configure_tesseract():
    """Find Tesseract and point it to our local Hindi model."""
    # An optional custom path takes priority over the usual install folders.
    custom_path = os.environ.get("TESSERACT_CMD")
    candidates = [custom_path] if custom_path else [
        shutil.which("tesseract"),
        str(Path(os.environ.get("ProgramFiles", "C:/Program Files"))
            / "Tesseract-OCR" / "tesseract.exe"),
        str(Path(os.environ.get("LOCALAPPDATA", ""))
            / "Programs" / "Tesseract-OCR" / "tesseract.exe"),
    ]
    executable = next((path for path in candidates if path and Path(path).is_file()), None)
    if not executable:
        raise RuntimeError(
            "Tesseract was not found. Run setup.ps1 to install it. "
            "For a custom installation, set TESSERACT_CMD to tesseract.exe."
        )
    pytesseract.pytesseract.tesseract_cmd = executable

    # setup.ps1 puts Hindi data here. TESSDATA_PREFIX is more reliable than
    # --tessdata-dir on Windows when the project path contains spaces.
    data_folder = PROJECT_FOLDER / "tessdata"
    if (data_folder / "hin.traineddata").is_file():
        os.environ["TESSDATA_PREFIX"] = str(data_folder)
    config = ""
    try:
        languages = pytesseract.get_languages(config=config)
    except (OSError, pytesseract.TesseractError) as error:
        raise RuntimeError("Tesseract could not start. Run setup.ps1 again.") from error
    if "hin" not in languages:
        raise RuntimeError("The Hindi OCR model is missing. Run setup.ps1 to download it.")
    return config


def get_ocr_status():
    """Let the app explain whether Hindi OCR is ready on this computer."""
    try:
        _configure_tesseract()
        return {"ready": True, "message": "Hindi OCR is ready.",
                "executable": pytesseract.pytesseract.tesseract_cmd}
    except RuntimeError as error:
        return {"ready": False, "message": str(error), "executable": None}


def extract_hindi_text(image_source):
    """Read an image path or uploaded file and return editable Hindi text."""
    # Read the image first so an invalid upload gets a useful error message.
    try:
        with Image.open(image_source) as image:
            if image.format not in {"JPEG", "PNG"}:
                raise ValueError("Please use a JPG or PNG textbook image.")
            # Honour phone-camera orientation and use a standard colour mode.
            image = ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError) as error:
        raise ValueError("This image could not be opened. Choose a readable JPG or PNG file.") from error

    config = _configure_tesseract()
    try:
        # 'hin' selects Hindi. Default page layout detection suits textbook pages.
        text = pytesseract.image_to_string(image, lang="hin", config=config, timeout=120)
    except pytesseract.TesseractError as error:
        raise RuntimeError("Tesseract could not read this page. Check its Hindi model and try a clearer image.") from error
    except RuntimeError as error:
        raise RuntimeError("Reading the page took too long. Try cropping to the text area.") from error

    # Preserve Tesseract's internal line breaks for the user to review.
    return text.strip()
