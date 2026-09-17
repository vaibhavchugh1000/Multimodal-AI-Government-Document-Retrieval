from pdf_loader import load_pdf


pdf_path = "data/documents/citizen-charter-2024-25-1.pdf"


pages = load_pdf(pdf_path)


print("\n========== PDF LOADER TEST ==========\n")

print("Total pages processed:", len(pages))

for page in pages:
    print("\n-----------------------------------")
    print("Page:", page["page_number"])
    print("Characters extracted:", len(page["text"]))
    print("Preview:")
    print(page["text"][:300])