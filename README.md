# 42: ML Reproducibility Checker
**42** is an AI-assisted reproducibility audit tool designed to assess the alignment between a research paper and its corresponding Python code. Upload your PDF and code files, and get a quick reproducibility check with a downloadable audit report.

- **PDF + Code Analysis**: Upload a research paper and one or more `.py` files.
- **Keyword Extraction**: Extract key ML terms from the paper (e.g., attention, optimizer, token).
- **Code Parsing**: Detect Python functions, imports, and random seed usage using AST and regex.
- **Cross-Validation**: Compare extracted paper keywords with function names to find missing alignment.
- **Reproducibility Report**: Generate and download a plaintext audit of code-paper consistency.

git clone https://github.com/midnightoatmeal/42-ML_reproducibility_checker
pip install -r requirements.txt
streamlit run app1.py

# Sample Use Case

You're reviewing a NeurIPS or ICLR submission. With `42`, you can:

1. Upload the PDF paper and its codebase.
2. Instantly check if:
   - Random seeds are set (for reproducibility).
   - Key terms in the paper appear in the code.
   - All functions and imports are clearly defined.
3. Download an audit report summarizing the alignment.

## Live Demo
Try it live: https://whatis42.streamlit.app

## License
MIT
