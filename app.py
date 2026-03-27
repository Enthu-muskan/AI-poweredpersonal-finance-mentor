import streamlit as st
import os
import PyPDF2
import io
import google.generativeai as genai
from dotenv import load_dotenv

# Load local .env file (for when you run it on your own computer)
load_dotenv()

# --- 1. CONFIGURE GOOGLE AI ---
# First try to get the key from Streamlit Secrets (Cloud), then fallback to local .env
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Missing GOOGLE_API_KEY. Please add it to your Streamlit secrets!")
    st.stop()

genai.configure(api_key=api_key)

# --- 2. DEFINE THE AI TOOL ---
def tax_calculator(salary: float, deductions: float = 0.0) -> str:
    """
    Calculates and compares taxes under the Old and New Indian Tax Regimes.
    Input the gross salary and any deductions (like 80C, HRA).
    """
    new_tax = salary * 0.10 
    taxable_old = max(0, salary - deductions)
    old_tax = taxable_old * 0.15
    recommendation = "New Regime" if new_tax <= old_tax else "Old Regime"
    savings = abs(new_tax - old_tax)
    return f"Old Regime Tax: ₹{old_tax:,.2f} | New Regime Tax: ₹{new_tax:,.2f}. Recommendation: Opt for the {recommendation} to save ₹{savings:,.2f}."

# --- 3. SETUP THE AI AGENT ---
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=[tax_calculator],
    system_instruction="You are an AI Money Mentor for the ET Hackathon. Use the tax_calculator tool to calculate taxes based on user input. Be friendly and helpful."
)

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=True)
    st.session_state.messages = []

# --- 4. HELPER: READ PDF ---
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page].extract_text()
    return text

# --- 5. BUILD THE UI ---
st.set_page_config(page_title="ET AI Money Mentor", page_icon="💸", layout="wide")
st.title("💸 AI Money Mentor: Tax Wizard")
st.markdown("Upload your Form 16, or just type your salary below!")

# Sidebar for PDF Upload
st.sidebar.header("Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload Form 16 (PDF)", type=["pdf"])

if uploaded_file and st.sidebar.button("Analyze My Document"):
    with st.spinner("Extracting numbers and calculating taxes..."):
        document_text = extract_text_from_pdf(uploaded_file)
        prompt = f"Here is my tax document: '{document_text}'. Find my gross salary and deductions, then calculate my taxes."
        
        response = st.session_state.chat_session.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": f"**Document Analyzed!**\n\n{response.text}"})

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
user_input = st.chat_input("E.g., My salary is 15 Lakhs and I have 2 Lakhs in 80C deductions.")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Crunching the numbers..."):
            response = st.session_state.chat_session.send_message(user_input)
            st.markdown(response.text)
            
    st.session_state.messages.append({"role": "assistant", "content": response.text})