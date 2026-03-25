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

if "results" not in st.session_state:
    st.session_state.results = {}

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
        return "User uploaded an image. Describe it."

    else:
        return file.read().decode(errors="ignore")

# ---------- PDF ----------
def pdf_download(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("AI Analysis Report", styles["Heading1"]))
    elements.append(Spacer(1, 10))

    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- SMART AI ----------
def smart_prompt(module, content):

    if module == "Career":
        return f"""
Analyze this resume.

Give:
- Rating /5
- Strengths
- Weaknesses
- Improvements
- Suggestions

{content}
"""

    elif module == "Education":
        return f"""
Analyze study material.

Give:
- Summary
- Key points
- Important questions

{content}
"""

    elif module == "Finance":
        return f"""
Analyze financial content.

Give:
- Insights
- Risks
- Suggestions

{content}
"""

    else:
        return f"""
Analyze document.

Give:
- Summary
- Key points
- Improvements

{content}
"""

# ---------- CHAT ----------
def chatbot(module):
    st.markdown("### 💬 Chat with AI")
    q = st.text_input("Ask anything")

    if st.button("Ask AI"):
        if q:
            res = call_ai(q)
            st.write(res)

# ============================================================
# 🎓 EDUCATION
# ============================================================
if mode == "🎓 Education":

    st.header("🎓 Education AI")

    file = st.file_uploader("Upload Notes", type=["pdf","docx","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Answer"):
        result = call_ai(smart_prompt("Education", read_file(file) + "\n" + q))
        st.session_state.results["Education"] = result
        st.session_state.usage.append("Education")

    if "Education" in st.session_state.results:
        st.write(st.session_state.results["Education"])
        st.download_button("Download PDF", pdf_download(st.session_state.results["Education"]))

    chatbot("Education")

# ============================================================
# 💼 CAREER
# ============================================================
elif mode == "💼 Career":

    st.header("💼 Career AI")

    file = st.file_uploader("Upload Resume", type=["pdf","docx","txt","png","jpg"])
    role = st.text_input("Target Role")

    if st.button("Analyze"):
        result = call_ai(smart_prompt("Career", role + "\n" + read_file(file)))
        st.session_state.results["Career"] = result
        st.session_state.usage.append("Career")

    if "Career" in st.session_state.results:
        st.write(st.session_state.results["Career"])
        st.download_button("Download PDF", pdf_download(st.session_state.results["Career"]))

    chatbot("Career")

# ============================================================
# 💰 FINANCE
# ============================================================
elif mode == "💰 Finance":

    st.header("💰 Finance AI")

    file = st.file_uploader("Upload Data", type=["pdf","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Advice"):
        result = call_ai(smart_prompt("Finance", read_file(file) + "\n" + q))
        st.session_state.results["Finance"] = result
        st.session_state.usage.append("Finance")

    if "Finance" in st.session_state.results:
        st.write(st.session_state.results["Finance"])
        st.download_button("Download PDF", pdf_download(st.session_state.results["Finance"]))

    chatbot("Finance")

# ============================================================
# 📄 ANALYZER
# ============================================================
elif mode == "📄 Analyzer":

    st.header("📄 Analyzer AI")

    file = st.file_uploader("Upload File", type=["pdf","docx","txt","png","jpg"])

    if st.button("Analyze"):
        result = call_ai(smart_prompt("Analyzer", read_file(file)))
        st.session_state.results["Analyzer"] = result
        st.session_state.usage.append("Analyzer")

    if "Analyzer" in st.session_state.results:
        st.write(st.session_state.results["Analyzer"])
        st.download_button("Download PDF", pdf_download(st.session_state.results["Analyzer"]))

    chatbot("Analyzer")

# ============================================================
# 📊 DASHBOARD
# ============================================================
elif mode == "📊 Dashboard":

    st.header("📊 Dashboard")

    if st.session_state.usage:
        df = pd.DataFrame(st.session_state.usage, columns=["Feature"])
        st.bar_chart(df["Feature"].value_counts())

# ============================================================
# 💬 CHAT ANALYTICS
# ============================================================
elif mode == "💬 Chat Analytics":

    st.header("💬 Chat Analytics")

    total = sum(len(v) for v in st.session_state.memory.values())
    st.metric("Total Messages", total)

    if st.session_state.usage:
        df = pd.DataFrame(st.session_state.usage, columns=["Module"])
        counts = df["Module"].value_counts()

        st.subheader("Usage Chart")
        st.bar_chart(counts)

        st.subheader("AI Insights")

        insight = call_ai(f"Give insights for this usage data: {counts.to_dict()}")
        st.write(insight)

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b> 🚀</center>", unsafe_allow_html=True)