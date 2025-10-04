"""
Demo script for Personal Finance AI Assistant
Run this to see the application in action
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ingestion import create_sample_transactions
from db import TransactionDB
from categorize import TransactionCategorizer
from insights import FinancialInsights
from explain import TransactionExplainer
from translate import FinancialTranslator

def main():
    print("💰 Personal Finance AI Assistant - Demo")
    print("=" * 50)
    
    # 1. Create sample data
    print("\n1. 📄 Creating sample transaction data...")
    sample_df = create_sample_transactions()
    print(f"   ✅ Created {len(sample_df)} sample transactions")
    
    # 2. Initialize database
    print("\n2. 🗄️ Initializing database...")
    db = TransactionDB()
    print("   ✅ Database initialized")
    
    # 3. Categorize transactions
    print("\n3. 🤖 Categorizing transactions...")
    categorizer = TransactionCategorizer()
    categorized_df = categorizer.categorize_batch(sample_df)
    print("   ✅ Transactions categorized")
    
    # Show categorization stats
    stats = categorizer.get_category_stats(categorized_df)
    print("   📊 Category breakdown:")
    for category, count in stats.items():
        print(f"      - {category}: {count} transactions")
    
    # 4. Store in database
    print("\n4. 💾 Storing transactions in database...")
    db.insert_transactions(categorized_df)
    print("   ✅ Transactions stored")
    
    # 5. Generate insights
    print("\n5. 📊 Generating financial insights...")
    insights = FinancialInsights(categorized_df)
    
    # Net worth
    net_worth = insights.get_net_worth_snapshot()
    print(f"   💰 Net Worth: ${net_worth['net_worth']:,.2f}")
    print(f"   📈 Total Income: ${net_worth['total_income']:,.2f}")
    print(f"   📉 Total Expenses: ${net_worth['total_expenses']:,.2f}")
    
    # Category breakdown
    category_breakdown = insights.get_category_breakdown()
    print("\n   📊 Top spending categories:")
    for _, row in category_breakdown.head(5).iterrows():
        print(f"      - {row['category']}: ${row['total_spent']:,.2f} ({row['percentage']:.1f}%)")
    
    # Financial health score
    health_score = insights.get_financial_health_score()
    print(f"\n   💚 Financial Health Score: {health_score['score']}/100")
    print("   📋 Health factors:")
    for factor in health_score['factors']:
        print(f"      - {factor}")
    
    # Recurring subscriptions
    subscriptions = insights.detect_recurring_subscriptions()
    print(f"\n   🔄 Recurring subscriptions detected: {len(subscriptions)}")
    for sub in subscriptions[:3]:  # Show top 3
        print(f"      - {sub['description']}: ${sub['amount']:.2f} ({sub['frequency']})")
    
    # 6. Explain a transaction
    print("\n6. 🔍 Explaining a transaction...")
    explainer = TransactionExplainer()
    
    # Pick a transaction to explain
    sample_transaction = categorized_df.iloc[0]
    explanations = explainer.explain_transaction(
        sample_transaction['description'],
        sample_transaction['amount'],
        sample_transaction.get('category')
    )
    
    print(f"   📝 Transaction: {sample_transaction['description']} (${sample_transaction['amount']:.2f})")
    for service, explanation in explanations.items():
        print(f"   🤖 {service.title()} explanation: {explanation}")
    
    # 7. Translation demo
    print("\n7. 🌍 Translation demo...")
    translator = FinancialTranslator()
    
    # Translate some text
    test_text = "Total Income: $2,500.00"
    translated = translator.translate_text(test_text, 'es')
    print(f"   🇪🇸 '{test_text}' → '{translated}'")
    
    # 8. Recommendations
    print("\n8. 💡 Budget recommendations...")
    recommendations = insights.get_budget_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\nTo run the full Streamlit app:")
    print("   streamlit run frontend/app.py")
    print("\nTo run tests:")
    print("   python -m pytest tests/")

if __name__ == "__main__":
    main()