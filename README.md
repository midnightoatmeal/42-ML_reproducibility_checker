## 42: Your AI-Powered Reproducibility Auditor
42 is a web tool designed to automate the initial audit of ML reproducibility signals.

The Problem
Machine learning research moves at an incredible pace, but reproducibility often lags. It can be difficult and time-consuming to verify if the code for a given paper truly reflects the methods, parameters, and environment described in the text. This friction slows down scientific progress and makes it harder to build upon previous work.

42 aims to be the first line of defense, providing a quick, automated analysis to highlight key alignment signals and potential discrepancies between a paper and its code.

## Key Features
-PDF Text Extraction: Ingests research papers in PDF format and intelligently extracts key text and concepts.

-Keyword Alignment: Automatically identifies key ML terms (e.g., transformer, attention, optimizer) in the paper and verifies their presence in the Python source code.

-Hyperparameter Comparison: Scans both the paper and the code for critical hyperparameters (like learning rate, batch size, epochs) and presents them in a side-by-side comparison table to instantly spot mismatches.

-Random Seed Detection: Checks for the use of random seeds (torch.manual_seed, np.random.seed, etc.), a crucial practice for ensuring deterministic results.

-Reproducibility Dashboard: Presents all findings in a clean, easy-to-read UI, with clear success and warning indicators.

-Downloadable Reports: Generates a full text-based audit report of the analysis that you can save for your records.

## How It Works
-Upload: Provide your research paper as a .pdf file.

-Add Code: Upload one or more Python .py source files associated with the paper.

-Analyze: Click the "Analyze" button to run the audit.

-Review: Explore the dashboard to see the keyword alignment, hyperparameter comparison, and other reproducibility signals.

## Running Locally
Clone the repository:

git clone https://github.com/midnightoatmeal/42-ML_reproducibility_checker

Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install dependencies:
(Make sure you have a requirements.txt file with the necessary libraries)

```pip install -r requirements.txt```

Your requirements.txt should contain:
```
streamlit
PyMuPDF
pandas
```

Run the Streamlit app:

```streamlit run app.py```

## Contributing

Contributions are welcome! If you have ideas for new features or improvements, please open an issue to discuss it. If you'd like to contribute code, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

