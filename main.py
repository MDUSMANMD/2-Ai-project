import streamlit as st
import io, requests
import PyPDF2
from docx import Document
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER

# ---------- API ----------
API_KEY = st.secrets["NVIDIA_API_KEY"]

st.set_page_config(page_title="NovaMind AI", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
.stApp {background:#1e1e1e; color:white;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🚀 NovaMind AI")

mode = st.sidebar.radio(
    "Choose AI Feature",
    ["🎓 Education", "💼 Career", "💰 Finance", "📄 Analyzer", "📊 Dashboard", "💬 Chat Analytics"]
)

# ---------- SESSION ----------
if "memory" not in st.session_state:
    st.session_state.memory = {
        "Education": [], "Career": [], "Finance": [], "Analyzer": []
    }

if "usage" not in st.session_state:
    st.session_state.usage = []

# ---------- AI ----------
def call_ai(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta/llama3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400
    }

    try:
        with st.spinner("🤖 AI is thinking..."):
            res = requests.post(url, headers=headers, json=data, timeout=25)

        if res.status_code != 200:
            return f"API ERROR {res.status_code}: {res.text}"

        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"ERROR: {str(e)}"

# ---------- FILE ----------
def read_file(file):
    if not file:
        return ""

    if "pdf" in file.type:
        reader = PyPDF2.PdfReader(file)
        return "".join([p.extract_text() or "" for p in reader.pages])

    elif "word" in file.type:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif "image" in file.type:
        return "User uploaded an image. Describe and analyze it."

    else:
        return file.read().decode(errors="ignore")

# ---------- PDF ----------
def pdf_download(text):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        name="Heading",
        parent=styles["Heading2"],
        spaceAfter=10
    )

    body_style = styles["Normal"]

    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    elements = []

    elements.append(Paragraph("AI Analysis Report", title_style))
    elements.append(Spacer(1, 12))

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            elements.append(Spacer(1, 8))
            continue

        if line.lower().startswith(("summary", "key points", "insights", "strengths", "weaknesses", "suggestions", "rating")):
            elements.append(Paragraph(line, heading_style))
        else:
            elements.append(Paragraph(line, body_style))

        elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- SMART AI ----------
def memory_chat(module, user_input):

    history = "\n".join(st.session_state.memory[module][-4:])

    if module == "Career":
        instruction = """
Analyze this resume/career document.

Give:
- Rating (out of 5)
- Strengths
- Weaknesses
- Improvements
- Final Suggestions
"""
    elif module == "Education":
        instruction = """
Analyze study material.

Give:
- Summary
- Key Points
- Important Questions
"""
    elif module == "Finance":
        instruction = """
Analyze financial content.

Give:
- Insights
- Risks
- Suggestions
"""
    else:
        instruction = """
Analyze document.

Give:
- Summary
- Key Points
- Improvements
"""

    prompt = f"""
{instruction}

Previous Context:
{history}

User Input:
{user_input}
"""

    response = call_ai(prompt)

    st.session_state.memory[module].append(f"User: {user_input}")
    st.session_state.memory[module].append(f"AI: {response}")

    return response

# ---------- CHAT ----------
def chatbot(module):
    st.markdown("### 💬 Chat with AI")
    q = st.text_input("Ask anything")

    if st.button("Ask AI"):
        if q:
            res = memory_chat(module, q)
            st.write(res)

# ============================================================
# 🎓 EDUCATION
# ============================================================
if mode == "🎓 Education":

    st.header("🎓 Education AI")

    file = st.file_uploader("Upload Notes", type=["pdf","docx","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Answer"):
        result = memory_chat("Education", read_file(file) + "\n" + q)

        st.markdown("### 📘 Answer")
        st.write(result)

        st.download_button("⬇️ Download PDF", pdf_download(result), "Education_Report.pdf")

        st.session_state.usage.append("Education")

    chatbot("Education")

# ============================================================
# 💼 CAREER
# ============================================================
elif mode == "💼 Career":

    st.header("💼 Career AI")

    file = st.file_uploader("Upload Resume", type=["pdf","docx","txt","png","jpg"])
    role = st.text_input("Target Role")

    if st.button("Analyze"):
        result = memory_chat("Career", role + "\n" + read_file(file))

        st.markdown("### 💼 Career Analysis")
        st.write(result)

        st.download_button("⬇️ Download PDF", pdf_download(result), "Career_Report.pdf")

        st.session_state.usage.append("Career")

    chatbot("Career")

# ============================================================
# 💰 FINANCE
# ============================================================
elif mode == "💰 Finance":

    st.header("💰 Finance AI")

    file = st.file_uploader("Upload Data", type=["pdf","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Advice"):
        result = memory_chat("Finance", read_file(file) + "\n" + q)

        st.markdown("### 💰 Advice")
        st.write(result)

        st.download_button("⬇️ Download PDF", pdf_download(result), "Finance_Report.pdf")

        st.session_state.usage.append("Finance")

    chatbot("Finance")

# ============================================================
# 📄 ANALYZER
# ============================================================
elif mode == "📄 Analyzer":

    st.header("📄 Analyzer AI")

    file = st.file_uploader("Upload File", type=["pdf","docx","txt","png","jpg"])

    if st.button("Analyze"):
        result = memory_chat("Analyzer", read_file(file))

        st.markdown("### 📊 Analysis Result")
        st.write(result)

        st.download_button("⬇️ Download PDF", pdf_download(result), "Analysis_Report.pdf")

        st.session_state.usage.append("Analyzer")

    chatbot("Analyzer")

# ============================================================
# 📊 DASHBOARD
# ============================================================
elif mode == "📊 Dashboard":

    st.header("📊 Advanced Analytics Dashboard")

    if st.session_state.usage:
        df = pd.DataFrame(st.session_state.usage, columns=["Feature"])
        counts = df["Feature"].value_counts()

        st.bar_chart(counts)
        st.write(counts)
        st.metric("Total Usage", len(st.session_state.usage))

    else:
        st.info("No usage yet")

# ============================================================
# 💬 CHAT ANALYTICS
# ============================================================
elif mode == "💬 Chat Analytics":

    st.header("💬 Chat Analytics")

    total = sum(len(v) for v in st.session_state.memory.values())
    st.metric("Total Messages", total)

    if st.session_state.usage:
        df = pd.DataFrame(st.session_state.usage, columns=["Module"])
        st.bar_chart(df["Module"].value_counts())

    for module, chats in st.session_state.memory.items():
        if chats:
            st.write(f"### {module}")
            for msg in chats[-4:]:
                st.write(msg)

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b> 🚀</center>", unsafe_allow_html=True)