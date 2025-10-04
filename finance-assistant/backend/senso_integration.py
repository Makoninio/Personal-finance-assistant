"""
Senso API integration for storing raw PDF text and structured transactions
"""
import requests
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class SensoIntegration:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('SENSO_API_KEY')
        self.base_url = 'https://sdk.senso.ai/api/v1'
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def upload_raw_text(self, title: str, raw_text: str, category_id: str = None) -> Optional[str]:
        """
        Upload raw PDF text to Senso /content/raw endpoint
        
        Args:
            title: Title for the content
            raw_text: Extracted text from PDF
            category_id: Optional category ID for organization
            
        Returns:
            content_id if successful, None otherwise
        """
        if not self.api_key:
            print("Warning: Senso API key not provided. Skipping upload.")
            return None
        
        data = {
            'title': title,
            'body': raw_text
        }
        
        if category_id:
            data['category_id'] = category_id
        
        try:
            response = requests.post(
                f'{self.base_url}/content/raw',
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                content_id = result.get('content_id')
                print(f"✅ Raw content uploaded successfully. Content ID: {content_id}")
                return content_id
            else:
                print(f"❌ Failed to upload raw content: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading raw content: {e}")
            return None
    
    def upload_structured_transactions(self, title: str, transactions: List[Dict[str, Any]], 
                                    category_id: str = None) -> Optional[str]:
        """
        Upload structured transactions to Senso /content/json endpoint
        
        Args:
            title: Title for the content
            transactions: List of structured transaction dictionaries
            category_id: Optional category ID for organization
            
        Returns:
            content_id if successful, None otherwise
        """
        if not self.api_key:
            print("Warning: Senso API key not provided. Skipping upload.")
            return None
        
        # Convert transactions to Senso format
        structured_data = {
            'title': title,
            'body': self._format_transactions_for_senso(transactions),
            'metadata': {
                'transaction_count': len(transactions),
                'upload_timestamp': datetime.now().isoformat(),
                'source': 'finance_assistant'
            }
        }
        
        if category_id:
            structured_data['category_id'] = category_id
        
        try:
            response = requests.post(
                f'{self.base_url}/content/json',
                headers=self.headers,
                json=structured_data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                content_id = result.get('content_id')
                print(f"✅ Structured transactions uploaded successfully. Content ID: {content_id}")
                return content_id
            else:
                print(f"❌ Failed to upload structured content: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading structured content: {e}")
            return None
    
    def _format_transactions_for_senso(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format transactions for Senso JSON upload
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Formatted list of transactions
        """
        formatted_transactions = []
        
        for transaction in transactions:
            formatted_transaction = {
                'id': transaction.get('id'),
                'date': transaction.get('date').isoformat() if hasattr(transaction.get('date'), 'isoformat') else str(transaction.get('date')),
                'amount': float(transaction.get('amount', 0)),
                'description': transaction.get('description', ''),
                'type': transaction.get('type', 'unknown'),
                'category': transaction.get('category', 'uncategorized'),
                'subcategory': transaction.get('subcategory', ''),
                'currency': 'USD'  # Default currency
            }
            
            # Add any additional fields
            if 'merchant' in transaction:
                formatted_transaction['merchant'] = transaction['merchant']
            if 'location' in transaction:
                formatted_transaction['location'] = transaction['location']
            
            formatted_transactions.append(formatted_transaction)
        
        return formatted_transactions
    
    def upload_both_formats(self, pdf_title: str, raw_text: str, transactions: List[Dict[str, Any]], 
                          category_id: str = None) -> Dict[str, Optional[str]]:
        """
        Upload both raw text and structured transactions to Senso
        
        Args:
            pdf_title: Title for the content
            raw_text: Extracted text from PDF
            transactions: List of structured transaction dictionaries
            category_id: Optional category ID for organization
            
        Returns:
            Dictionary with content_ids for both uploads
        """
        result = {
            'raw_content_id': None,
            'structured_content_id': None
        }
        
        # Upload raw text
        raw_title = f"{pdf_title} - Raw Text"
        result['raw_content_id'] = self.upload_raw_text(raw_title, raw_text, category_id)
        
        # Upload structured transactions
        structured_title = f"{pdf_title} - Structured Transactions"
        result['structured_content_id'] = self.upload_structured_transactions(
            structured_title, transactions, category_id
        )
        
        return result
    
    def test_connection(self) -> bool:
        """
        Test Senso API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.api_key:
            print("❌ No API key provided")
            return False
        
        try:
            # Try to get account info or similar endpoint
            response = requests.get(
                f'{self.base_url}/account',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Senso API connection successful")
                return True
            else:
                print(f"❌ Senso API connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Senso API connection error: {e}")
            return False
