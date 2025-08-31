## 42: Your AI-Powered Reproducibility Auditor

42 is an AI-assisted reproducibility audit tool designed to quickly assess how well a research paper's claims align with its accompanying Python code.

### The Problem
Machine learning research moves at an incredible pace, but reproducibility often lags. It can be difficult and time-consuming to verify if the code for a given paper truly reflects the methods, parameters, and environment described in the text. This friction slows down scientific progress and makes it harder to build upon previous work.

42 aims to be the first line of defense, providing a quick, automated analysis to highlight key alignment signals and potential discrepancies between a paper and its code.

Upload a paper (PDF) and one or more .py files, and 42 will parse both, highlight reproducibility signals, and generate a downloadable plaintext audit report.



## Features
- **PDF + Code Analysis**
Upload a research paper (.pdf) and associated Python code files (.py).
- **Keyword Extraction**
Automatically identify core ML terms from the paper (e.g., attention, transformer, embedding, optimizer, token).
-Code Parsing (AST + Regex)
-Detect Python functions and imports.
-Identify random seed usage and determinism flags.
-Extract hyperparameters (learning rate, batch size, epochs, dropout).
-Cross-Validation
Compare extracted paper keywords with codebase content to spot alignment gaps.
-Hyperparameter Comparison
Highlight mismatches between values reported in the paper and those implemented in the code.
-Reproducibility Report
Generate and download a plaintext audit that summarizes keyword alignment, hyperparameters, and reproducibility practices.


## Installation

Clone the repo and install dependencies:

```
git clone https://github.com/midnightoatmeal/42-ML_reproducibility_checker
cd 42-ML_reproducibility_checker
```

# Create a virtual environment
```
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

# Install dependencies
`pip install -r requirements.txt`

# Run the Streamlit app
`streamlit run app.py`

Your requirements.txt should contain:
```
streamlit
PyMuPDF
pandas
```

## Live Demo

Try it live: https://whatis42.streamlit.app

## Contributing

Contributions are welcome! If you have ideas for new features or improvements, please open an issue to discuss it. If you'd like to contribute code, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
