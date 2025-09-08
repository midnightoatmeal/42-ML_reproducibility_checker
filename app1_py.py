import streamlit as st
import fitz  # PyMuPDF for PDF processing
import ast
import re
import datetime
import pandas as pd

st.set_page_config(page_title="42: Reproducibility Checker", layout="wide")

# --- Constants & Regex Helpers ---

# Float pattern: matches 0.1, .001, 1e-4, 5E-05, etc.
NUM_FP = r'([0-9]*\.?[0-9]+(?:[eE][\+\-]?\d+)?)'

HYPERPARAMETER_PATTERNS = {
    'learning_rate': [rf'learning[_\s]?rate\s*=\s*{NUM_FP}', rf'lr\s*=\s*{NUM_FP}'],
    'batch_size':    [r'batch[_\s]?size\s*=\s*(\d+)'],
    'epochs':        [r'(?:num_)?epochs\s*=\s*(\d+)'],
    'dropout':       [rf'dropout\s*=\s*{NUM_FP}'],
}

PAPER_HYPERPARAMETER_PATTERNS = {
    'learning_rate': [rf'learning\s*rate\s*(?:of|is|=)\s*{NUM_FP}'],
    'batch_size':    [r'batch[-\s]?size\s*(?:of|is|=)\s*(\d+)'],
    'epochs':        [r'(?:for|over)\s*(\d+)\s*epochs', r'epochs\s*(?:of|=)\s*(\d+)'],
    'dropout':       [rf'dropout\s*(?:of|is|=)\s*{NUM_FP}'],
}

# Broader reproducibility signals (case-insensitive)
SEED_PATTERNS = [
    r'np\.random\.seed',
    r'torch\.manual_seed',
    r'torch\.cuda\.manual_seed_all',
    r'random\.seed',
    r'tf\.random\.set_seed',
    r'jax\.random\.PRNGKey',
    r'os\.environ\[\s*[\'"]PYTHONHASHSEED[\'"]\s*\]',
    r'torch\.use_deterministic_algorithms\(\s*True\s*\)',
    r'torch\.backends\.cudnn\.deterministic\s*=\s*True',
    r'torch\.backends\.cudnn\.benchmark\s*=\s*False',
]

# --- Helper Functions ---

def _normalize_spaces(text: str) -> str:
    """Clean odd spaces from OCR'd PDFs."""
    return re.sub(r'[\u00A0\u2000-\u200B\u202F\u205F\u3000]', ' ', text)

def extract_pdf_data(file):
    """Extracts full text and hyperparameters from a PDF."""
    try:
        full_text = ""
        hyperparameters = {}
        pdf_bytes = file.read()
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            full_text = "\n".join([page.get_text("text") for page in doc])

        # Normalize weird spaces (helps regex)
        full_text = _normalize_spaces(full_text)

        # Extract keywords (expand as needed)
        keywords = set(re.findall(
            r'\b(attention|transformer|embedding|optimizer|layer|model|token|prediction|loss)\b',
            full_text, re.IGNORECASE
        ))
        # Ensure stable ordering in UI later
        keywords = {k.lower() for k in keywords}

        # Extract hyperparameters from text (case-insensitive)
        for param, patterns in PAPER_HYPERPARAMETER_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    hyperparameters[param] = match.group(1)
                    break  # Take the first match for this param

        # Isolate first few lines for preview
        preview_text = "\n".join(full_text.split('\n')[:50])  # Preview ~50 lines

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
            elif isinstance(node, ast.ImportFrom) and node.module:
                # Guard against None for relative imports like: from . import x
                imports.append(node.module)

        # Seed / determinism detection (case-insensitive)
        seeds_used = any(re.search(pattern, file_content, re.IGNORECASE) for pattern in SEED_PATTERNS)

        # Keyword overlap (case-insensitive)
        matched_keywords = {
            kw for kw in paper_keywords
            if re.search(rf'\b{re.escape(kw)}\b', file_content, re.IGNORECASE)
        }

        # Hyperparameter regex search (case-insensitive)
        hyperparameters = {}
        for param, patterns in HYPERPARAMETER_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, file_content, re.IGNORECASE)
                if match:
                    hyperparameters[param] = match.group(1)
                    break  # Take first match

        return functions, imports, seeds_used, matched_keywords, hyperparameters
    except Exception as e:
        st.error(f"Error analyzing a Python file: {str(e)}")
        return [], [], False, set(), {}

