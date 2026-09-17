from PIL import Image, ImageDraw, ImageFont


# Create a white image
image = Image.new("RGB", (1000, 300), "white")

# Create drawing object
draw = ImageDraw.Draw(image)

# Add text to the image
text = """Government of India
Citizen Services Portal
Digital Document Retrieval System"""

# Draw the text
draw.text((50, 50), text, fill="black")

# Save the image
image.save("ocr_test_image.png")

print("Test image created successfully.")