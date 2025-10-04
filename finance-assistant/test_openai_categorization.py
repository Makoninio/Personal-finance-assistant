"""
Test script for OpenAI-based transaction categorization
"""
import os
import sys
from dotenv import load_dotenv
from backend.categorize import TransactionCategorizer
import pandas as pd

# Load environment variables
load_dotenv()

def test_openai_categorization():
    """Test the OpenAI categorization functionality"""
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API key not found!")
        print("Please set your OpenAI API key in the .env file:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return False
    
    print("✅ OpenAI API key found!")
    
    # Initialize categorizer
    categorizer = TransactionCategorizer()
    
    # Test transactions that should trigger OpenAI categorization
    test_transactions = [
        {"description": "Mysterious charge from unknown merchant", "amount": -29.99},
        {"description": "Cryptocurrency purchase - Bitcoin", "amount": -150.00},
        {"description": "Online course - Python Programming", "amount": -89.99},
        {"description": "Pet grooming service", "amount": -45.00},
        {"description": "Gym membership renewal", "amount": -39.99},
        {"description": "Charity donation to Red Cross", "amount": -25.00},
        {"description": "Book purchase from local bookstore", "amount": -18.50},
        {"description": "Car insurance payment", "amount": -120.00},
        {"description": "Freelance payment received", "amount": 500.00},
        {"description": "ATM withdrawal fee", "amount": -3.50}
    ]
    
    print("\n🧠 Testing LLM-based categorization...")
    print("=" * 60)
    
    results = []
    for i, transaction in enumerate(test_transactions, 1):
        print(f"\nTransaction {i}: {transaction['description']} (${transaction['amount']})")
        
        category, subcategory = categorizer.categorize_transaction(
            transaction['description'], 
            transaction['amount']
        )
        
        result = {
            'description': transaction['description'],
            'amount': transaction['amount'],
            'category': category,
            'subcategory': subcategory
        }
        results.append(result)
        
        print(f"  → Category: {category}")
        if subcategory:
            print(f"  → Subcategory: {subcategory}")
    
    # Create DataFrame and display results
    df = pd.DataFrame(results)
    print("\n📊 Categorization Results:")
    print("=" * 60)
    print(df.to_string(index=False))
    
    # Show category distribution
    print("\n📈 Category Distribution:")
    print("=" * 30)
    category_counts = df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"{category}: {count}")
    
    return True

def test_with_sample_data():
    """Test with the sample transactions data"""
    print("\n📁 Testing with sample transactions data...")
    print("=" * 50)
    
    # Load sample data
    sample_df = pd.read_csv('data/sample_transactions.csv')
    
    # Remove existing categories to test fresh categorization
    test_df = sample_df[['description', 'amount']].copy()
    
    categorizer = TransactionCategorizer()
    categorized_df = categorizer.categorize_batch(test_df)
    
    print("Sample categorization results:")
    print(categorized_df[['description', 'amount', 'category', 'subcategory']].to_string(index=False))
    
    return categorized_df

if __name__ == "__main__":
    print("🚀 OpenAI Transaction Categorization Test")
    print("=" * 50)
    
    # Test OpenAI integration
    success = test_openai_categorization()
    
    if success:
        # Test with sample data
        test_with_sample_data()
        
        print("\n✅ All tests completed!")
        print("\nTo use this in your application:")
        print("1. Set your OpenAI API key in the .env file")
        print("2. Import and use TransactionCategorizer from backend.categorize")
        print("3. Call categorize_transaction() for single transactions")
        print("4. Call categorize_batch() for DataFrames")
    else:
        print("\n❌ Please set up your OpenAI API key first!")
