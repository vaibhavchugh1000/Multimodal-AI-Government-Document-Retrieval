from admin_pipeline import process_document


pdf_path = "data/documents/scanned_test_document.pdf"


result = process_document(pdf_path)


print("\n========== ADMIN OCR PIPELINE TEST ==========\n")

print("Result:")
print(result)