# test_page3_fullpage_vision.py

import pymupdf
from vision_processor import analyse_image


PDF_PATH = "data/documents/doc202112201.pdf"


VISION_TEST_PROMPT = """
This is a complete page from a Government of India office-order document.

Carefully inspect the entire page, including all tables, rows, columns,
names, designations, ministries, and their relationships.

Answer this specific question:

Who was assigned the work of looking after the publicity of the
Ministry of Railways, Communications, Electronics & IT?

Return:

1. Officer's name
2. Officer's designation

Pay particular attention to the relationship between the ministry/
portfolio and the officer assigned to it.

Use only information visible on this page.

Do not guess.

If the information cannot be read clearly, say so.
"""


document = pymupdf.open(PDF_PATH)

try:

    # Page 3 -> zero-based index 2
    page = document[2]

    # Render the COMPLETE page at 300 DPI
    pixmap = page.get_pixmap(dpi=300)

    # Convert rendered page into PNG bytes
    image_bytes = pixmap.tobytes("png")

    print("========================================")
    print("FULL PAGE VISION TEST")
    print("========================================")

    print("Page number: 3")
    print("Rendering DPI: 300")
    print("Image format: PNG")
    print("Image size:", len(image_bytes), "bytes")

    # Send the COMPLETE PAGE to Vision
    result = analyse_image(
        image_bytes,
        VISION_TEST_PROMPT,
        "image/png"
    )

    print("\n========================================")
    print("FULL PAGE VISION TEST RESULT")
    print("========================================")

    print(result)

finally:

    document.close()