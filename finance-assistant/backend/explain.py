"""
AI-powered transaction explanation using OpenAI and Perplexity
"""
import openai
import requests
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class TransactionExplainer:
    def __init__(self):
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
    
    def explain_transaction(self, description: str, amount: float, category: str = None) -> Dict[str, str]:
        """
        Explain a transaction using AI services
        Returns explanation from both OpenAI and Perplexity if available
        """
        explanations = {}
        
        # Get OpenAI explanation
        if self.openai_client:
            try:
                openai_explanation = self._get_openai_explanation(description, amount, category)
                explanations['openai'] = openai_explanation
            except Exception as e:
                print(f"OpenAI explanation failed: {e}")
                explanations['openai'] = "OpenAI explanation unavailable"
        
        # Get Perplexity explanation
        if self.perplexity_api_key:
            try:
                perplexity_explanation = self._get_perplexity_explanation(description, amount, category)
                explanations['perplexity'] = perplexity_explanation
            except Exception as e:
                print(f"Perplexity explanation failed: {e}")
                explanations['perplexity'] = "Perplexity explanation unavailable"
        
        # If no AI services available, provide basic explanation
        if not explanations:
            explanations['basic'] = self._get_basic_explanation(description, amount, category)
        
        return explanations
    
    def _get_openai_explanation(self, description: str, amount: float, category: str = None) -> str:
        """Get explanation from OpenAI"""
        prompt = f"""
        Explain this bank transaction in simple terms:
        
        Description: {description}
        Amount: ${amount:.2f}
        Category: {category or 'Unknown'}
        
        Provide a brief explanation of what this transaction likely represents, 
        including any context about the merchant or service. Keep it concise and helpful.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    def _get_perplexity_explanation(self, description: str, amount: float, category: str = None) -> str:
        """Get explanation from Perplexity API"""
        prompt = f"""
        What is {description}? Explain this merchant or service in the context of a ${amount:.2f} transaction.
        """
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 150,
            "temperature": 0.3
        }
        
        response = requests.post(self.perplexity_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    def _get_basic_explanation(self, description: str, amount: float, category: str = None) -> str:
        """Provide basic explanation without AI services"""
        explanations = {
            'spotify': 'Music streaming service subscription',
            'netflix': 'Video streaming service subscription',
            'food lion': 'Grocery store chain',
            'shell': 'Gas station chain',
            't-mobile': 'Mobile phone service provider',
            'amazon': 'Online shopping and services',
            'starbucks': 'Coffee shop chain',
            'salary': 'Regular income payment',
            'rent': 'Housing payment'
        }
        
        description_lower = description.lower()
        
        for key, explanation in explanations.items():
            if key in description_lower:
                return f"{explanation} - ${amount:.2f}"
        
        return f"Transaction to {description} for ${amount:.2f}"
    
    def get_merchant_context(self, description: str) -> Dict[str, str]:
        """Get additional context about a merchant"""
        context = {}
        
        # Basic merchant information
        merchant_info = {
            'spotify': {
                'type': 'Music Streaming',
                'website': 'spotify.com',
                'description': 'Premium music streaming service'
            },
            'netflix': {
                'type': 'Video Streaming',
                'website': 'netflix.com',
                'description': 'Video streaming and production company'
            },
            'food lion': {
                'type': 'Grocery Store',
                'website': 'foodlion.com',
                'description': 'Regional grocery store chain'
            },
            'shell': {
                'type': 'Gas Station',
                'website': 'shell.com',
                'description': 'International energy company'
            },
            't-mobile': {
                'type': 'Telecommunications',
                'website': 't-mobile.com',
                'description': 'Mobile network operator'
            },
            'amazon': {
                'type': 'E-commerce',
                'website': 'amazon.com',
                'description': 'Online retail and cloud services'
            },
            'starbucks': {
                'type': 'Coffee Shop',
                'website': 'starbucks.com',
                'description': 'Coffeehouse chain'
            }
        }
        
        description_lower = description.lower()
        
        for key, info in merchant_info.items():
            if key in description_lower:
                context = info
                break
        
        if not context:
            context = {
                'type': 'Unknown',
                'website': 'N/A',
                'description': 'Merchant information not available'
            }
        
        return context
    
    def suggest_budget_adjustments(self, description: str, amount: float, category: str) -> List[str]:
        """Suggest budget adjustments based on transaction"""
        suggestions = []
        
        if category == 'Entertainment' and amount > 50:
            suggestions.append("Consider reducing entertainment spending")
        
        if category == 'Dining' and amount > 30:
            suggestions.append("Try cooking at home more often")
        
        if category == 'Transportation' and amount > 100:
            suggestions.append("Consider carpooling or public transport")
        
        if category == 'Subscriptions' and amount > 20:
            suggestions.append("Review if this subscription is necessary")
        
        if amount > 200 and category not in ['Income', 'Housing']:
            suggestions.append("This is a large expense - consider if it's essential")
        
        return suggestions