# app.py
import streamlit as st
import os
from pathlib import Path
import sys

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.pdf_handler import extract_text_from_pdf
from utils.ocr_handler import extract_handwritten_text
from utils.llm_handler import grade_with_ollama
from utils.similarity_handler import calculate_similarity, extract_reference_content
from config import ACCURACY_THRESHOLD_MIN, ACCURACY_THRESHOLD_MAX

# Page configuration
st.set_page_config(
    page_title="Smart Student Grader",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">📚 Smart Student Grader</div>', unsafe_allow_html=True)
st.write("Intelligent system to grade student answers against reference materials using AI")

# Sidebar - Instructions
with st.sidebar:
    st.header("📖 Instructions")
    with st.expander("How to use?", expanded=False):
        st.write("""
        1. **Upload Reference Material (Ebook)**
           - Upload the subject textbook/ebook (PDF)
           - System will extract content for comparison
        
        2. **Upload Question Paper**
           - Upload question paper with questions and marks
        
        3. **Upload Student Answer Sheet**
           - Upload handwritten/typed student answers (PDF)
        
        4. **Set Accuracy Threshold**
           - Define minimum accuracy % for answers (50-100%)
           - Lower threshold = more lenient grading
        
        5. **Compare & Grade**
           - Click "Grade Answer" button
           - AI analyzes and allocates marks
        """)
    
    st.divider()
    
    st.header("⚙️ Configuration")
    accuracy_threshold = st.slider(
        "Accuracy Threshold (%)",
        min_value=ACCURACY_THRESHOLD_MIN,
        max_value=ACCURACY_THRESHOLD_MAX,
        value=60,
        step=5,
        help="Minimum relevance score for answer to be considered valid"
    )

# Main content area
col1, col2, col3 = st.columns(3)

# Column 1: Upload Reference Material
with col1:
    st.subheader("1️⃣ Reference Material")
    ebook_file = st.file_uploader(
        "Upload Subject Ebook (PDF)",
        type="pdf",
        key="ebook",
        help="Upload the reference textbook/ebook"
    )
    
    if ebook_file:
        st.success("✅ Ebook uploaded successfully!")
        ebook_pages = st.number_input(
            "Number of pages to analyze",
            min_value=1,
            max_value=100,
            value=10,
            help="Analyze first N pages for faster processing"
        )

# Column 2: Upload Question Paper
with col2:
    st.subheader("2️⃣ Question Paper")
    question_file = st.file_uploader(
        "Upload Question Paper (PDF)",
        type="pdf",
        key="question",
        help="Upload question paper with questions and marks"
    )
    
    if question_file:
        st.success("✅ Question paper uploaded!")
        # Extract questions
        try:
            questions_text = extract_text_from_pdf(question_file)
            num_questions = st.number_input(
                "Number of questions",
                min_value=1,
                max_value=50,
                value=10
            )
        except Exception as e:
            st.error(f"Error reading question paper: {e}")

# Column 3: Upload Student Answer Sheet
with col3:
    st.subheader("3️⃣ Student Answer Sheet")
    student_file = st.file_uploader(
        "Upload Student Answers (PDF)",
        type="pdf",
        key="student",
        help="Upload student's handwritten or typed answers"
    )
    
    if student_file:
        st.success("✅ Student answer sheet uploaded!")

# Divider
st.divider()

# Question Selection and Grading
if ebook_file and question_file and student_file:
    st.subheader("🎯 Select Question to Grade")
    
    col_q1, col_q2 = st.columns([2, 1])
    
    with col_q1:
        question_number = st.selectbox(
            "Select Question Number",
            options=list(range(1, num_questions + 1)),
            format_func=lambda x: f"Question {x}"
        )
    
    with col_q2:
        marks_for_question = st.number_input(
            "Marks for this question",
            min_value=1,
            max_value=100,
            value=10
        )
    
    st.divider()
    
    # Manual question input (in case auto-extraction fails)
    with st.expander("📝 Enter Question Manually (Optional)"):
        manual_question = st.text_area(
            "Paste the question here",
            height=100,
            help="You can manually enter the question if auto-extraction fails"
        )
    
    # Grade button
    col_grade1, col_grade2, col_grade3 = st.columns([1, 1, 2])
    
    with col_grade1:
        grade_button = st.button(
            "🎯 Grade Answer",
            type="primary",
            use_container_width=True
        )
    
    with col_grade2:
        clear_button = st.button(
            "🔄 Clear Results",
            use_container_width=True
        )
    
    # Processing
    if grade_button:
        with st.spinner("⏳ Processing... This may take a moment"):
            try:
                # Step 1: Extract texts
                st.info("📖 Extracting reference material...")
                ebook_text = extract_text_from_pdf(ebook_file, pages=ebook_pages)
                
                st.info("📄 Extracting student answer...")
                student_answer = extract_handwritten_text(student_file)
                
                st.info("🔍 Analyzing similarity...")
                similarity_score = calculate_similarity(student_answer, ebook_text)
                
                # Step 2: Check accuracy threshold
                if similarity_score < accuracy_threshold:
                    st.markdown(f"""
                    <div class="error-box">
                    <h4>❌ Answer Below Threshold</h4>
                    <p><strong>Relevance Score:</strong> {similarity_score:.1f}%</p>
                    <p><strong>Required Threshold:</strong> {accuracy_threshold}%</p>
                    <p>Answer is not sufficiently relevant to the reference material.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    score = 0
                    grading_feedback = f"Answer relevance ({similarity_score:.1f}%) is below the threshold ({accuracy_threshold}%). Score: 0/{marks_for_question}"
                
                else:
                    st.info("🤖 Grading with AI...")
                    
                    # Step 3: Grade with LLM
                    question_text = manual_question if manual_question else f"Question {question_number}"
                    
                    grading_result = grade_with_ollama(
                        student_answer=student_answer,
                        reference_text=ebook_text,
                        question=question_text,
                        accuracy_threshold=accuracy_threshold,
                        max_marks=marks_for_question
                    )
                    
                    score = grading_result['score']
                    grading_feedback = grading_result['feedback']
                    missing_points = grading_result['missing_points']
                    strengths = grading_result['strengths']
                
                # Display results
                st.divider()
                st.subheader("📊 Grading Results")
                
                # Results in columns
                res_col1, res_col2, res_col3 = st.columns(3)
                
                with res_col1:
                    st.metric(
                        "Score",
                        f"{score}/{marks_for_question}",
                        f"{(score/marks_for_question)*100:.1f}%"
                    )
                
                with res_col2:
                    st.metric(
                        "Relevance Score",
                        f"{similarity_score:.1f}%",
                        "vs requirement"
                    )
                
                with res_col3:
                    st.metric(
                        "Threshold",
                        f"{accuracy_threshold}%",
                        "minimum required"
                    )
                
                st.divider()
                
                # Detailed feedback
                st.markdown(f"""
                <div class="success-box">
                <h4>📋 Feedback</h4>
                <p>{grading_feedback}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Strengths and Missing points (if available)
                if similarity_score >= accuracy_threshold:
                    feedback_col1, feedback_col2 = st.columns(2)
                    
                    with feedback_col1:
                        if 'strengths' in grading_result and grading_result['strengths']:
                            st.success(f"✅ **Strengths:** {grading_result['strengths']}")
                    
                    with feedback_col2:
                        if 'missing_points' in grading_result and grading_result['missing_points']:
                            st.warning(f"⚠️ **Missing Points:** {grading_result['missing_points']}")
                
                # Student answer preview
                with st.expander("👀 View Student's Answer"):
                    st.text_area(
                        "Student Answer (OCR Extracted):",
                        value=student_answer,
                        height=200,
                        disabled=True
                    )
                
                # Save results option
                st.divider()
                if st.button("💾 Save Results", use_container_width=True):
                    st.success("✅ Results saved successfully!")
            
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                <h4>❌ Error Occurred</h4>
                <p><strong>Error Details:</strong> {str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
                st.error(f"Debug Info: {type(e).__name__}")

else:
    st.info("👆 Please upload all three files (Ebook, Question Paper, Student Answer) to begin grading")