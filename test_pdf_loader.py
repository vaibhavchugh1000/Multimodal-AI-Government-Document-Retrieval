from pdf_loader import load_pdf


pdf_path = "data/documents/doc202112201.pdf"

pages = load_pdf(pdf_path)

"""

print("\n========== PDF LOADER RESULT ==========\n")


for page in pages:

    print("Page:", page["page_number"])
    print("Document:", page["document_name"])
    print("Text Source:", page["text_source"])
    print("Has Images:", page["has_images"])
    print("Image Count:", page["image_count"])

    print("\nExtracted Text:")
    print(page["text"])

    print("\n--------------------------------------\n")
    
"""