from PIL import Image


image=Image.open("C:\\Users\\ADMIN\\OneDrive\\Documents\\College\\Sem-7\\subjects\\Major Project\\multimodal-government-rag\\ocr_test_image.png").convert("RGB")

image.save("data/documents/scanned_test_document.pdf",
    "PDF",
    resolution=300.0)

print("Scanned test PDF created successfully.")