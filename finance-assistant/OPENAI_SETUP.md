# OpenAI Integration Setup Guide

This guide will help you set up OpenAI API integration for intelligent transaction categorization.

## Prerequisites

1. **OpenAI API Key**: You need an active OpenAI API account and API key
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Generate an API key from your account settings
   - Ensure you have credits available for API usage

## Setup Steps

### 1. Create Environment File

Create a `.env` file in the `finance-assistant` directory:

```bash
# Copy the example file
cp env_example.txt .env
```

### 2. Add Your OpenAI API Key

Edit the `.env` file and replace the placeholder with your actual API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Test the Integration

Run the test script to verify everything works:

```bash
python test_openai_categorization.py
```

## How It Works

The system uses a **hybrid approach**:

1. **Rule-based categorization first**: Fast pattern matching for common transactions
2. **OpenAI fallback**: AI-powered categorization for complex or unknown transactions

### Features

- **Intelligent categorization**: Uses GPT-3.5-turbo for accurate transaction classification
- **Subcategory detection**: Automatically suggests relevant subcategories
- **Context awareness**: Considers transaction amount and description context
- **Cost efficient**: Only uses OpenAI when rule-based matching fails

### Categories Supported

- Entertainment (streaming, gaming, movies, music)
- Groceries (food, household items)
- Transportation (gas, rideshare, parking)
- Income (salary, deposits, refunds)
- Housing (rent, mortgage, utilities)
- Subscriptions (monthly services)
- Dining (restaurants, coffee, fast food)
- Utilities (electric, water, internet, phone)
- Healthcare (medical, pharmacy)
- Shopping (retail, online purchases)
- Insurance (car, home, health)
- Education (courses, books, tuition)
- Travel (flights, hotels, vacation)
- Personal Care (gym, beauty, wellness)
- Charitable (donations, charity)
- Other (uncategorized)

## Usage Examples

### Single Transaction
```python
from backend.categorize import TransactionCategorizer

categorizer = TransactionCategorizer()
category, subcategory = categorizer.categorize_transaction(
    "Cryptocurrency purchase - Bitcoin", 
    -150.00
)
print(f"Category: {category}, Subcategory: {subcategory}")
```

### Batch Processing
```python
import pandas as pd
from backend.categorize import TransactionCategorizer

# Load your transaction data
df = pd.read_csv('your_transactions.csv')

# Categorize all transactions
categorizer = TransactionCategorizer()
categorized_df = categorizer.categorize_batch(df)
```

## Cost Considerations

- Uses GPT-3.5-turbo (cost-effective model)
- Only processes transactions that don't match rule-based patterns
- Typical cost: ~$0.001-0.002 per transaction
- 1000 transactions ≈ $1-2 in API costs

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Ensure `.env` file exists and contains your API key
   - Check that the key starts with `sk-`

2. **"OpenAI API error"**
   - Verify your API key is valid and has credits
   - Check your internet connection
   - Ensure you're not hitting rate limits

3. **Poor categorization results**
   - The system learns from context - try more descriptive transaction names
   - Consider adding custom rules for your specific use case

### Getting Help

- Check the test script output for detailed error messages
- Review the OpenAI API documentation for rate limits and usage
- The system will fall back to "Other" category if OpenAI fails
