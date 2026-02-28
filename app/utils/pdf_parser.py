import io
import PyPDF2

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from a PDF file provided as bytes.
    """
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        extracted = page.extract_text()
        if extracted:
            text += extracted + " "
    return text.strip()
