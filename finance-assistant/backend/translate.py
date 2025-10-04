"""
Multilingual translation using DeepL API
"""
import requests
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class FinancialTranslator:
    def __init__(self):
        self.deepl_api_key = os.getenv('DEEPL_API_KEY')
        self.deepl_url = "https://api-free.deepl.com/v2/translate"
        
        # Supported languages for financial reports
        self.supported_languages = {
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic'
        }
    
    def translate_text(self, text: str, target_lang: str = 'es') -> str:
        """Translate text to target language"""
        if not self.deepl_api_key:
            return self._fallback_translation(text, target_lang)
        
        try:
            headers = {
                'Authorization': f'DeepL-Auth-Key {self.deepl_api_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'text': text,
                'target_lang': target_lang.upper()
            }
            
            response = requests.post(self.deepl_url, headers=headers, data=data)
            response.raise_for_status()
            
            result = response.json()
            return result['translations'][0]['text']
        
        except Exception as e:
            print(f"DeepL translation failed: {e}")
            return self._fallback_translation(text, target_lang)
    
    def translate_financial_summary(self, summary: Dict, target_lang: str = 'es') -> Dict:
        """Translate a financial summary to target language"""
        translated = {}
        
        # Translate main metrics
        if 'total_income' in summary:
            translated['total_income'] = self.translate_text(f"Total Income: ${summary['total_income']}", target_lang)
        
        if 'total_expenses' in summary:
            translated['total_expenses'] = self.translate_text(f"Total Expenses: ${summary['total_expenses']}", target_lang)
        
        if 'net_worth' in summary:
            translated['net_worth'] = self.translate_text(f"Net Worth: ${summary['net_worth']}", target_lang)
        
        # Translate category breakdown
        if 'categories' in summary:
            translated['categories'] = []
            for category in summary['categories']:
                translated_category = {
                    'name': self.translate_text(category['name'], target_lang),
                    'amount': category['amount'],
                    'percentage': category['percentage']
                }
                translated['categories'].append(translated_category)
        
        return translated
    
    def translate_insights(self, insights: List[str], target_lang: str = 'es') -> List[str]:
        """Translate financial insights to target language"""
        translated_insights = []
        
        for insight in insights:
            translated_insight = self.translate_text(insight, target_lang)
            translated_insights.append(translated_insight)
        
        return translated_insights
    
    def translate_category_names(self, categories: List[str], target_lang: str = 'es') -> Dict[str, str]:
        """Translate category names to target language"""
        translated_categories = {}
        
        for category in categories:
            translated_name = self.translate_text(category, target_lang)
            translated_categories[category] = translated_name
        
        return translated_categories
    
    def _fallback_translation(self, text: str, target_lang: str) -> str:
        """Fallback translation using basic word mapping"""
        if target_lang == 'es':
            translations = {
                'Total Income': 'Ingresos Totales',
                'Total Expenses': 'Gastos Totales',
                'Net Worth': 'Patrimonio Neto',
                'Entertainment': 'Entretenimiento',
                'Groceries': 'Comestibles',
                'Transportation': 'Transporte',
                'Income': 'Ingresos',
                'Housing': 'Vivienda',
                'Subscriptions': 'Suscripciones',
                'Dining': 'Restaurantes',
                'Utilities': 'Servicios Públicos',
                'Healthcare': 'Salud',
                'Shopping': 'Compras',
                'Other': 'Otros'
            }
            
            for english, spanish in translations.items():
                text = text.replace(english, spanish)
        
        return text
    
    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        return self.supported_languages.get(lang_code, 'Unknown')
    
    def is_language_supported(self, lang_code: str) -> bool:
        """Check if language is supported"""
        return lang_code in self.supported_languages
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()