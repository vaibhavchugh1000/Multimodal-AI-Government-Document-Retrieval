from PIL import Image
import pytesseract

# Path of the image on which OCR will be performed
image_path = "ocr_test_image.png"
image=Image.open(image_path)

text=pytesseract.image_to_string(image)

print("=====OCR RESULT======")
print(text)