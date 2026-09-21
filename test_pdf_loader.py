from pdf_loader import load_pdf
from source_checker import containsScannedpages
import os
from pathlib import Path

pdf_paths = os.listdir("data/documents")

scanned_pdfs=list()
for pdf_path in pdf_paths : 
    
    value=containsScannedpages("data/documents/"+pdf_path)
    
    if value :
        scanned_pdfs.append(Path(pdf_path).stem)
        
print("names of scanned pdfs : ")
for scanned_pdf in scanned_pdfs : 
    
    print(scanned_pdf)
    
print("count of scanned pdfs = ",len(scanned_pdfs))

    