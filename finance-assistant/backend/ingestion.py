"""
PDF and CSV ingestion module for bank statements
"""
import pandas as pd
import PyPDF2
import re
from datetime import datetime
from typing import List, Dict, Any
import io

class StatementIngestion:
    def __init__(self):
        self.transaction_patterns = {
            'date': r'(\d{1,2}/\d{1,2}/\d{2,4})',
            'amount': r'(\$?[\d,]+\.\d{2})',
            'description': r'([A-Za-z0-9\s\-\.&,]+)'
        }
    
    def parse_pdf(self, pdf_path: str) -> pd.DataFrame:
        """Parse bank statement PDF and extract transactions"""
        transactions = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    page_transactions = self._extract_transactions_from_text(text)
                    transactions.extend(page_transactions)
        
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return pd.DataFrame()
        
        return self._create_dataframe(transactions)
    
    def parse_csv(self, csv_path: str) -> pd.DataFrame:
        """Parse CSV bank statement"""
        try:
            df = pd.read_csv(csv_path)
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            return df
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return pd.DataFrame()
    
    def _extract_transactions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract transaction data from PDF text"""
        transactions = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines that contain date, amount, and description
            if self._is_transaction_line(line):
                transaction = self._parse_transaction_line(line)
                if transaction:
                    transactions.append(transaction)
        
        return transactions
    
    def _is_transaction_line(self, line: str) -> bool:
        """Check if line contains transaction data"""
        # Look for date pattern and amount pattern
        has_date = re.search(self.transaction_patterns['date'], line)
        has_amount = re.search(self.transaction_patterns['amount'], line)
        return bool(has_date and has_amount)
    
    def _parse_transaction_line(self, line: str) -> Dict[str, Any]:
        """Parse individual transaction line"""
        try:
            # Extract date
            date_match = re.search(self.transaction_patterns['date'], line)
            date_str = date_match.group(1) if date_match else None
            
            # Extract amount
            amount_match = re.search(self.transaction_patterns['amount'], line)
            amount_str = amount_match.group(1) if amount_match else None
            
            if not date_str or not amount_str:
                return None
            
            # Clean amount
            amount = float(amount_str.replace('$', '').replace(',', ''))
            
            # Extract description (everything else)
            description = line.replace(date_str, '').replace(amount_str, '').strip()
            
            # Determine transaction type
            transaction_type = 'debit' if amount < 0 else 'credit'
            
            return {
                'date': self._parse_date(date_str),
                'amount': amount,
                'description': description,
                'type': transaction_type
            }
        
        except Exception as e:
            print(f"Error parsing line: {line} - {e}")
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            # Try different date formats
            for fmt in ['%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return datetime.now()
        except:
            return datetime.now()
    
    def _create_dataframe(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create pandas DataFrame from transactions"""
        if not transactions:
            return pd.DataFrame(columns=['date', 'amount', 'description', 'type'])
        
        df = pd.DataFrame(transactions)
        df['id'] = range(1, len(df) + 1)
        return df[['id', 'date', 'amount', 'description', 'type']]

# Sample data generator for demo
def create_sample_transactions() -> pd.DataFrame:
    """Create sample transaction data for demo purposes"""
    sample_data = [
        {'date': '2024-01-15', 'amount': -12.99, 'description': 'SPOTIFY PREMIUM', 'type': 'debit'},
        {'date': '2024-01-16', 'amount': -45.67, 'description': 'FOOD LION #1234', 'type': 'debit'},
        {'date': '2024-01-17', 'amount': -89.50, 'description': 'SHELL GAS STATION', 'type': 'debit'},
        {'date': '2024-01-18', 'amount': 2500.00, 'description': 'SALARY DEPOSIT', 'type': 'credit'},
        {'date': '2024-01-19', 'amount': -1200.00, 'description': 'RENT PAYMENT', 'type': 'debit'},
        {'date': '2024-01-20', 'amount': -75.00, 'description': 'T-MOBILE BILL', 'type': 'debit'},
        {'date': '2024-01-21', 'amount': -25.50, 'description': 'NETFLIX SUBSCRIPTION', 'type': 'debit'},
        {'date': '2024-01-22', 'amount': -15.99, 'description': 'AMAZON PRIME', 'type': 'debit'},
        {'date': '2024-01-23', 'amount': -8.50, 'description': 'STARBUCKS COFFEE', 'type': 'debit'},
        {'date': '2024-01-24', 'amount': -200.00, 'description': 'UTILITY BILL', 'type': 'debit'},
    ]
    
    df = pd.DataFrame(sample_data)
    df['date'] = pd.to_datetime(df['date'])
    df['id'] = range(1, len(df) + 1)
    return df[['id', 'date', 'amount', 'description', 'type']]