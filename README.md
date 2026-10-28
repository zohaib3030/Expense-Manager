# Smart Expense Manager

A Python-based expense tracking web application built with Streamlit. It helps users record daily expenses, monitor category-wise spending, track monthly budgets, and receive AI-generated saving strategies.

## Features

- Add expenses manually by category.
- Track Food, Fare, Stationary, Health, Entertainment, and Others.
- Store expense records in a CSV file without using SQL.
- View monthly spending summaries and interactive Plotly charts.
- Set a monthly budget and monitor remaining funds.
- Generate personalized expense-management suggestions using Google's GenAI API.
- Export expense records to CSV.

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly Express
- Google GenAI API
- CSV file storage

## Installation

1. Clone the repository:

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd smart-expense-manager
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   On Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` and configure your Google API key:

   ```toml
   GEMINI_API_KEY = "your_google_api_key"
   ```

5. Start the application:

   ```bash
   streamlit run app.py
   ```

## Data Storage

Expense records are stored locally in `expenses.csv`. The application does not require an SQL database. Back up your CSV file regularly.

## Security

Keep API keys and personal expense records private. Never commit secrets or personal financial data to a public repository.

## Disclaimer

AI-generated suggestions are informational and should be reviewed before making financial decisions.

## Future Improvements

- Edit and delete expenses.
- Persist monthly budget settings.
- Add spending trend analysis.
- Improve dashboard customization and deployment support.
