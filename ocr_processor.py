# ocr_processor module

import io

import pymupdf
import pytesseract

from PIL import Image


def ocr_image(image_bytes):

    image = Image.open(io.BytesIO(image_bytes))

    text = pytesseract.image_to_string(image)

    return text


def ocr_pdf_page(pdf_path, page_number=0, dpi=300):

    document = pymupdf.open(pdf_path)

    try:
        
        page = document[page_number]

        pixmap = page.get_pixmap(dpi=dpi)

        image_bytes = pixmap.tobytes("png")

        text = ocr_image(image_bytes)

        return text

    finally:

      document.close()