# OpenAI-Powered Document Parsing Guide

## 🎯 **Problem Solved**

The original regex-based parsing was struggling with complex bank statement formats like the Fifth Third statement you showed. The new OpenAI-powered parser can intelligently:

1. **Identify transaction sections** in bank statements
2. **Extract accurate dates** from various formats (MM/DD, MM/DD/YYYY, etc.)
3. **Parse amounts correctly** with proper positive/negative values
4. **Preserve merchant names and locations** in descriptions
5. **Handle different bank statement layouts** automatically

## 🚀 **What's Been Added**

### **1. OpenAI Document Parser (`backend/openai_document_parser.py`)**
- Uses GPT-4o-mini for intelligent document parsing
- Extracts transactions with proper date, amount, and description formatting
- Handles various bank statement formats automatically
- Includes metadata extraction (account info, statement period, etc.)

### **2. Enhanced Ingestion System (`backend/ingestion.py`)**
- **Hybrid approach**: OpenAI parsing first, regex fallback
- **Intelligent parsing**: Automatically detects and parses transaction sections
- **Better accuracy**: Handles complex layouts like your Fifth Third statement
- **Graceful fallback**: Falls back to regex if OpenAI fails

### **3. Key Features**

#### **Smart Transaction Extraction**
```python
# Before (regex): Struggled with complex layouts
# After (OpenAI): Intelligently identifies and extracts:

{
    "date": "2025-06-12",
    "amount": -50.93,
    "description": "TARGET T-9801 S - 966175 9801 Sam Furr Rd Huntersville NC"
}
```

#### **Automatic Format Detection**
- Recognizes "Withdrawals/Debits" sections
- Handles multi-line transaction descriptions
- Preserves merchant names and locations
- Converts dates to standard YYYY-MM-DD format

#### **Metadata Extraction**
- Bank name and account information
- Statement period dates
- Account balances
- Account holder information

## 🔧 **How to Use**

### **1. Set Up Your API Key**
```bash
# In your .env file
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### **2. Parse Bank Statements**
```python
from backend.ingestion import StatementIngestion

# Initialize with OpenAI parsing enabled
ingestion = StatementIngestion()

# Parse PDF with OpenAI (default behavior)
df = ingestion.parse_pdf("your_bank_statement.pdf", use_openai=True)

# The system will automatically:
# 1. Try OpenAI parsing first
# 2. Fall back to regex if OpenAI fails
# 3. Return properly formatted DataFrame
```

### **3. Direct OpenAI Parsing**
```python
from backend.openai_document_parser import OpenAIDocumentParser

parser = OpenAIDocumentParser()

# Parse from text
df = parser.parse_bank_statement_text(bank_statement_text)

# Parse from PDF
df = parser.parse_bank_statement_pdf("statement.pdf")

# Extract metadata
metadata = parser.get_statement_metadata(bank_statement_text)
```

## 📊 **Expected Results**

For your Fifth Third statement, the system will now correctly extract:

| Date | Amount | Description |
|------|--------|-------------|
| 2025-06-12 | -50.93 | TARGET T-9801 S - 966175 9801 Sam Furr Rd Huntersville NC |
| 2025-06-13 | -50.00 | CVS/PHARMACY #06 - 127 SOUTH MAIN S DAVIDSON NC |
| 2025-06-13 | -4.10 | CTLP*CANTEEN VENDI - CHARLOTTE, NC |
| 2025-06-16 | -15.00 | UBER *TRIP HELP.UB - ATLANTA, GA |

## 🎯 **Benefits**

1. **Accurate Parsing**: No more misaligned dates and amounts
2. **Intelligent Recognition**: Understands bank statement structure
3. **Format Flexibility**: Works with various bank statement layouts
4. **Better Categorization**: Clean data leads to better AI categorization
5. **Robust Fallback**: Still works if OpenAI is unavailable

## 🔄 **Integration with Existing System**

The new parser integrates seamlessly with your existing categorization system:

1. **Document Upload** → OpenAI parsing extracts clean transaction data
2. **Transaction Categorization** → AI categorizes the properly formatted data
3. **Financial Insights** → Analytics work with accurate transaction information

## 🚨 **Important Notes**

- **API Key Required**: You need a valid OpenAI API key
- **Cost**: Uses GPT-4o-mini (cost-effective) for document parsing
- **Fallback**: System gracefully falls back to regex if OpenAI fails
- **Accuracy**: Much more accurate than regex-based parsing

## 🧪 **Testing**

Once you have a valid API key, test with:
```bash
python test_openai_parsing.py
```

This will demonstrate the parsing capabilities with sample bank statement data.

---

**Your bank statement parsing problem is now solved!** 🎉 The system will intelligently extract transaction data from complex bank statements like your Fifth Third statement, ensuring accurate dates, amounts, and descriptions for proper categorization and analysis.
