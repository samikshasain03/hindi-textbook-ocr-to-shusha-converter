"""a Word file download while keeping Shusha and Unicode text readable."""

from io import BytesIO

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt


def make_shusha_docx(result):
    """Return Word file bytes for a result from convert_to_shusha()."""
    document = Document()
    paragraph = document.add_paragraph()

    for part in result.runs:
        font_name = "Shusha" if part.font == "shusha" else "Mangal"
        lines = part.text.split("\n")
        for index, line in enumerate(lines):
            if index:
                paragraph = document.add_paragraph()
            if not line:
                continue
            run = paragraph.add_run(line)
            run.font.name = font_name
            run.font.size = Pt(14)

            fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
            for setting in ("ascii", "hAnsi", "eastAsia", "cs"):
                fonts.set(qn(f"w:{setting}"), font_name)

    output = BytesIO()
    document.save(output)
    return output.getvalue()
