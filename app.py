import streamlit as st
import os
import PyPDF2
import io
import google.generativeai as genai
from dotenv import load_dotenv

# Load local .env file
load_dotenv()

# --- 1. CONFIGURE GOOGLE AI ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Missing GOOGLE_API_KEY. Please add it to your Streamlit secrets!")
    st.stop()

genai.configure(api_key=api_key)

# --- 2. SETUP THE AI AGENT ---
system_prompt = """You are an expert AI Money Mentor for the ET Hackathon. 
Your job is to act as a 'Tax Wizard'. 
When a user provides their salary and deductions (or a Form 16 text), you must:
1. Identify their gross salary and deductions.
2. Calculate taxes under the Old Regime.
3. Calculate taxes under the New Regime.
4. Recommend which regime is better and show the exact savings.
5. Suggest 2-3 tax-saving investments based on their profile.
Be friendly, highly structured, and use emojis!"""

# Updated to the correct, active model version
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt
)

# CRITICAL FIX: We store the raw history data, NOT the live connection object!
if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []

# Start a fresh, clean connection on every run using the saved history
chat_session = model.start_chat(history=st.session_state.gemini_history)

# --- 3. HELPER: READ PDF ---
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in range(len(pdf_reader.pages)):
        extracted = pdf_reader.pages[page].extract_text()
        if extracted:
            text += extracted
    return text

# --- 4. BUILD THE UI ---
st.set_page_config(page_title="ET AI Money Mentor", page_icon="💸", layout="wide")
st.title("💸 AI Money Mentor: Tax Wizard")
st.markdown("Upload your Form 16, or just type your salary below!")

# Sidebar for PDF Upload
st.sidebar.header("Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload Form 16 (PDF)", type=["pdf"])

if uploaded_file and st.sidebar.button("Analyze My Document"):
    with st.spinner("Extracting numbers and calculating taxes..."):
        document_text = extract_text_from_pdf(uploaded_file)
        
        if not document_text.strip():
            st.error("Could not read text from this PDF. Ensure it is not a scanned image.")
        else:
            prompt = f"Here is my tax document: \n\n{document_text}\n\nFind my gross salary and deductions, calculate my taxes, and recommend the best regime."
            
            try:
                # Send to AI
                response = chat_session.send_message(prompt)
                
                # Update our saved histories securely
                st.session_state.gemini_history = chat_session.history
                st.session_state.ui_messages.append({"role": "user", "content": f"*(Uploaded Document: {uploaded_file.name})*"})
                st.session_state.ui_messages.append({"role": "assistant", "content": f"**Document Analyzed!**\n\n{response.text}"})
            except Exception as e:
                st.error(f"⚠️ Google API Error: {e}")

# Display Chat History
for msg in st.session_state.ui_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
user_input = st.chat_input("E.g., My salary is 15 Lakhs and I have 2 Lakhs in 80C deductions.")

if user_input:
    st.session_state.ui_messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Crunching the numbers..."):
            try:
                # Send to AI
                response = chat_session.send_message(user_input)
                st.markdown(response.text)
                
                # Update our saved histories securely
                st.session_state.gemini_history = chat_session.history
                st.session_state.ui_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ Google API Error: {e}")