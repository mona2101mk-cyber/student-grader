import streamlit as st
import tempfile
import os
from google import genai
import time
import random
st.title("📝 AI Paper Grader")

# 1. API Initialization
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
client = None

if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("Please enter your API Key in the sidebar to begin.")

# 2. Holybook Upload Logic
uploaded_holybook = st.file_uploader("Upload 'Holybook' (Textbook PDF)", type="pdf")

if uploaded_holybook and client: # Added 'and client' check here
    if 'holybook_ref' not in st.session_state:
        with st.spinner("Uploading Textbook to Gemini..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_holybook.getbuffer())
                tmp_path = tmp.name
            
            try:
                # Now 'client' is guaranteed to exist
                file_ref = client.files.upload(file=tmp_path)
                st.session_state.holybook_ref = file_ref
                st.success("Textbook processed!")
            except Exception as e:
                st.error(f"Upload failed: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)


# 3. Question Paper Input
st.header("2. Question Paper")
q_paper_text = st.text_area("Paste the Questions here (e.g., Q1. What is DBMS? [10 marks])", height=150)

# 4. Student Answer Sheet
st.header("3. Student Submission")
uploaded_student_pdf = st.file_uploader("Upload Student Answer Sheet (Handwritten PDF)", type="pdf")

if uploaded_student_pdf and client:
    if 'student_ref' not in st.session_state:
        with st.spinner("Processing Student Paper..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_student_pdf.getbuffer())
                tmp_path = tmp.name
            try:
                # Uploading the student paper just like the holybook
                student_file_ref = client.files.upload(file=tmp_path)
                st.session_state.student_ref = student_file_ref
                st.success("Student paper uploaded!")
            except Exception as e:
                st.error(f"Student upload failed: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

# 5. Threshold & Compare
st.header("4. Evaluation")
accuracy_threshold = st.slider("Accuracy Threshold (%)", 0, 100, 50)



# Use the latest stable model
MODEL_NAME = 'gemini-2.5-flash-lite' 

if st.button("🚀 Compare and Grade"):
    if 'holybook_ref' in st.session_state and 'student_ref' in st.session_state and q_paper_text:
        success = False
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                with st.spinner(f"AI is grading (Attempt {attempt+1}/{max_retries})..."):
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=[
                            st.session_state.holybook_ref, 
                            st.session_state.student_ref, 
                            prompt
                        ]
                    )
                    st.markdown("### 📊 Grading Report")
                    st.write(response.text)
                    success = True
                    break # Exit loop on success
                    
            except Exception as e:
                if "429" in str(e):
                    wait_time = (2 ** attempt) + random.random() * 5
                    st.warning(f"Quota hit. Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    st.error(f"Error: {e}")
                    break
        
        if not success:
            st.error("Failed after multiple retries. Try a smaller textbook PDF or enable billing for higher Tier 1 limits.")

# if st.button("🚀 Compare and Grade"):
#     if 'holybook_ref' in st.session_state and 'student_ref' in st.session_state and q_paper_text:
#         with st.spinner("AI is grading... please wait."):
#             # PROMPT ENGINEERING
#             prompt = f"""
#             You are a strict but fair College Professor. 
#             Inputs:
#             1. Textbook (attached file 1)
#             2. Student Handwritten Answer Sheet (attached file 2)
#             3. Questions: {q_paper_text}
            
#             Task:
#             - Use OCR to read the student's handwriting from the PDF.
#             - Compare each answer to the relevant section in the Textbook.
#             - The user has set an accuracy threshold of {accuracy_threshold}%. 
#             - If the student's answer is at least {accuracy_threshold}% accurate/relevant to the textbook, award marks accordingly.
#             - Total marks per question as per the question paper.
            
#             Output Format:
#             Q1: [Score]/[Total] - [Brief Reasoning]
#             Q2: ...
#             TOTAL SCORE: [X]/[Total]
#             """
            
#             try:
#                 # Sending BOTH files in the contents list
#                 response = client.models.generate_content(
#                     model='gemini-2.0-flash-lite', # Using the newest fast model
#                     contents=[
#                         st.session_state.holybook_ref, 
#                         st.session_state.student_ref, 
#                         prompt
#                     ]
#                 )
#                 st.markdown("### 📊 Grading Report")
#                 st.write(response.text)
#             except Exception as e:
#                 st.error(f"Grading failed: {e}")
#                 # if "429" in str(e):
#                 #     st.error("Wait 10 seconds. The PDFs use a lot of 'tokens'—Lite is processing them now!")
#                 # else:
#                 #     st.error(f"Grading failed: {e}")
    else:
        st.warning("Ensure all files are uploaded and questions are filled.")



