import pymupdf

from vision_processor import analyse_image


# Replace this with the actual PDF filename
PDF_PATH = "data/documents/doc202112201.pdf"


PROMPT = """
Analyze this image from a government document.

Describe the important information contained in the image, including:

1. The main subject or purpose of the image.
2. Any important text that contributes to its meaning.
3. Names, designations, dates, postings, or relationships visible in the image.
4. The overall meaning of the information represented.

Do not invent information that is not visible in the image.

Return a concise but informative textual description suitable
for storing and retrieving this information later.
"""


document = pymupdf.open(PDF_PATH)

try:

    # Page 3 → index 2 because Python uses zero-based indexing
    page = document[2]

    images = page.get_images(full=True)

    print("Number of embedded images:", len(images))

    if not images:
        raise ValueError("No embedded images found on page 3")

    # Take the first embedded image for our initial test
    xref = images[0][0]

    image_data = document.extract_image(xref)

    image_bytes = image_data["image"]

    print("Image extracted successfully.")
    print("Image format:", image_data["ext"])

    # Send image to Vision model
    result = analyse_image(
        image_bytes,
        PROMPT
    )

    print("\n========== VISION OUTPUT ==========\n")
    print(result)

finally:

    document.close()