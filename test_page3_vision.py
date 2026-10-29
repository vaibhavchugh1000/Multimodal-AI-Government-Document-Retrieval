import pymupdf

from vision_processor import analyse_image


PDF_PATH = "data/documents/doc202112201.pdf"


VISION_TEST_PROMPT = """
This is a page from a Government of India office-order document.

Carefully inspect the complete image, including all rows and columns
of any table present.

Answer this specific question:

Who was assigned the work of looking after the publicity of the
Ministry of Railways, Communications, Electronics & IT?

Return:

1. Officer's name
2. Officer's designation

Use only information visible in the image.

Do not guess.

If the information cannot be read clearly, say so.
"""


document = pymupdf.open(PDF_PATH)

try:

    # Page 3 = index 2 because PyMuPDF uses zero-based indexing
    page = document[2]

    images = page.get_images(full=True)

    print("Number of images on page 3:", len(images))

    for image_info in images:

        xref = image_info[0]

        image_data = document.extract_image(xref)

        image_bytes = image_data["image"]
        extension = image_data["ext"]

        if extension == "jpg" or extension == "jpeg":
            mime_type = "image/jpeg"
        else:
            mime_type = f"image/{extension}"

        result = analyse_image(
            image_bytes,
            VISION_TEST_PROMPT,
            mime_type
        )

        print("\n========================================")
        print("VISION TEST RESULT")
        print("========================================")
        print(result)

finally:

    document.close()