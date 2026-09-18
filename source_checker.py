from pypdf import PdfReader

def containsScannedpages(pdf_path) : 
    
    reader=PdfReader(pdf_path)
    
    for page in reader.pages : 
        
        text=page.extract_text()
        
        if not (text and text.strip()) : 
            
            return True
        
        
    return False