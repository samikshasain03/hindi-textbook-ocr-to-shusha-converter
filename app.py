"""A local screen for reading textbook pages and downloading Shusha text."""

import base64
import hashlib
import html
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

from converter import convert_to_shusha
from export import make_shusha_docx
from ocr import extract_hindi_text, get_ocr_status


PROJECT_FOLDER = Path(__file__).resolve().parent
FONT_PATH = PROJECT_FOLDER / "assets" / "fonts" / "Shusha.ttf"

st.set_page_config(page_title="Hindi to Shusha", page_icon="📖", layout="wide")
st.title("Hindi to Shusha")
st.write("Read a clear textbook page, check the Hindi, and download the Shusha version.")

# Keep the user's edits between button clicks. Streamlit reruns this file
# after an interaction, but session_state remembers these values.
if "hindi_text" not in st.session_state:
    st.session_state.hindi_text = ""

source_choice = st.radio(
    "Start with", ["Your image", "Sample page", "Text only"], horizontal=True
)
image_bytes = None
if source_choice == "Your image":
    uploaded = st.file_uploader("Choose a textbook page", type=["jpg", "jpeg", "png"])
    if uploaded is not None:
        image_bytes = uploaded.getvalue()
elif source_choice == "Sample page":
    sample = PROJECT_FOLDER / "samples" / "demo_hindi.png"
    if sample.exists():
        image_bytes = sample.read_bytes()
    else:
        st.info("The sample image is missing. Upload a page or choose Text only.")

# A different page should not accidentally inherit another page's results.
source_id = source_choice + (hashlib.sha256(image_bytes).hexdigest() if image_bytes else "")
if st.session_state.get("source_id") != source_id:
    st.session_state.source_id = source_id
    st.session_state.hindi_text = ""
    st.session_state.pop("conversion", None)
    st.session_state.pop("converted_source", None)

left, right = st.columns(2, gap="large")
with left:
    st.subheader("1. Read the page")
    image_ready = False
    if image_bytes:
        try:
            with Image.open(BytesIO(image_bytes)) as image:
                if image.format not in {"JPEG", "PNG"}:
                    raise ValueError("Please choose a JPG or PNG image.")
                preview = ImageOps.exif_transpose(image).convert("RGB")
                st.image(preview, caption="Your page", use_container_width=True)
            image_ready = True
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as error:
            st.error(f"This page could not be opened. {error}")
    elif source_choice != "Text only":
        st.info("Choose a clear JPG or PNG image to begin.")
    else:
        st.write("Paste your Hindi text in the box on the right.")

    status = get_ocr_status()
    if not status["ready"] and source_choice != "Text only":
        st.info("Text extraction needs setup.ps1 to finish first. You can still use Text only.")
        with st.expander("Setup details"):
            st.write(status["message"])

    if st.button("Extract Hindi text", key="extract", disabled=not image_ready or not status["ready"], type="primary"):
        try:
            with st.spinner("Reading the Hindi text…"):
                text = extract_hindi_text(BytesIO(image_bytes))
            st.session_state.hindi_text = text
            st.session_state.pop("conversion", None)
            if not text:
                st.warning("No text was found. Try a closer image of the printed words.")
        except (ValueError, RuntimeError, OSError) as error:
            st.error(str(error))

with right:
    st.subheader("2. Check the Hindi")
    edited_text = st.text_area(
        "Correct any mistakes before converting", key="hindi_text", height=350,
        placeholder="Extract text from a page, or paste Hindi here…"
    )
    st.caption("Check matras, joined letters, numbers, and paragraph breaks against the page.")
    st.download_button(
        "Download Hindi text", data=edited_text.encode("utf-8"),
        file_name="hindi_text.txt", mime="text/plain; charset=utf-8",
        disabled=not edited_text.strip()
    )
    if st.button("Convert to Shusha", key="convert", disabled=not edited_text.strip(), type="primary"):
        st.session_state.conversion = convert_to_shusha(edited_text)
        st.session_state.converted_source = edited_text

# Hide older output after an edit, so downloads never contain stale text.
result = st.session_state.get("conversion")
if result and st.session_state.get("converted_source") != edited_text:
    st.info("The Hindi text has changed. Click Convert to Shusha to update the download.")
elif result:
    st.divider()
    st.subheader("3. Download the result")
    if result.warnings:
        st.warning("Some parts need checking. They have been kept readable in the Word file.")
        with st.expander("See the parts to check"):
            for warning in result.warnings:
                st.write(warning)

    # Embed the local font for preview only; no font is downloaded from a server.
    if FONT_PATH.exists():
        encoded_font = base64.b64encode(FONT_PATH.read_bytes()).decode("ascii")
        preview_parts = []
        for part in result.runs:
            family = "ShushaPreview" if part.font == "shusha" else "Mangal, 'Nirmala UI', sans-serif"
            preview_parts.append(f'<span style="font-family:{family}">{html.escape(part.text)}</span>')
        st.markdown(
            f"<style>@font-face{{font-family:ShushaPreview;src:url(data:font/ttf;base64,{encoded_font})}}"
            ".shusha-preview{white-space:pre-wrap;font-size:24px;line-height:1.8;padding:20px;"
            "border:1px solid #ddd;border-radius:8px}</style>"
            + '<div class="shusha-preview">' + "".join(preview_parts) + "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Add assets/fonts/Shusha.ttf to see the Shusha preview.")

    st.caption("Word is recommended: it remembers which font each part needs. Install the matching Shusha font before opening the file; see assets/fonts/README.md.")
    st.download_button(
        "Download Word file (.docx)", data=make_shusha_docx(result),
        file_name="shusha_text.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )
    with st.expander("Raw Shusha keys (.txt)"):
        st.write("These keys may look like English until the Shusha font is applied. Plain text cannot remember different fonts; use Word for mixed text or parts marked for checking.")
        st.text_area("Encoded text", value=result.text, height=180, disabled=True)
        st.download_button(
            "Download raw keys", data=result.text.encode("utf-8"),
            file_name="shusha_keys.txt", mime="text/plain; charset=utf-8",
        )

with st.expander("How to use this app"):
    st.write("1. Upload a clear, upright textbook page.\n\n2. Click Extract Hindi text.\n\n3. Correct the text against the image.\n\n4. Click Convert to Shusha.\n\n5. Download the Word file and open it with the matching Shusha font installed.")
    st.caption("Pages are processed on this computer. No OCR API or account is required.")
