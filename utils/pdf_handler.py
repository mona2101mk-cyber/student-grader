# utils/pdf_handler.py
import PyPDF2
import io
import streamlit as st

@st.cache_data
def extract_text_from_pdf(pdf_file, pages=None):
    """
    Extract text from PDF file
    
    Args:
        pdf_file: Streamlit uploaded file
        pages: Number of pages to extract (None = all)
    
    Returns:
        Extracted text
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        
        max_pages = len(pdf_reader.pages) if pages is None else min(pages, len(pdf_reader.pages))
        
        for page_num in range(max_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        if not text.strip():
            raise ValueError("No text extracted from PDF. PDF may be scanned/image-based.")
        
        return text
    
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")