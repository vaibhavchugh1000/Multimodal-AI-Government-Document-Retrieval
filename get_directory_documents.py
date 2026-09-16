from pathlib import Path

def get_documents():
   
   document_directory=Path("data/documents")
   
   documents=[]
   for file in document_directory.iterdir():
      
      if file.is_file():
         
         documents.append(file.name)
         
   return documents
         
         