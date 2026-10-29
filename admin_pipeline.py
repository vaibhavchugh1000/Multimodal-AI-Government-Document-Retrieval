#admin_pipeline module

from pathlib import Path
from pdf_loader import load_pdf
from docx_loader import load_docx
from txt_loader import load_txt
from cleaner import clean_records
from chunker import chunk_records
from embedding_model import create_embeddings
from vector_store import add_documents
from vector_store import collection


def process_document(document_path):
    
    extension=Path(document_path).suffix.lower()
    
    document_id=Path(document_path).stem
    
    existing=collection.get(where={
        "document_id" : document_id
    },limit=1)
    
    if existing["ids"]:
        
        print("document already exists in the vector_db")
        
        return {
            
           "status" : "skipped",
            "document_name" : Path(document_path).name,
            "chunks_created": 0,
            "message" : "document already exists in the vector_db",
            "success" : False
            
        }
    
    document_type=""
    if extension==".pdf" : 
        print("calling load_pdf() : ")
        records=load_pdf(document_path)
        document_type="pdf"
    elif extension==".txt" : 
        print("calling load_txt() : ")
        records=load_txt(document_path)
        document_type="txt"
    elif extension==".docx":
        print("calling load_docx() : ")
        records=load_docx(document_path)
        document_type="docx"
        
    else : 
        raise ValueError("invalid extension")
    
    
    if document_type == "pdf" : 
        
        for record in records : 
    
                print("Page:", record["page_number"])
                print("Page type:", record["page_type"])
                print("Text source:", record["text_source"])
                print("Has images:", record["has_images"])
                print("Image count:", record["image_count"])
                print("Drawing count:", record["drawing_count"])
                
    cleaned_records=clean_records(records)
    try :
      for cleaned_record in cleaned_records : 
        
        if len(cleaned_record) == 0: 
            
            raise Exception("empty record found after cleaning")
        
    except Exception as e: 
        print(e)
           
    chunks=chunk_records(cleaned_records)
    try : 
      if len(chunks) == 0: 
        raise Exception("chunks not created") 
    
    except Exception as e:
        print(e)   
    texts=[chunk["text"] for chunk in chunks]
    
    
    embeddings=create_embeddings(texts)
    
    add_documents(chunks,embeddings)
    
    print("document processed and stored in vector db successfully")
    print("total vector count present in vector_db = ",collection.count())
    
    return {
        "document_name": str(Path(document_path).name),
        "chunks_created": len(chunks),
        "success" : True
    }
    
        
    
       