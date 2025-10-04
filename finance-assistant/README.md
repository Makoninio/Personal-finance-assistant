# 💰 Personal Finance AI Assistant

A hackathon-ready MVP for personal finance management with AI-powered categorization, insights, and multilingual support.

## 🚀 Features

- **📄 Data Ingestion**: Parse bank statement PDFs and CSV files
- **🤖 AI Categorization**: Rule-based + OpenAI fallback for transaction categorization
- **📊 Financial Insights**: Net worth tracking, spending analysis, and health scores
- **🔍 Transaction Explanations**: AI-powered explanations using OpenAI and Perplexity
- **🌍 Multilingual Reports**: DeepL integration for Spanish, French, German, and more
- **📈 Interactive Dashboard**: Streamlit-based UI with charts and visualizations
- **☁️ Senso Integration**: Store raw PDF text and structured transactions in Senso cloud

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Pandas, SQLite
- **Frontend**: Streamlit
- **AI Services**: OpenAI, Perplexity, DeepL
- **Cloud Storage**: Senso API for raw text and structured data
- **Database**: SQLite (local storage)
- **Charts**: Plotly

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (optional but recommended)
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

## 🚀 Quick Start

1. **Run the application**
   ```bash
   streamlit run frontend/app.py
   ```

2. **Load sample data**
   - Click "🔄 Load Sample Data" in the sidebar
   - Or upload your own PDF/CSV file

3. **Explore features**
   - View the dashboard with financial overview
   - Explain transactions with AI
   - Generate multilingual reports
   - Analyze spending patterns

## 📁 Project Structure

```
finance-assistant/
├── backend/
│   ├── ingestion.py         # PDF/CSV parser
│   ├── categorize.py        # Rule-based + OpenAI categorizer
│   ├── insights.py          # Aggregation + metrics
│   ├── explain.py           # AI explanations
│   ├── translate.py         # DeepL integration
│   └── db.py                # SQLite operations
├── frontend/
│   ├── app.py               # Main Streamlit app
│   └── charts.py            # Chart utilities
├── data/
│   └── sample_transactions.csv
├── tests/
│   └── test_categorize.py   # Unit tests
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### API Keys (Optional)

- **Senso**: Required for storing raw PDF text and structured transactions in cloud
- **OpenAI**: Required for AI categorization and explanations
- **Perplexity**: Optional, for enhanced transaction explanations
- **DeepL**: Optional, for multilingual translations

### Database

The app uses SQLite for local storage. Database file is created automatically at `data/transactions.db`.

### Senso Integration

The app can optionally store both raw PDF text and structured transaction data in Senso cloud storage:

1. **Raw Text Storage**: Full PDF text is uploaded to `/content/raw` endpoint
2. **Structured Data**: Parsed transactions are uploaded to `/content/json` endpoint
3. **Content IDs**: Both uploads return content IDs for future reference

To enable Senso integration:
1. Get your Senso API key from [Senso Dashboard](https://senso.ai)
2. Add it to your `.env` file or enter it in the Settings page
3. Upload PDFs will automatically be stored in Senso

## 📊 Usage Examples

### 1. Upload Bank Statement
```python
# PDF upload
ingestion = StatementIngestion()
df = ingestion.parse_pdf("bank_statement.pdf")

# CSV upload
df = ingestion.parse_csv("transactions.csv")
```

### 2. Categorize Transactions
```python
categorizer = TransactionCategorizer()
categorized_df = categorizer.categorize_batch(df)
```

### 3. Generate Insights
```python
insights = FinancialInsights(categorized_df)
net_worth = insights.get_net_worth_snapshot()
category_breakdown = insights.get_category_breakdown()
```

### 4. Explain Transactions
```python
explainer = TransactionExplainer()
explanations = explainer.explain_transaction(
    "SPOTIFY PREMIUM", -12.99, "Entertainment"
)
```

### 5. Translate Reports
```python
translator = FinancialTranslator()
translated = translator.translate_financial_summary(
    summary, target_lang='es'
)
```

## 🔮 Future Enhancements

- **Budget Planning**: Set and track budget goals
- **Investment Tracking**: Monitor investment accounts
- **Bill Reminders**: Automated payment reminders
- **Receipt Scanning**: OCR for receipt processing
- **Mobile App**: React Native mobile interface
- **Advanced Analytics**: Machine learning insights
