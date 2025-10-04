"""
Unit tests for transaction categorization
"""
import unittest
import pandas as pd
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from categorize import TransactionCategorizer

class TestTransactionCategorizer(unittest.TestCase):
    def setUp(self):
        self.categorizer = TransactionCategorizer()
    
    def test_rule_based_categorization(self):
        """Test rule-based categorization"""
        test_cases = [
            ("SPOTIFY PREMIUM", -12.99, "Entertainment", "Streaming"),
            ("FOOD LION #1234", -45.67, "Groceries", None),
            ("SHELL GAS STATION", -89.50, "Transportation", "Gas"),
            ("SALARY DEPOSIT", 2500.00, "Income", None),
            ("RENT PAYMENT", -1200.00, "Housing", None),
            ("T-MOBILE BILL", -75.00, "Subscriptions", None),
            ("NETFLIX SUBSCRIPTION", -25.50, "Entertainment", "Streaming"),
            ("STARBUCKS COFFEE", -8.50, "Dining", "Coffee"),
            ("UTILITY BILL", -200.00, "Utilities", None),
            ("CVS PHARMACY", -45.00, "Healthcare", None),
            ("AMAZON PURCHASE", -120.00, "Shopping", None),
            ("UBER RIDE", -35.00, "Transportation", "Rideshare"),
            ("PARKING FEE", -12.00, "Transportation", "Parking"),
        ]
        
        for description, amount, expected_category, expected_subcategory in test_cases:
            with self.subTest(description=description):
                category, subcategory = self.categorizer.categorize_transaction(description, amount)
                self.assertEqual(category, expected_category)
                self.assertEqual(subcategory, expected_subcategory)
    
    def test_batch_categorization(self):
        """Test batch categorization"""
        test_data = pd.DataFrame({
            'description': [
                'SPOTIFY PREMIUM',
                'FOOD LION #1234',
                'SHELL GAS STATION',
                'SALARY DEPOSIT'
            ],
            'amount': [-12.99, -45.67, -89.50, 2500.00]
        })
        
        result_df = self.categorizer.categorize_batch(test_data)
        
        self.assertIn('category', result_df.columns)
        self.assertIn('subcategory', result_df.columns)
        self.assertEqual(len(result_df), 4)
        
        # Check specific categorizations
        spotify_row = result_df[result_df['description'] == 'SPOTIFY PREMIUM'].iloc[0]
        self.assertEqual(spotify_row['category'], 'Entertainment')
        self.assertEqual(spotify_row['subcategory'], 'Streaming')
    
    def test_category_stats(self):
        """Test category statistics"""
        test_data = pd.DataFrame({
            'description': [
                'SPOTIFY PREMIUM',
                'FOOD LION #1234',
                'SHELL GAS STATION',
                'SALARY DEPOSIT',
                'SPOTIFY PREMIUM'  # Duplicate
            ],
            'amount': [-12.99, -45.67, -89.50, 2500.00, -12.99],
            'category': ['Entertainment', 'Groceries', 'Transportation', 'Income', 'Entertainment']
        })
        
        stats = self.categorizer.get_category_stats(test_data)
        
        self.assertIn('Entertainment', stats)
        self.assertEqual(stats['Entertainment'], 2)
        self.assertEqual(stats['Groceries'], 1)
    
    def test_unknown_transaction(self):
        """Test handling of unknown transactions"""
        category, subcategory = self.categorizer.categorize_transaction("UNKNOWN MERCHANT", -50.00)
        self.assertEqual(category, "Other")
        self.assertIsNone(subcategory)
    
    def test_case_insensitive_matching(self):
        """Test case insensitive pattern matching"""
        test_cases = [
            ("spotify premium", -12.99, "Entertainment"),
            ("Food Lion", -45.67, "Groceries"),
            ("shell gas", -89.50, "Transportation"),
            ("StArBuCkS", -8.50, "Dining"),
        ]
        
        for description, amount, expected_category in test_cases:
            with self.subTest(description=description):
                category, _ = self.categorizer.categorize_transaction(description, amount)
                self.assertEqual(category, expected_category)

if __name__ == '__main__':
    unittest.main()