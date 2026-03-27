# 💸 AI Money Mentor: Tax Wizard

**An AI-powered personal finance assistant built for the ET Hackathon.**

## 🚀 Overview
The **AI Money Mentor** is a smart, conversational web application designed to demystify taxes for salaried professionals. Powered by Google's Gemini AI and built with Streamlit, this app allows users to either manually enter their salary details or directly upload their Form 16 PDF. The AI acts as a "Tax Wizard" to instantly analyze their financials and provide actionable advice.

## ✨ Key Features
* **📄 Document Analysis:** Seamlessly extracts text and financial data from uploaded Form 16 PDFs.
* **🧮 Smart Tax Calculation:** Automatically calculates tax liabilities under both the Old and New Indian Tax Regimes.
* **💡 Personalized Recommendations:** Compares the two regimes and explicitly recommends which one saves the user the most money.
* **📈 Investment Advice:** Suggests tailored 80C, 80D, and other tax-saving investment strategies based on the user's specific profile.
* **💬 Conversational Memory:** Remembers context throughout the chat session for a natural, flowing conversation.

## 🛠️ Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI/LLM:** [Google Gemini](https://ai.google.dev/) (via `google-generativeai`)
* **Document Processing:** `PyPDF2`
* **Language:** Python 3

## 💻 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/ai-poweredpersonal-finance-mentor.git](https://github.com/YOUR_USERNAME/ai-poweredpersonal-finance-mentor.git)
   cd ai-poweredpersonal-finance-mentor