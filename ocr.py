# Pipeline - 
# Download PDF
# Convert PDF to Image
# Extract Text from Image

import os
import requests
import pdf2image
import easyocr

def download_pdf(url):
    response = requests.get(url)
    with open("file.pdf", "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def convert_pdf_to_image():
    pages = pdf2image.convert_from_path("file.pdf", 500)
    for i, page in enumerate(pages):
        page.save(f'page_{i}.jpg', 'JPEG')
    return len(pages)

def extract_text_from_image():
    reader = easyocr.Reader(['en'])
    text = ""
    for i in range(convert_pdf_to_image()):
        output = reader.readtext(f'page_{i}.jpg')
        for data in output:
            text += data[1] + " "
        os.remove(f"page_{i}.jpg")
    os.remove("file.pdf")
    print("Text extracted successfully!")
    return text

def read_pdf(url):
    download_pdf(url)
    return extract_text_from_image()