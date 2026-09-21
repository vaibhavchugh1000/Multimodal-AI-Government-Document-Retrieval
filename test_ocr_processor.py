from ocr_processor import ocr_pdf_page


# Path to the PDF we want to test
pdf_path = "data/documents/scanned_test_document.pdf"


# Perform OCR on the first page
text = ocr_pdf_page(
    pdf_path,
    page_number=0,
    dpi=300
)


print("\n========== OCR PDF PAGE RESULT ==========\n")
print(text)