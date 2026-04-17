# utils/similarity_handler.py
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

@st.cache_resource
def load_embedding_model():
    """Load pre-trained embedding model (runs locally, no API)"""
    return SentenceTransformer('all-MiniLM-L6-v2')  # ~22MB, fast

def calculate_similarity(student_answer, reference_text):
    """
    Calculate semantic similarity between student answer and reference
    
    Args:
        student_answer: Student's answer text
        reference_text: Reference material
    
    Returns:
        Similarity score (0-100)
    """
    try:
        model = load_embedding_model()
        
        # Create embeddings
        student_embedding = model.encode(student_answer, convert_to_tensor=True)
        reference_embedding = model.encode(reference_text, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            [student_embedding.cpu().numpy()],
            [reference_embedding.cpu().numpy()]
        )[0][0]
        
        # Convert to percentage
        similarity_score = max(0, min(100, similarity * 100))
        
        return similarity_score
    
    except Exception as e:
        raise Exception(f"Similarity calculation failed: {str(e)}")

def extract_reference_content(reference_text, question):
    """Extract most relevant content from reference material for a question"""
    # Simple approach: find paragraphs containing key terms from question
    keywords = question.lower().split()
    relevant_content = []
    
    for paragraph in reference_text.split('\n\n'):
        if any(keyword in paragraph.lower() for keyword in keywords):
            relevant_content.append(paragraph)
    
    return ' '.join(relevant_content[:1000])  # Limit to 1000 chars