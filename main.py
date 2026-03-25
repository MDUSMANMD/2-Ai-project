import streamlit as st
import io, requests
import PyPDF2
from docx import Document
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- CONFIG ----------
st.set_page_config(page_title="NovaMind AI", layout="wide")

API_KEY = st.secrets["NVIDIA_API_KEY"]

# ---------- UI ----------
st.markdown("""
<style>
.stApp {background:#1e1e1e; color:white;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🚀 NovaMind AI")

mode = st.sidebar.radio(
    "Select Module",
    [
        "🎓 Education",
        "💼 Career",
        "💰 Finance",
        "📄 Analyzer",
        "📊 Dashboard",
        "📈 Chart Analyzer"
    ]
)

# ---------- SESSION ----------
if "results" not in st.session_state:
    st.session_state.results = {}

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
        with st.spinner("🤖 AI Thinking..."):
            res = requests.post(url, headers=headers, json=data, timeout=25)

        if res.status_code != 200:
            return f"❌ API ERROR: {res.text}"

        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ ERROR: {str(e)}"

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
        return "User uploaded an image. Analyze and describe it."

    else:
        return file.read().decode(errors="ignore")

# ---------- PDF ----------
def generate_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("AI Report", styles["Heading1"]))
    elements.append(Spacer(1, 10))

    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 5))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- PROMPTS ----------
def get_prompt(module, content):

    if module == "Career":
        return f"""
Analyze resume.

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
Analyze financial data.

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
def chatbot():
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

    file = st.file_uploader("Upload File", type=["pdf","docx","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Answer"):
        result = call_ai(get_prompt("Education", read_file(file) + "\n" + q))
        st.session_state.results["Education"] = result
        st.session_state.usage.append("Education")

    if "Education" in st.session_state.results:
        st.write(st.session_state.results["Education"])
        st.download_button("Download PDF", generate_pdf(st.session_state.results["Education"]))

    chatbot()

# ============================================================
# 💼 CAREER
# ============================================================
elif mode == "💼 Career":

    st.header("💼 Career AI")

    file = st.file_uploader("Upload Resume", type=["pdf","docx","txt","png","jpg"])
    role = st.text_input("Target Role")

    if st.button("Analyze"):
        result = call_ai(get_prompt("Career", role + "\n" + read_file(file)))
        st.session_state.results["Career"] = result
        st.session_state.usage.append("Career")

    if "Career" in st.session_state.results:
        st.write(st.session_state.results["Career"])
        st.download_button("Download PDF", generate_pdf(st.session_state.results["Career"]))

    chatbot()

# ============================================================
# 💰 FINANCE
# ============================================================
elif mode == "💰 Finance":

    st.header("💰 Finance AI")

    file = st.file_uploader("Upload File", type=["pdf","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Advice"):
        result = call_ai(get_prompt("Finance", read_file(file) + "\n" + q))
        st.session_state.results["Finance"] = result
        st.session_state.usage.append("Finance")

    if "Finance" in st.session_state.results:
        st.write(st.session_state.results["Finance"])
        st.download_button("Download PDF", generate_pdf(st.session_state.results["Finance"]))

    chatbot()

# ============================================================
# 📄 ANALYZER
# ============================================================
elif mode == "📄 Analyzer":

    st.header("📄 Analyzer AI")

    file = st.file_uploader("Upload File", type=["pdf","docx","txt","png","jpg"])

    if st.button("Analyze"):
        result = call_ai(get_prompt("Analyzer", read_file(file)))
        st.session_state.results["Analyzer"] = result
        st.session_state.usage.append("Analyzer")

    if "Analyzer" in st.session_state.results:
        st.write(st.session_state.results["Analyzer"])
        st.download_button("Download PDF", generate_pdf(st.session_state.results["Analyzer"]))

    chatbot()

# ============================================================
# 📊 DASHBOARD
# ============================================================
elif mode == "📊 Dashboard":

    st.header("📊 Dashboard")

    if st.session_state.usage:
        df = pd.DataFrame(st.session_state.usage, columns=["Feature"])
        st.bar_chart(df["Feature"].value_counts())

# ============================================================
# 📈 CHART ANALYZER
# ============================================================
elif mode == "📈 Chart Analyzer":

    st.header("📈 Chart Analyzer & AI Insights")

    if st.session_state.usage:

        df = pd.DataFrame(st.session_state.usage, columns=["Feature"])
        counts = df["Feature"].value_counts()

        st.subheader("📊 Usage Chart")
        st.bar_chart(counts)

        st.subheader("📋 Data")
        st.dataframe(counts)

        st.subheader("🤖 AI Insights")

        insight = call_ai(f"Analyze this usage data and give insights: {counts.to_dict()}")
        st.write(insight)

    else:
        st.warning("No data yet. Use app first.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b> 🚀</center>", unsafe_allow_html=True)