import streamlit as st
import fitz  # PyMuPDF for PDF processing
import ast
import re
import datetime
import pandas as pd

st.set_page_config(page_title="42: Reproducibility Checker", layout="wide")

# --- Constants for Analysis ---
HYPERPARAMETER_PATTERNS = {
    'learning_rate': [r'learning_rate\s*=\s*([0-9\.]+)', r'lr\s*=\s*([0-9\.]+)'],
    'batch_size': [r'batch_size\s*=\s*(\d+)'],
    'epochs': [r'epochs\s*=\s*(\d+)', r'num_epochs\s*=\s*(\d+)'],
    'dropout': [r'dropout\s*=\s*([0-9\.]+)'],
}

PAPER_HYPERPARAMETER_PATTERNS = {
    'learning_rate': [r'learning rate of\s*([0-9\.]+)'],
    'batch_size': [r'batch size of\s*(\d+)'],
    'epochs': [r'for\s*(\d+)\s*epochs'],
    'dropout': [r'dropout of\s*([0-9\.]+)'],
}

# --- Helper Functions ---

def extract_pdf_data(file):
    """Extracts full text and hyperparameters from a PDF."""
    try:
        full_text = ""
        hyperparameters = {}
        pdf_bytes = file.read()
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            full_text = "\n".join([page.get_text("text") for page in doc])

        # Extract keywords
        keywords = set(re.findall(r'\b(attention|transformer|embedding|optimizer|layer|model|token|prediction|loss)\b', full_text, re.I))

        # Extract hyperparameters from text
        for param, patterns in PAPER_HYPERPARAMETER_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    hyperparameters[param] = match.group(1)
                    break # Take the first match for this param
        
        # Isolate first few pages for preview
        preview_text = "\n".join(full_text.split('\n')[:50]) # Preview ~50 lines

        return preview_text, full_text, keywords, hyperparameters
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return "Unable to extract text.", "", set(), {}

def analyze_python_code(file_content, paper_keywords):
    """Analyzes Python code for functions, imports, seeds, keywords, and hyperparameters."""
    try:
        tree = ast.parse(file_content)

        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(name.name for name in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)

        seed_patterns = [
            r'np\.random\.seed', r'torch\.manual_seed', r'random\.seed',
            r'torch\.cuda\.manual_seed_all', r'os\.environ\[\s*[\'"]PYTHONHASHSEED[\'"]\s*\]',
            r'torch\.backends\.cudnn\.deterministic',
        ]
        seeds_used = any(re.search(pattern, file_content) for pattern in seed_patterns)

        matched_keywords = {kw for kw in paper_keywords if re.search(rf'\b{re.escape(kw)}\b', file_content, re.IGNORECASE)}

        hyperparameters = {}
        for param, patterns in HYPERPARAMETER_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, file_content)
                if match:
                    hyperparameters[param] = match.group(1)
                    break # Take first match

        return functions, imports, seeds_used, matched_keywords, hyperparameters
    except Exception as e:
        st.error(f"Error analyzing a Python file: {str(e)}")
        return [], [], False, set(), {}

def generate_report(paper_name, code_files, functions, imports, seeds_used, pdf_keywords, matched_keywords, hyperparameter_df):
    """Generates a downloadable text report of the audit."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    missing_keywords = pdf_keywords - matched_keywords
    report = f"""
42: Reproducibility Audit Report
=================================
Generated: {now}

Analyzed Files:
- Paper: {paper_name}
- Code: {', '.join([f.name for f in code_files])}

Overall Summary:
----------------
- Random Seed Used: {'Yes' if seeds_used else 'No'}
- Keyword Alignment: {len(matched_keywords)} / {len(pdf_keywords)} keywords matched.
- Missing Keywords: {', '.join(missing_keywords) if missing_keywords else 'None'}

Hyperparameter Comparison:
--------------------------
{hyperparameter_df.to_string()}

Detected Components:
--------------------
- Functions: {', '.join(functions) if functions else 'None'}
- Imports: {', '.join(set(imports)) if imports else 'None'}

