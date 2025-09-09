## 42: ML Reproducibility Checker

https://whatis42.streamlit.app


**42** is a Streamlit application designed to automate the critical but often tedious process of verifying the reproducibility of machine learning research papers. By analyzing a paper's text and its corresponding code repository, the tool flags inconsistencies and missing information, providing a rapid first-pass check for researchers, reviewers, and engineers.

## The Problem

Reproducibility is the cornerstone of scientific progress, yet many published ML papers are difficult to reproduce due to missing dataset links, ambiguous methodology descriptions, or discrepancies between the paper's claims and the provided code. The "42" checker was built to address this challenge by automating the verification of key claims, methods, and datasets.

## Key Features

* **Automated Claim Extraction:** Scans research papers from top conferences (NeurIPS, ICLR, ICML) to identify and extract key claims, methodologies, and referenced datasets.
* **Code & Paper Validation:** Performs an NLP-driven comparison between the paper's text and the code repository to flag inconsistencies in methodology and dataset usage.
* **Inconsistency Reporting:** Generates a clear report highlighting potential issues, such as missing dataset links or mismatches between the described implementation and the actual code. In testing, this system has successfully flagged over 50 missing dataset links and 25+ implementation-method mismatches.

## How It Works

The application's backend is a Python pipeline that:
1.  Accepts a link to a research paper (PDF) and its code repository.
2.  Uses libraries like `pdfplumber` to parse the paper's text.
3.  Applies an NLP pipeline to extract entities related to datasets, libraries, and specific ML methods.
4.  Scans the code repository to verify the presence of dataset links and to check for alignment with the paper's described methodology.
5.  Presents the findings in a clean, user-friendly interface powered by **Streamlit**.

## Installation & Usage

To run the application locally, follow these steps:

# Clone the repository:
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
`streamlit run app_py.py`

Your requirements.txt should contain:
```
streamlit
PyMuPDF
pandas
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
