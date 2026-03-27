import streamlit as st
import os
import PyPDF2
import io
from dotenv import load_dotenv

# --- MODERN LANGCHAIN IMPORTS ---
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Load the secret API key from the .env file (for local use)
load_dotenv()

# --- 1. DEFINE THE AI TOOL (The Math Engine) ---
@tool
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

# --- 2. SETUP THE AI AGENT (Modern Way) ---
def create_tax_agent():
    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    tools = [tax_calculator]
    
    # Modern LangChain requires a specific prompt format
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Money Mentor. Use your tax_calculator tool to calculate taxes for the user. Present the results clearly."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the modern tool-calling agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

# --- 3. HELPER FUNCTION: READ PDF ---
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page].extract_text()
    return text

# --- 4. BUILD THE UI (Streamlit) ---
st.set_page_config(page_title="ET AI Money Mentor", page_icon="💸", layout="wide")

st.title("💸 AI Money Mentor: Tax Wizard")
st.markdown("Chat with me to optimize your taxes, or upload your Form 16 to get started instantly!")

# Sidebar for File Upload
st.sidebar.header("Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload Form 16/Salary Slip (PDF)", type=["pdf"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Process PDF if uploaded
if uploaded_file is not None:
    if st.sidebar.button("Analyze My Document"):
        with st.spinner("Extracting numbers and calculating taxes..."):
            document_text = extract_text_from_pdf(uploaded_file)
            hidden_prompt = f"The user uploaded a tax document. Here is the text: '{document_text}'. Find their gross salary and deductions, then use your tax_calculator tool to tell them which tax regime is better."
            
            agent_executor = create_tax_agent()
            # Modern LangChain execution
            result = agent_executor.invoke({"input": hidden_prompt})
            response = result["output"]
            
            st.session_state.messages.append({"role": "assistant", "content": f"**Document Analyzed!**\n\n{response}"})

# Display past chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Text Input for Chat
user_input = st.chat_input("E.g., My salary is 15 Lakhs and I have 2 Lakhs in 80C deductions.")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show AI response
    with st.chat_message("assistant"):
        with st.spinner("Crunching the numbers..."):
            agent_executor = create_tax_agent()
            # Modern LangChain execution
            result = agent_executor.invoke({"input": user_input})
            response = result["output"]
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})