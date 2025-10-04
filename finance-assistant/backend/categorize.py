"""
Transaction categorization using rule-based matching and OpenAI fallback
"""
import re
import openai
import os
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class TransactionCategorizer:
    def __init__(self):
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Rule-based categorization patterns
        self.category_rules = {
            'Entertainment': [
                r'spotify', r'netflix', r'hulu', r'disney', r'prime', r'amazon prime',
                r'youtube', r'twitch', r'steam', r'xbox', r'playstation', r'apple music',
                r'pandora', r'soundcloud', r'itunes', r'google play'
            ],
            'Groceries': [
                r'food lion', r'kroger', r'walmart', r'target', r'whole foods',
                r'trader joe', r'aldi', r'publix', r'safeway', r'giant eagle',
                r'grocery', r'supermarket', r'food', r'grocery store'
            ],
            'Transportation': [
                r'shell', r'exxon', r'bp', r'chevron', r'gas station', r'fuel',
                r'uber', r'lyft', r'taxi', r'parking', r'toll', r'public transport',
                r'bus', r'train', r'metro', r'subway'
            ],
            'Income': [
                r'salary', r'payroll', r'deposit', r'bonus', r'refund', r'income',
                r'paycheck', r'direct deposit', r'wage'
            ],
            'Housing': [
                r'rent', r'mortgage', r'apartment', r'property', r'landlord',
                r'home', r'house', r'lease'
            ],
            'Subscriptions': [
                r'subscription', r'monthly', r'annual', r'recurring', r'auto-pay',
                r'auto pay', r'bill pay', r'payment'
            ],
            'Dining': [
                r'restaurant', r'cafe', r'coffee', r'starbucks', r'dunkin',
                r'mcdonald', r'burger king', r'kfc', r'pizza', r'dining',
                r'food truck', r'fast food', r'delivery'
            ],
            'Utilities': [
                r'electric', r'water', r'gas', r'internet', r'cable', r'phone',
                r'utility', r'power', r'sewer', r'trash', r'waste'
            ],
            'Healthcare': [
                r'pharmacy', r'medical', r'doctor', r'hospital', r'clinic',
                r'health', r'dental', r'vision', r'prescription', r'cvs',
                r'walgreens', r'rite aid'
            ],
            'Shopping': [
                r'amazon', r'ebay', r'etsy', r'shop', r'store', r'retail',
                r'purchase', r'buy', r'mall', r'department store'
            ]
        }
        
        # Subcategory mappings for more specific categorization
        self.subcategory_rules = {
            'Entertainment': {
                'Streaming': [r'spotify', r'netflix', r'hulu', r'disney', r'prime'],
                'Gaming': [r'steam', r'xbox', r'playstation', r'gaming'],
                'Music': [r'spotify', r'apple music', r'pandora', r'soundcloud']
            },
            'Transportation': {
                'Gas': [r'shell', r'exxon', r'bp', r'chevron', r'gas station'],
                'Rideshare': [r'uber', r'lyft', r'taxi'],
                'Parking': [r'parking', r'toll']
            },
            'Dining': {
                'Coffee': [r'starbucks', r'dunkin', r'coffee', r'cafe'],
                'Fast Food': [r'mcdonald', r'burger king', r'kfc', r'fast food'],
                'Restaurants': [r'restaurant', r'dining', r'fine dining']
            }
        }
    
    def categorize_transaction(self, description: str, amount: float) -> Tuple[str, Optional[str]]:
        """
        Categorize a transaction using rule-based matching first, then OpenAI if needed
        Returns (category, subcategory)
        """
        description_lower = description.lower().strip()
        
        # Try rule-based categorization first
        category, subcategory = self._rule_based_categorization(description_lower)
        
        if category != 'Other':
            return category, subcategory
        
        # If no rule matches and OpenAI is available, use AI categorization
        if self.openai_client:
            try:
                ai_category, ai_subcategory = self._ai_categorization(description, amount)
                return ai_category, ai_subcategory
            except Exception as e:
                print(f"OpenAI categorization failed: {e}")
        
        return 'Other', None
    
    def _rule_based_categorization(self, description: str) -> Tuple[str, Optional[str]]:
        """Apply rule-based categorization"""
        for category, patterns in self.category_rules.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    # Check for subcategory
                    subcategory = self._get_subcategory(category, description)
                    return category, subcategory
        
        return 'Other', None
    
    def _get_subcategory(self, category: str, description: str) -> Optional[str]:
        """Get subcategory for a given category and description"""
        if category in self.subcategory_rules:
            for subcat, patterns in self.subcategory_rules[category].items():
                for pattern in patterns:
                    if re.search(pattern, description, re.IGNORECASE):
                        return subcat
        return None
    
    def _ai_categorization(self, description: str, amount: float) -> Tuple[str, Optional[str]]:
        """Use OpenAI to categorize transaction"""
        prompt = f"""
        You are a financial transaction categorization expert. Analyze this bank transaction and categorize it accurately.

        Transaction Details:
        - Description: "{description}"
        - Amount: ${amount:.2f}
        - Amount Type: {"Credit (money in)" if amount > 0 else "Debit (money out)"}

        Available Categories:
        - Entertainment: streaming services, gaming, movies, music, sports, hobbies
        - Groceries: food shopping, household essentials, supermarkets
        - Transportation: gas, rideshare, parking, public transit, vehicle expenses
        - Income: salary, wages, deposits, refunds, freelance payments
        - Housing: rent, mortgage, property taxes, home maintenance
        - Subscriptions: recurring monthly/annual services, memberships
        - Dining: restaurants, coffee shops, food delivery, fast food
        - Utilities: electricity, water, gas, internet, phone, cable
        - Healthcare: medical expenses, pharmacy, doctor visits, insurance
        - Shopping: retail purchases, online shopping, clothing, electronics
        - Insurance: car, home, health, life insurance payments
        - Education: courses, books, school supplies, tuition
        - Travel: flights, hotels, vacation expenses
        - Personal Care: gym, beauty, wellness services
        - Charitable: donations, charity contributions
        - Other: uncategorized or miscellaneous expenses

        Instructions:
        1. Consider the transaction description, amount, and context
        2. Choose the most appropriate category
        3. If applicable, suggest a relevant subcategory
        4. For income transactions, use "Income" category
        5. Be specific but not overly granular

        Respond with ONLY the category name and optional subcategory in this exact format: "CategoryName: SubcategoryName" or just "CategoryName" if no subcategory applies.
        
        Examples:
        - "Shopping: Electronics"
        - "Entertainment: Streaming"
        - "Other"
        - "Income"
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response
            result = result.strip()
            if ':' in result:
                parts = result.split(':', 1)
                category = parts[0].strip()
                subcategory = parts[1].strip() if parts[1].strip() else None
                return category, subcategory
            else:
                return result, None
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return 'Other', None
    
    def categorize_batch(self, transactions_df) -> pd.DataFrame:
        """Categorize a batch of transactions"""
        categories = []
        subcategories = []
        
        for _, row in transactions_df.iterrows():
            category, subcategory = self.categorize_transaction(
                row['description'], 
                row['amount']
            )
            categories.append(category)
            subcategories.append(subcategory)
        
        transactions_df['category'] = categories
        transactions_df['subcategory'] = subcategories
        
        return transactions_df
    
    def get_category_stats(self, transactions_df) -> Dict[str, int]:
        """Get statistics about categorization results"""
        if 'category' not in transactions_df.columns:
            return {}
        
        return transactions_df['category'].value_counts().to_dict()