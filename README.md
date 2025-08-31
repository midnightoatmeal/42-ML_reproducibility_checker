## 42: ML Reproducibilty Checker

42 is an AI-assisted reproducibility audit tool designed to quickly assess how well a research paper’s claims align with its accompanying Python code.

Upload a paper (PDF) and one or more .py files, and 42 will parse both, highlight reproducibility signals, and generate a downloadable plaintext audit report.



## Features
	•	PDF + Code Analysis
Upload a research paper (.pdf) and associated Python code files (.py).
	•	Keyword Extraction
Automatically identify core ML terms from the paper (e.g., attention, transformer, embedding, optimizer, token).
	•	Code Parsing (AST + Regex)
	•	Detect Python functions and imports.
	•	Identify random seed usage and determinism flags.
	•	Extract hyperparameters (learning rate, batch size, epochs, dropout).
	•	Cross-Validation
Compare extracted paper keywords with codebase content to spot alignment gaps.
	•	Hyperparameter Comparison
Highlight mismatches between values reported in the paper and those implemented in the code.
	•	Reproducibility Report
Generate and download a plaintext audit that summarizes keyword alignment, hyperparameters, and reproducibility practices.

⸻

## Installation

Clone the repo and install dependencies:

```
git clone https://github.com/midnightoatmeal/42-ML_reproducibility_checker
pip install -r requirements.txt
streamlit run app.py
```

## Sample Use Case

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
MIT License. See LICENSE for details.
