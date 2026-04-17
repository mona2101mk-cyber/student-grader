# utils/ocr_handler.py
import streamlit as st
from pdf2image import convert_from_bytes
import io

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    try:
        import pytesseract
        from PIL import Image
        TESSERACT_AVAILABLE = True
    except ImportError:
        TESSERACT_AVAILABLE = False

@st.cache_resource
def initialize_ocr():
    """Initialize OCR engine"""
    if PADDLE_AVAILABLE:
        return PaddleOCR(use_angle_cls=True, lang='en'), "paddle"
    elif TESSERACT_AVAILABLE:
        return pytesseract, "tesseract"
    else:
        raise Exception("No OCR engine available. Install: pip install paddleocr OR pytesseract")

@st.cache_data
def extract_handwritten_text(pdf_file):
    """
    Extract handwritten text from PDF using OCR
    
    Args:
        pdf_file: Streamlit uploaded PDF file
    
    Returns:
        Extracted text from handwritten content
    """
    try:
        ocr_engine, engine_type = initialize_ocr()
        
        # Convert PDF to images
        images = convert_from_bytes(pdf_file.read())
        
        extracted_text = ""
        
        if engine_type == "paddle":
            for idx, image in enumerate(images):
                st.info(f"Processing page {idx + 1}/{len(images)}...")
                result = ocr_engine.ocr(image, cls=True)
                
                for line in result:
                    for word_info in line:
                        text = word_info[1][0]
                        confidence = word_info[1][1]
                        
                        # Only include high-confidence extractions
                        if confidence > 0.3:
                            extracted_text += text + " "
                    extracted_text += "\n"
        
        elif engine_type == "tesseract":
            for idx, image in enumerate(images):
                st.info(f"Processing page {idx + 1}/{len(images)}...")
                text = pytesseract.image_to_string(image)
                extracted_text += text + "\n"
        
        if not extracted_text.strip():
            raise ValueError("No text detected in images using OCR")
        
        return extracted_text
    
    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")