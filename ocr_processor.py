import pymupdf
import pytesseract
from PIL import Image


def ocr_image(image):
    """
    Perform OCR on a PIL image using Tesseract.
    """

    text = pytesseract.image_to_string(image)

    return text


def ocr_pdf_page(pdf_path, page_number=0, dpi=300):
    """
    Render a PDF page as an image and perform OCR on that page.

    Parameters:
        pdf_path: Path to the PDF file.
        page_number: Zero-based page number.
        dpi: Resolution used to render the PDF page.

    Returns:
        Extracted text from the page.
    """

    # Open the PDF
    document = pymupdf.open(pdf_path)

    try:
        # Check whether requested page exists
        if page_number < 0 or page_number >= len(document):
            raise ValueError(
                f"Invalid page number. PDF contains {len(document)} pages."
            )

        # Get the requested page
        page = document[page_number]

        # Convert PDF page into an image
        zoom = dpi / 72

        matrix = pymupdf.Matrix(zoom, zoom)

        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        # Convert rendered PDF page into a PIL image
        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples
        )

        # Perform OCR
        text = ocr_image(image)

        return text

    finally:
        # Always close the PDF
        document.close()