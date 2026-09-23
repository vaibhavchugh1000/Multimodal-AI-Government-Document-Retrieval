# pdf_loader module

from pathlib import Path
import pymupdf

from ocr_processor import ocr_image, ocr_pdf_page
from page_classifier import inspect_page , classify_page

def load_pdf(pdf_path):

    document = pymupdf.open(pdf_path)

    document_name = Path(pdf_path).name
    document_id = Path(pdf_path).stem

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text().strip()
        images = page.get_images(full=True)
        
        page_info=inspect_page(page)
        
        page_type=classify_page(page_info)
        
        
        print(
        f"Page {page_number}: ",
        f"page_type = {page_type}",
        f"text={page_info['text_present']}, "
        f"images={page_info['image_count']}, "
        f"drawings={page_info['drawing_count']}"
        )

        # Case 1: Page has native text and images
        if text and images:

            ocr_parts = []

            for image_info in images:

                xref = image_info[0]

                image_data = document.extract_image(xref)
                image_bytes = image_data["image"]

                ocr_text = ocr_image(image_bytes)

                if ocr_text and ocr_text.strip():
                    ocr_parts.append(ocr_text.strip())

            if ocr_parts:
                text += "\n\n" + "\n\n".join(ocr_parts)
                text_source = "pdf_text+ocr"

            else:
                text_source = "pdf_text"

        # Case 2: Page has native text only
        elif text:

            text_source = "pdf_text"

        # Case 3: Page has no native text → OCR entire page
        else:

            text = ocr_pdf_page(
                pdf_path,
                page_number=page_number - 1,
                dpi=300
            )

            text_source = "ocr"

        pages.append({
            "text": text,
            "page_number": page_number,
            "document_id": document_id,
            "document_name": document_name,
            "document_path": str(pdf_path),
            "document_type": "pdf",
            "text_source": text_source,
            "has_images": bool(images),
            "image_count": len(images)
        })

    document.close()

    print("Successfully loaded PDF:", pdf_path)

    return pages