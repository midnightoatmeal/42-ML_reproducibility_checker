# 42: ML Reproducibility Checker
**42** is an AI-assisted reproducibility audit tool designed to assess the alignment between a research paper and its corresponding Python code. Upload your PDF and code files, and get a quick reproducibility check with a downloadable audit report.

- **PDF + Code Analysis**: Upload a research paper and one or more `.py` files.
- **Keyword Extraction**: Extract key ML terms from the paper (e.g., attention, optimizer, token).
- **Code Parsing**: Detect Python functions, imports, and random seed usage using AST and regex.
- **Cross-Validation**: Compare extracted paper keywords with function names to find missing alignment.
- **Reproducibility Report**: Generate and download a plaintext audit of code-paper consistency.

## Installation
1. Clone the repo: `git clone https://github.com/midnightoatmeal/42-ML_reproducibility.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `streamlit run app1.py`

## Usage
Upload a PDF and `.py` files, then click "Analyze"!

## Live Demo
Try it live: https://whatis42.streamlit.app

## License
MIT
