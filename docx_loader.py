from docx import Document
from pathlib import Path


def load_docx(docx_path) : 
    
    reader=Document(docx_path)
    document_name=Path(docx_path).name
    document_id=Path(docx_path).stem
    
    
    paragraphs=list()
    for (paragraph_number,paragraph) in enumerate(reader.paragraphs,start=1):
        
        text=paragraph.text
        if text and text.strip(): 
           paragraphs.append({"text" : text,
                              "paragraph_number" : paragraph_number,
                              "document_name" : document_name,
                              "document_id" : document_id,
                              "document_path" : str(docx_path),
                              "document_type" : "docx"})
        
    print("successfully loaded docx file : ",docx_path)
    return paragraphs