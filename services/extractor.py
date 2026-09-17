import os

import pdfplumber
from docx import Document

def extract_text_from_file(file_storage):
    if not file_storage.filename:
        filename = ""
    else:
        filename = file_storage.filename

    file_type = os.path.splitext(filename)[1].lower()

    if file_type == ".docx":
        return extract_docx(file_storage)
    if file_type == ".pdf":
            return extract_pdf(file_storage)
    if file_type == ".txt":
        return extract_txt(file_storage)

    raise ValueError(
        f"Unsupported file type '{file_type}'. The app allows only .docx, .pdf and .txt files. "
    )

def extract_docx(file_storage):
    document = Document(file_storage)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def extract_pdf(file_storage):
    full_text = []
    with pdfplumber.open(file_storage) as pdf:
         for page in pdf.pages:
              page_text = page.extract_text()
              if page_text:
                   full_text.append(page_text)
    return "\n".join(full_text)

def extract_txt(file_storage):
    raw_text = file_storage.read()
    # decoding it to a string, if the file is in bytes
    if isinstance(raw_text, bytes):
         return raw_text.decode("utf-8", errors="ignore")
    return raw_text