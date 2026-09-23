from pdf_loader import load_pdf


PDF_PATH = r"data/documents/EAadhaar_VaibhavChugh.pdf"


pages = load_pdf(PDF_PATH)


print("\n========================================")
print("PDF LOADER TEST COMPLETED")
print("========================================")

print("Total pages:", len(pages))


for page in pages:

    print("\n----------------------------------------")
    print("Page:", page["page_number"])
    print("Page type:", page["page_type"])
    print("Text source:", page["text_source"])
    print("Has images:", page["has_images"])
    print("Image count:", page["image_count"])
    print("Drawing count:", page["drawing_count"])
    print("Text length:", len(page["text"]))

    print("\nText preview:")
    print(page["text"][:500])