def _to_num(x):
    """Normalize numeric strings (including scientific notation) to floats when possible."""
    try:
        if isinstance(x, str) and re.fullmatch(NUM_FP, x.strip(), re.IGNORECASE):
            return float(x)
        return x
    except Exception:
        return x

def generate_report(paper_name, code_files, functions, imports, seeds_used, pdf_keywords, matched_keywords, hyperparameter_df):
    """Generates a downloadable text report of the audit."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    missing_keywords = sorted((pdf_keywords - matched_keywords))
    imports_unique = sorted(set(imports))
    functions_sorted = sorted(functions)

    if hyperparameter_df is None or hyperparameter_df.empty:
        hparam_section = "No hyperparameters detected in paper or code."
    else:
        hparam_section = hyperparameter_df.to_string(index=False)

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
{hparam_section}

Detected Components:
--------------------
- Functions: {', '.join(functions_sorted) if functions_sorted else 'None'}
- Imports: {', '.join(imports_unique) if imports_unique else 'None'}

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
        file_contents = {file.name: file.read().decode("utf-8", errors="replace") for file in uploaded_code}
        for name, content in file_contents.items():
            functions, imports, seed, matched, hypers = analyze_python_code(content, pdf_keywords)
            all_functions.extend(functions)
            all_imports.extend(imports)
            all_matched_keywords.update(matched)
            if seed:
                seeds_used = True
            for key, val in hypers.items():
                if key not in code_hyperparams:  # Only take the first one found across all files
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
        missing_keywords = sorted((pdf_keywords - all_matched_keywords))
        if not missing_keywords:
            st.success("✅ All key terms from the paper were found in the code.")
        else:
            st.warning(f"⚠️ Missing Keywords: `{', '.join(missing_keywords)}`")

    st.subheader("🔬 Hyperparameter Comparison")

    # Create a DataFrame for comparison (with numeric normalization to avoid false mismatches)
    param_keys = sorted(list(set(paper_hyperparams.keys()) | set(code_hyperparams.keys())))
    if not param_keys:
        st.info("No common hyperparameters found to compare.")
        hyperparameter_df = pd.DataFrame()
    else:
        data = []
        for key in param_keys:
            paper_val_raw = paper_hyperparams.get(key, "Not Found")
            code_val_raw = code_hyperparams.get(key, "Not Found")

            paper_val = _to_num(paper_val_raw)
            code_val = _to_num(code_val_raw)

            match = "✅" if paper_val == code_val and paper_val != "Not Found" else "❌"
            data.append({
                "Parameter": key,
                "Value in Paper": paper_val_raw,
                "Value in Code": code_val_raw,
                "Match": match
            })

        hyperparameter_df = pd.DataFrame(data)
        st.dataframe(hyperparameter_df, use_container_width=True)

    # --- 4. Detailed Breakdown & Report ---
    with st.expander("📄 Detailed File-by-File Analysis"):
        for name, content in file_contents.items():
            st.markdown(f"**{name}**")
            functions, imports, _, matched, hypers = analyze_python_code(content, pdf_keywords)
            st.write(" - **Functions:**", ", ".join(sorted(functions)) if functions else "None")
            st.write(" - **Imports:**", ", ".join(sorted(set(imports))) if imports else "None")
            st.write(" - **Matched Keywords:**", ", ".join(sorted(matched)) if matched else "None")
            st.write(" - **Found Hyperparameters:**", str(hypers) if hypers else "None")

    with st.expander("📝 PDF Preview"):
        st.text_area("Text Extract", pdf_preview, height=250)
        st.write("🔑 **Keywords Found:**", ", ".join(sorted(pdf_keywords)) if pdf_keywords else "None")

    # Generate and offer the report for download
    report = generate_report(
        uploaded_paper.name,
        uploaded_code,
        all_functions,
        all_imports,
        seeds_used,
        pdf_keywords,
        all_matched_keywords,
        hyperparameter_df if not hyperparameter_df.empty else pd.DataFrame()
    )
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
