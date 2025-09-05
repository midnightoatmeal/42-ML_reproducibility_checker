

import streamlit as st
import fitz  # PyMuPDF for PDF processing
import ast
import re
import datetime

st.set_page_config(page_title="42: Reproducibility Checker", layout="wide")

# --- Helper Functions ---
def analyze_python_code(file, paper_keywords):
    try:
        code_str = file.read().decode("utf-8")
        tree = ast.parse(code_str)

        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(name.name for name in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)

        seed_patterns = [
            r'np\.random\.seed',
            r'torch\.manual_seed',
            r'random\.seed',
            r'torch\.cuda\.manual_seed_all',
            r'os\.environ\[\s*[\'"]PYTHONHASHSEED[\'"]\s*\]',
            r'torch\.backends\.cudnn\.deterministic',
        ]
        seeds_used = any(re.search(pattern, code_str) for pattern in seed_patterns)

        # Enhanced keyword match across full code
        matched_keywords = set()
        for kw in paper_keywords:
            if re.search(rf'\b{re.escape(kw)}\b', code_str, re.IGNORECASE):
                matched_keywords.add(kw)

        return functions, imports, seeds_used, matched_keywords
    except Exception as e:
        st.error(f"Error analyzing {file.name}: {str(e)}")
        return [], [], False, set()

def extract_pdf_text(file, pages=2):
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            text = "\n".join([page.get_text("text") for page in doc][:pages])
            keywords = set(re.findall(r'\b(attention|transformer|embedding|optimizer|layer|model|token|prediction|loss)\b', text, re.I))
        return text, keywords
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return "Unable to extract text.", set()

def generate_report(functions, imports, seeds_used, pdf_keywords, matched_keywords):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    missing_keywords = pdf_keywords - matched_keywords
    report = f"""
42: Reproducibility Audit Report
Generated: {now}

Functions Detected:
{', '.join(functions) if functions else 'None'}

Imports Detected:
{', '.join(set(imports)) if imports else 'None'}

Random Seed Used: {'Yes' if seeds_used else 'No'}

Paper Keywords:
{', '.join(pdf_keywords) if pdf_keywords else 'None'}

Matched Keywords in Code:
{', '.join(matched_keywords) if matched_keywords else 'None'}

Missing Keywords from Paper:
{', '.join(missing_keywords) if missing_keywords else 'None'}

-- Audited using 42
"""
    return report

# --- UI ---
st.title("🔍 42: ML Reproducibility Checker")
st.write("Upload your research paper (PDF) and code files to analyze reproducibility.")

uploaded_paper = st.file_uploader("📄 Upload Paper (PDF)", type=["pdf"])
uploaded_code = st.file_uploader("📜 Upload Python Code", type=["py"], accept_multiple_files=True)

if uploaded_paper:
    st.success(f"Uploaded: {uploaded_paper.name}")
    with st.spinner("Extracting PDF..."):
        pdf_text, pdf_keywords = extract_pdf_text(uploaded_paper)
        st.subheader("📄 PDF Preview")
        st.text_area("Text Extract", pdf_text, height=200)
        st.write("🔑 Keywords:", ", ".join(pdf_keywords) if pdf_keywords else "None")

if uploaded_code:
    st.success(f"{len(uploaded_code)} Python file(s) uploaded.")

if st.button("Analyze"):
    if not uploaded_paper or not uploaded_code:
        st.warning("Please upload both paper and code.")
    else:
        all_functions, all_imports, all_matched_keywords = [], [], set()
        seeds_used = False

        st.subheader("🔬 Per-File Analysis")
        for code_file in uploaded_code:
            with st.expander(f"📄 {code_file.name}"):
                functions, imports, seed, matched_keywords = analyze_python_code(code_file, pdf_keywords)
                all_functions.extend(functions)
                all_imports.extend(imports)
                all_matched_keywords.update(matched_keywords)
                if seed:
                    seeds_used = True

                st.write("📌 Functions:", ", ".join(functions) if functions else "None")
                st.write("📦 Imports:", ", ".join(set(imports)) if imports else "None")
                st.write("🧠 Matched Keywords:", ", ".join(matched_keywords) if matched_keywords else "None")

        missing_keywords = pdf_keywords - all_matched_keywords

        st.subheader("🧪 Reproducibility Summary")
        if seeds_used:
            st.success("✅ Random seed setting detected.")
        else:
            st.warning("⚠ No random seed found. Add for consistent results.")

        if missing_keywords:
            st.warning(f"⚠ Missing Keywords from Paper: {', '.join(missing_keywords)}")
        else:
            st.success("✅ All key terms from paper found in code.")

        report = generate_report(all_functions, all_imports, seeds_used, pdf_keywords, all_matched_keywords)
        st.download_button("📄 Download Audit Report", report, file_name="42_audit_report.txt")

with st.expander("ℹ️ Instructions"):
    st.markdown("""
    1. Upload your paper (PDF) and code (.py).
    2. Click "Analyze" to run reproducibility checks.
    3. View results per file and download your audit report.
    4. For a full expert audit, [submit your repo here](#).
    """)
