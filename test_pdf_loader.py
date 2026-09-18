from pdf_loader import load_pdf
from source_checker import containsScannedpages

pdf_path = "data/documents/citizen-charter-2024-25-1.pdf"


pages = load_pdf(pdf_path)
value=containsScannedpages(pdf_path)

print("\n========== PDF LOADER TEST ==========\n")

print("Total pages processed:", len(pages))

for page in pages:
    print("\n-----------------------------------")
    print("Page:", page["page_number"])
    print("Characters extracted:", len(page["text"]))
    print("Preview:")
    print("page text source : ",page["text_source"])
    print(page["text"][:300])
    
print("is Document scanned : ",value)