import pytesseract
from PIL import Image

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Open image
img = Image.open("error.png")

# Extract text
text = pytesseract.image_to_string(img)

print("Detected Text:")
print(text)

# Simple AI logic
if "restart the game" in text.lower():
    print("\nPossible Fix:")
    print("Try restarting the game and verifying game files.")

elif "dll" in text.lower():
    print("\nPossible Fix:")
    print("Missing DLL detected.")
    print("Install Microsoft Visual C++ Redistributable.")

else:
    print("\nNo fix found yet.")