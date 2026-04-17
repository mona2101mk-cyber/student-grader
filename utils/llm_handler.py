# utils/llm_handler.py
import requests
import json
import streamlit as st
import re

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "mistral"  # or "llama2"

def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

@st.cache_data
def grade_with_ollama(student_answer, reference_text, question, accuracy_threshold, max_marks):
    """
    Grade student answer using local Ollama LLM
    
    Args:
        student_answer: Student's answer text
        reference_text: Reference material text
        question: Question being answered
        accuracy_threshold: Minimum accuracy %
        max_marks: Maximum marks for the question
    
    Returns:
        Dictionary with score, feedback, strengths, missing_points
    """
    
    # Check if Ollama is running
    if not check_ollama_connection():
        raise Exception(
            "❌ Ollama is not running!\n\n"
            "Please start Ollama first:\n"
            "1. Install from https://ollama.ai\n"
            "2. Run: ollama pull mistral\n"
            "3. Run: ollama serve"
        )
    
    # Prepare the prompt
    prompt = f"""You are an expert teacher evaluating a student's answer.

QUESTION: {question}

STUDENT'S ANSWER:
{student_answer}

REFERENCE MATERIAL (from textbook):
{reference_text[:2000]}  # Limit reference to avoid token overflow

EVALUATION CRITERIA:
- Maximum Marks: {max_marks}
- Minimum Accuracy Required: {accuracy_threshold}%
- Evaluate on: Correctness, Completeness, Clarity

Please evaluate and provide response in this exact JSON format:
{{
    "score": <integer between 0 and {max_marks}>,
    "feedback": "<2-3 sentence evaluation>",
    "strengths": "<what the student did well>",
    "missing_points": "<what was missing or incorrect>",
    "justification": "<why this score was given>"
}}

Return ONLY the JSON, no other text."""
    
    try:
        # Call Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3  # Lower temperature for consistent grading
            },
            timeout=60
        )
        
        response.raise_for_status()
        result_text = response.json()['response']
        
        # Parse JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            grading_result = json.loads(json_match.group())
        else:
            grading_result = json.loads(result_text)
        
        return {
            "score": min(grading_result.get("score", 0), max_marks),
            "feedback": grading_result.get("feedback", "No feedback"),
            "strengths": grading_result.get("strengths", ""),
            "missing_points": grading_result.get("missing_points", ""),
            "justification": grading_result.get("justification", "")
        }
    
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Is it running on localhost:11434?")
    except json.JSONDecodeError:
        raise Exception("Failed to parse LLM response. Try again.")
    except Exception as e:
        raise Exception(f"LLM grading failed: {str(e)}")