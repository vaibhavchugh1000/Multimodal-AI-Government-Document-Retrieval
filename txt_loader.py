from pathlib import Path


def load_txt(txt_file_path):
    
    file_id=Path(txt_file_path).stem
    file_name=Path(txt_file_path).name
    with open(txt_file_path,"r",encoding="utf-8") as f:
        
        text=f.read()
        
    
    documents=[]
    if text and text.strip() : 
        documents.append({
        "text" : text,
        "document_id" : file_id,
        "document_name" : file_name,
        "document_type" : "txt",
        "document_path" : txt_file_path
         })
        
    print("successfully loaded txt file : ",txt_file_path)
    return documents
    
    
   
        
        