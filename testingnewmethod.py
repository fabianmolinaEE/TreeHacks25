import requests
import fitz  # PyMuPDF

def download_pdf(url, save_path):
    """Downloads a PDF from a given URL and saves it to a file."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"✅ PDF downloaded successfully: {save_path}")
    else:
        print(f"❌ Failed to download PDF. Status code: {response.status_code}")
        return None

def extract_text_pymupdf(pdf_path):
    """Extracts text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    return text

# Define the URL and file path
pdf_url = "https://web.stanford.edu/class/archive/cs/cs111/cs111.1254/lectures/10/Lecture10.pdf"
pdf_path = "lecture10.pdf"

# Download and extract text
download_pdf(pdf_url, pdf_path)
extracted_text = extract_text_pymupdf(pdf_path)

# Print extracted text
print("\n📄 Extracted Text:\n")
print(extracted_text)