-- Audited using 42 --
"""
    return report

# --- UI ---
st.title("🔍 42: ML Reproducibility Checker")
st.markdown("Upload your research paper (`.pdf`) and associated code files (`.py`) to analyze for reproducibility signals.")

# Use session state to persist data
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

with st.sidebar:
    st.header("Uploads")
    uploaded_paper = st.file_uploader("📄 Upload Paper (PDF)", type=["pdf"])
    uploaded_code = st.file_uploader("📜 Upload Python Code", type=["py"], accept_multiple_files=True)
    analyze_button = st.button("Analyze Reproducibility", type="primary")

if analyze_button and (not uploaded_paper or not uploaded_code):
    st.warning("Please upload both a paper and at least one code file.")
elif analyze_button:
    st.session_state.analysis_done = True


if st.session_state.analysis_done and uploaded_paper and uploaded_code:
    st.success(f"Uploaded Paper: **{uploaded_paper.name}** | Uploaded Code: **{[f.name for f in uploaded_code]}**")
    
    # --- 1. Paper Analysis ---
    with st.spinner("Analyzing PDF..."):
        pdf_preview, pdf_full_text, pdf_keywords, paper_hyperparams = extract_pdf_data(uploaded_paper)

    # --- 2. Code Analysis ---
    all_functions, all_imports, all_matched_keywords, code_hyperparams = [], [], set(), {}
    seeds_used = False

    with st.spinner("Analyzing code files..."):
        file_contents = {file.name: file.read().decode("utf-8") for file in uploaded_code}
        for name, content in file_contents.items():
            functions, imports, seed, matched, hypers = analyze_python_code(content, pdf_keywords)
            all_functions.extend(functions)
            all_imports.extend(imports)
            all_matched_keywords.update(matched)
            if seed:
                seeds_used = True
            for key, val in hypers.items():
                if key not in code_hyperparams: # Only take the first one found across all files
                    code_hyperparams[key] = val
    
    # --- 3. Display Results ---
    st.header("📊 Reproducibility Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Randomness Control")
        if seeds_used:
            st.success("✅ Random seed setting was detected in the code.")
        else:
            st.warning("⚠️ No random seed found. This is crucial for consistent results.")
    
    with col2:
        st.subheader("Keyword Alignment")
        missing_keywords = pdf_keywords - all_matched_keywords
        if not missing_keywords:
            st.success("✅ All key terms from the paper were found in the code.")
        else:
            st.warning(f"⚠️ Missing Keywords: `{', '.join(missing_keywords)}`")

    st.subheader("🔬 Hyperparameter Comparison")
    
    # Create a DataFrame for comparison
    param_keys = sorted(list(set(paper_hyperparams.keys()) | set(code_hyperparams.keys())))
    if not param_keys:
        st.info("No common hyperparameters found to compare.")
    else:
        data = []
        for key in param_keys:
            paper_val = paper_hyperparams.get(key, "Not Found")
            code_val = code_hyperparams.get(key, "Not Found")
            match = "✅" if paper_val == code_val else "❌"
            data.append({"Parameter": key, "Value in Paper": paper_val, "Value in Code": code_val, "Match": match})
        
        hyperparameter_df = pd.DataFrame(data)
        st.dataframe(hyperparameter_df, use_container_width=True)

    # --- 4. Detailed Breakdown & Report ---
    with st.expander("📄 Detailed File-by-File Analysis"):
        for name, content in file_contents.items():
            st.markdown(f"**{name}**")
            functions, imports, _, matched, hypers = analyze_python_code(content, pdf_keywords)
            st.write(" - **Functions:**", ", ".join(functions) if functions else "None")
            st.write(" - **Imports:**", ", ".join(set(imports)) if imports else "None")
            st.write(" - **Matched Keywords:**", ", ".join(matched) if matched else "None")
            st.write(" - **Found Hyperparameters:**", str(hypers) if hypers else "None")
    
    with st.expander("📝 PDF Preview"):
        st.text_area("Text Extract", pdf_preview, height=250)
        st.write("🔑 **Keywords Found:**", ", ".join(pdf_keywords) if pdf_keywords else "None")

    # Generate and offer the report for download
    report = generate_report(uploaded_paper.name, uploaded_code, all_functions, all_imports, seeds_used, pdf_keywords, all_matched_keywords, hyperparameter_df if 'hyperparameter_df' in locals() else pd.DataFrame())
    st.download_button(
        label="📥 Download Full Audit Report",
        data=report,
        file_name=f"42_audit_report_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

else:
    st.info("Upload a paper and code files, then click 'Analyze' to begin.")
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1.  **Upload** your research paper (PDF) and the corresponding Python (`.py`) files.
        2.  **Analyze**: The tool extracts keywords and hyperparameters from the paper's text. It then parses your code to find functions, imported libraries, and implemented hyperparameters.
        3.  **Review**: The dashboard provides an at-a-glance summary comparing the findings from the paper and the code.
        4.  **Download**: Get a text file report of the complete audit for your records.
        """)
