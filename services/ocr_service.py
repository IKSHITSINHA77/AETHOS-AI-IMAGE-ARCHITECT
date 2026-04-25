import pytesseract
import cv2

def extract_text(image_path):

    img = cv2.imread(image_path)

    text = pytesseract.image_to_string(img)

    return text


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"