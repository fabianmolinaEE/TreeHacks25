# Pipeline - 
# Download PDF
# Convert PDF to Image
# Extract Text from Image

import os
import dotenv
import groq
import requests
import pdf2image
import easyocr

dotenv.load_dotenv()

client = groq.Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def download_pdf(url):
    print("Downloading PDF...")
    response = requests.get(url)
    with open("file.pdf", "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print("PDF downloaded successfully!")

def convert_pdf_to_image():
    print("Converting PDF to Image...")
    pages = pdf2image.convert_from_path("file.pdf", 500)
    for i, page in enumerate(pages):
        page.save(f'page_{i}.jpg', 'JPEG')
    print("PDF converted to Image successfully!")
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

def pipeline(url):
    download_pdf(url)
    print("\n-----------------\n", extract_text_from_image())

pipeline("https://webapp4.asu.edu/bookstore/viewsyllabus/2211/17920/pdf")