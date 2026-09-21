# pdf_loader module

from pypdf import PdfReader
from pathlib import Path
from ocr_processor import ocr_image , ocr_pdf_page

def load_pdf(pdf_path):
    
    
    reader=PdfReader(pdf_path)
    document_name=Path(pdf_path).name
    document_id=Path(pdf_path).stem
    
    pages=list()
    
    for (page_number,page) in enumerate(reader.pages,start=1):
        
        text=page.extract_text()
        
        if text and text.strip():
            
            print("in PDF_TEXT branch")
            pages.append({"text" : text,
                          "page_number" : page_number,
                          "document_id" : document_id,
                          "document_name" : document_name,
                          "document_path" : str(pdf_path),
                          "document_type" : "pdf",
                          "text_source" : "pdf_text"
                    })
            
        else : 
            
            print("in OCR branch")
            # Scanned/image-based PDF page
            ocr_text = ocr_pdf_page(
                pdf_path,
                page_number=page_number - 1,
                dpi=300
            )
            
            pages.append({"text" : ocr_text,
                                      "page_number" : page_number,
                                      "document_id" : document_id,
                                      "document_name" : document_name,
                                      "document_path" : str(pdf_path),
                                      "document_type" : "pdf",
                                      "text_source"  : "ocr"
             })
    
    print("successfully loaded pdf :",pdf_path)      
    return pages