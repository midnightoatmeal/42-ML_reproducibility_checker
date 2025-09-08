import streamlit as st
import fitz  # PyMuPDF for PDF processing
import ast
import re

st.set_page_config(page_title="42: AI-Powered Reproducibility Checker", layout="wide")

# Helper Functions
def analyze_python_code(file):
    """Extract function names, imports, and reproducibility markers from a Python file."""
    try:
        code_content = file.read().decode("utf-8")
        tree = ast.parse(code_content)
        
        # Extract function names
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Extract all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(name.name for name in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        
        # Check for random seed settings (key for reproducibility)
        seed_patterns = [r'np\.random\.seed', r'torch\.manual_seed', r'random\.seed']
        seeds_used = any(re.search(pattern, code_content) for pattern in seed_patterns)
        
        return functions, imports, seeds_used
    except Exception as e:
        st.error(f"Error analyzing {file.name}: {str(e)}")
        return [], [], False

def extract_pdf_text(file, pages=2):
    """Extract text from the first few pages of a PDF."""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            text = "\n".join([page.get_text("text") for page in doc][:pages])
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return "Unable to extract text."

# Main App
st.title("🔍 42: AI-Powered Reproducibility Checker")
st.write("Upload a research paper (PDF) and its code (Python files) to analyze reproducibility.")

# File Upload Section
uploaded_paper = st.file_uploader("📄 Upload Research Paper (PDF)", type=["pdf"])
uploaded_code = st.file_uploader("📜 Upload Python Code (.py)", type=["py"], accept_multiple_files=True)

# Display Upload Status
if uploaded_paper:
    st.success(f"✅ Paper uploaded: {uploaded_paper.name}")
    with st.spinner("Extracting PDF preview..."):
        pdf_text = extract_pdf_text(uploaded_paper)
        st.subheader("📄 Paper Preview:")
        st.text_area("Extracted Text", pdf_text, height=200)

if uploaded_code:
    st.success(f"✅ {len(uploaded_code)} Python files uploaded.")

st.write("🚀 Click 'Analyze' to check reproducibility.")

# Analysis Section
if st.button("Analyze"):
    if not uploaded_paper or not uploaded_code:
        st.warning("⚠️ Please upload both a research paper and Python code.")
    else:
        st.subheader("🔬 Analysis Results")
        
        with st.spinner("Analyzing code..."):
            all_functions, all_imports, seeds_used = [], [], False
            for code_file in uploaded_code:
                functions, imports, seed = analyze_python_code(code_file)
                all_functions.extend(functions)
                all_imports.extend(imports)
                if seed:
                    seeds_used = True

        # Display Code Analysis Results
        col1, col2 = st.columns(2)
        with col1:
            st.write("📌 **Detected Functions in Code:**")
            st.write(", ".join(all_functions) if all_functions else "None found")
        with col2:
            st.write("📦 **Detected Imports:**")
            st.write(", ".join(set(all_imports)) if all_imports else "None found")

        # Reproducibility Checklist
        st.subheader("🧪 Reproducibility Checklist")
        if seeds_used:
            st.write("✅ Random seed settings detected (e.g., `np.random.seed`, `torch.manual_seed`).")
        else:
            st.write("❌ No random seed settings found. Consider adding them for reproducibility.")
        
        st.success("✅ Analysis Complete! More features coming soon.")

# Instructions and Tips
with st.expander("ℹ️ How to Use"):
    st.write("""
    1. Upload the research paper in PDF format.
    2. Upload the accompanying Python code files.
    3. Click 'Analyze' to check for reproducibility markers.
    4. Review the results and checklist for insights.
    """)

st.write("💡 **Tip:** Including random seed settings in your code improves reproducibility.")
