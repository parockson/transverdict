# TransVerdict: Automated Batch Analysis

TransVerdict is a powerful, automated batch analysis tool built with Streamlit. It is designed to ingest raw transaction data, apply business-specific cleaning and segmentation logic, and generate comprehensive, interactive statistical reports and visualizations. 

## Features

- **Automated Data Ingestion**: Easily upload CSV or Excel transaction files.
- **Data Cleaning & Segmentation**: Automatically applies robust business logic to map client names to business segments, categorize technical failure messages into human-readable formats, and assign error responsibilities.
- **Statistical Reporting**: Generates dynamic pivot tables breaking down metrics by Response Codes, Business Segments, Client Names, and Transaction Types.
- **Interactive Visualizations**: View your data through beautifully rendered Plotly charts right in the dashboard.
- **Export Capabilities**: Download the fully transformed data as a CSV or access a heavily formatted, multi-sheet Excel report containing all your analyses.

## Project Structure

```
transverdict/
├── app.py                  # Main Streamlit application entry point
├── core/                   # Core business logic modules
│   ├── analyzer.py         # Logic for pivot tables, Excel export, and Plotly visuals
│   ├── cleaner.py          # Data pre-processing and cleaning functions
│   └── segmenter.py        # Business segmentation and failure wildcard mapping
├── data/                   # Directory for storing raw and processed data (ignored in git)
├── utils/                  # Helper utilities
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd transverdict
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

2. **Interact with the Dashboard:**
   - Open the provided local URL in your web browser.
   - Upload your transaction dataset (`.csv` or `.xlsx`).
   - Click **"🚀 Process Data & Generate Reports"**.
   - Navigate through the "Transformed Data", "Analysis Tables", and "Visual Dashboard" tabs to review the insights.
   - Download the formatted Excel report or the cleaned CSV using the provided buttons.

## Technologies Used

- **[Streamlit](https://streamlit.io/)**: For building the interactive web application UI.
- **[Pandas](https://pandas.pydata.org/)**: For powerful data manipulation, cleaning, and pivot table generation.
- **[Plotly](https://plotly.com/python/)**: For rendering interactive graphs and visual dashboards.
- **[Openpyxl](https://openpyxl.readthedocs.io/en/stable/)**: For formatting and exporting complex Excel workbooks.
