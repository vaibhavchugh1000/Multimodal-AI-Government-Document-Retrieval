from pypdf import PdfReader
from pathlib import Path

def load_pdf(pdf_path):
    
    
    reader=PdfReader(pdf_path)
    document_name=Path(pdf_path).name
    document_id=Path(pdf_path).stem
    
    pages=list()
    
    for (page_number,page) in enumerate(reader.pages,start=1):
        
        text=page.extract_text()
        
        if text and text.strip():
            
            pages.append({"text" : text,
                          "page_number" : page_number,
                          "document_id" : document_id,
                          "document_name" : document_name,
                          "document_path" : str(pdf_path),
                          "document_type" : "pdf",
                    })
    
    print("successfully loaded pdf :",pdf_path)      
    return pages