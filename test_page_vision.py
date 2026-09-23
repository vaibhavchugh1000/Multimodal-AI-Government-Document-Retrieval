import pymupdf
from vision_processor import analyse_image


PDF_PATH="data/documents/doc202112201.pdf"
PROMPT="""
Analyze this complete page from a government document.

Understand the page as a whole, including:

1. The purpose of the document/page.
2. Important text and information visible on the page.
3. Tables and their relationships between rows and columns.
4. Names, designations, dates, postings, and assignments.
5. Any important handwritten annotations.
6. The overall meaning of the information on the page.

Pay attention to the spatial and structural relationship between
the different parts of the page.

Do not invent information that is not visible.

Return a concise but informative textual description suitable
for storing and retrieving this information later.
"""

document=pymupdf.open(PDF_PATH)

try : 
    
    page=document[2]
    
    pix_map=page.get_pixmap(dpi=200)
    image_bytes=pix_map.tobytes("png")
    
    result=analyse_image(image_bytes,PROMPT)
    
    print("-----------------------VISION_OUTPUT-----------------------------")
    print(result)
finally : 
    document.close()