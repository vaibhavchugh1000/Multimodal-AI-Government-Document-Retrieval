#pdf loader module

from ocr_processor import ocr_image
from page_classifier import inspect_page,classify_page
from vision_processor import analyse_image
import pymupdf
from pathlib import Path


IMAGE_VISION_PROMPT="""
Analyze this image from a government document.

Describe the important information contained in the image, including:

1. The main subject or purpose of the image.
2. Important text that contributes to its meaning.
3. Tables, names, designations, dates, postings, or relationships visible.
4. The overall meaning of the information represented.

Do not invent information that is not visible.

Return a concise but informative textual description suitable
for storing and retrieving this information later.
"""


PAGE_VISION_PROMPT = """
Analyze this complete page from a government document.

Understand the page as a whole, including:

1. The purpose of the document/page.
2. Important text and information visible on the page.
3. Tables and relationships between rows and columns.
4. Names, designations, dates, postings, and assignments.
5. Important handwritten annotations.
6. The overall meaning of the information on the page.

Pay attention to the spatial and structural relationships
between different parts of the page.

Do not invent information that is not visible.

Return a concise but informative textual description suitable
for storing and retrieving this information later.

"""


def set_extension(extension :str):
    
    extension=extension.lower()
    
    if extension in {"jpeg","jpg"}:
        
        return "image/jpeg"
    
    return f"image/{extension}"

def load_pdf(pdf_path : str) : 
    
    
    document=pymupdf.open(pdf_path)
    pages=list()
    document_name=Path(pdf_path).name
    document_id=Path(pdf_path).stem
    count=0
    for (page_number,page) in enumerate(document,start=1) : 
        
        
        if count==6: 
            break
        # --------------------------------------------------
        # 1. Inspect page
        # --------------------------------------------------

        page_info = inspect_page(page)

        # --------------------------------------------------
        # 2. Classify page
        # --------------------------------------------------

        page_type = classify_page(page_info)

        
        text=page.get_text().strip()
        vision_content=list()
        
        if page_type=="text" : 
            
            text_source="pdf_text"
            
        elif page_type=="image":
            
            text_source="ocr+image_vision"
            
            images=page.get_images(full=True)
            
            for image_info in images :
                
                xref=image_info[0]
                
                image_data=document.extract_image(xref)
                
                image_bytes=image_data["image"]
                extension=image_data["ext"]
                
                extension=set_extension(extension)
                ocr_text=ocr_image(image_bytes)
                
                if ocr_text and ocr_text.strip():
                    
                    vision_content.append("ocr_text : " + ocr_text.strip())
                    
                vision_result=analyse_image(image_bytes,IMAGE_VISION_PROMPT,extension)
                
                if vision_result : 
                    
                    vision_content.append("image vision description : " + vision_result)
                    
        else : 
            
            # complex page 
            text_source="pdf_text+page_vision"
            pixmap=page.get_pixmap(dpi=200)
            image_bytes=pixmap.tobytes("png")
            
            vision_result=analyse_image(image_bytes,PAGE_VISION_PROMPT,"image/png")
            
            if vision_result : 
                
                vision_content.append("page vision description : " + vision_result)
                
        
        if vision_content : 
            
            text_parts = []

            if text:
                text_parts.append(text)

            text_parts.extend(vision_content)

            text = "\n\n".join(text_parts)
        
        pages.append({

            "text": text,

            "page_number": page_number,

            "document_id": document_id,

            "document_name": document_name,

            "document_path": str(pdf_path),

            "document_type": "pdf",

            "text_source": text_source,

            "has_images": page_info["image_present"],

            "image_count": page_info["image_count"],

            "drawing_count": page_info["drawing_count"],

            "page_type": page_type
        })
        print(pages[-1])
        print()
        count=count+1

    document.close()

    print("Successfully loaded PDF:", pdf_path)

    return pages