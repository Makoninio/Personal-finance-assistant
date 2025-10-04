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
        # More flexible patterns for generic bank statements
        self.transaction_patterns = {
            # Date patterns - handle various formats
            'date': r'(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?)',
            # Amount patterns - handle with/without $, with/without decimals
            'amount': r'(\$?[\d,]+(?:\.\d{2})?)',
            # Description patterns - very permissive
            'description': r'([A-Za-z0-9\s\-\.&,()*#/]+)'
        }
        
        # Additional patterns for different statement formats
        self.alternative_patterns = {
            'date_only': r'^(\d{1,2}[/\-]\d{1,2})',
            'amount_only': r'(\$?[\d,]+(?:\.\d{2})?)$',
            'debit_card': r'DEBIT CARD',
            'check': r'CHECK',
            'zelle': r'ZELLE',
            'transfer': r'TRANSFER'
        }
    
    def parse_pdf(self, pdf_path: str) -> pd.DataFrame:
        """Parse bank statement PDF and extract transactions"""
        transactions = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if not text:
                        print(f"No text extracted from page {page_num + 1}")
                        continue
                    
                    print(f"Page {page_num + 1} text length: {len(text)} characters")
                    lines = text.split("\n")
                    print(f"Page {page_num + 1} has {len(lines)} lines")
                    
                    page_transactions = self._extract_transactions_from_text(lines)
                    transactions.extend(page_transactions)
                    print(f"Page {page_num + 1}: Found {len(page_transactions)} transactions")
                    
                    # Debug: show first few lines of text
                    if page_num == 0:
                        print("First 10 lines of text:")
                        for i, line in enumerate(lines[:10]):
                            print(f"  {i+1}: {line}")

        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return pd.DataFrame()

        print(f"Total transactions found: {len(transactions)}")
        return self._create_dataframe(transactions)

    
    def parse_csv(self, csv_path: str) -> pd.DataFrame:
        """Parse CSV bank statement"""
        try:
            df = pd.read_csv(csv_path)
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Check if we have the required columns
            required_columns = ['date', 'amount', 'description']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Missing required columns: {missing_columns}")
                print(f"Available columns: {list(df.columns)}")
                return pd.DataFrame()
            
            # Convert date column to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Ensure amount is numeric
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            # Add type column if not present
            if 'type' not in df.columns:
                df['type'] = df['amount'].apply(lambda x: 'credit' if x > 0 else 'debit')
            
            # Add ID column if not present
            if 'id' not in df.columns:
                df['id'] = range(1, len(df) + 1)
            
            # Remove rows with missing critical data
            df = df.dropna(subset=['date', 'amount', 'description'])
            
            return df[['id', 'date', 'amount', 'description', 'type']]
            
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return pd.DataFrame()
    
    def _extract_transactions_from_text(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract transaction data from PDF text lines using multiple strategies"""
        transactions = []
        
        # Strategy 1: Look for complete transaction lines
        for i, line in enumerate(lines):
            if self._is_transaction_line(line):
                transaction = self._parse_transaction_line(line)
                if transaction:
                    transactions.append(transaction)
        
        # Strategy 2: Look for multi-line transactions
        if not transactions:
            transactions = self._extract_multiline_transactions(lines)
        
        # Strategy 3: Fallback - look for any line with date and amount
        if not transactions:
            transactions = self._extract_fallback_transactions(lines)
        
        return transactions
    
    def _extract_multiline_transactions(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract transactions that span multiple lines"""
        transactions = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for lines that start with a date
            date_match = re.search(self.alternative_patterns['date_only'], line)
            if date_match:
                # Found a potential transaction start
                transaction_lines = [line]
                
                # Look for continuation lines (next lines that don't start with date)
                j = i + 1
                while j < len(lines) and j < i + 5:  # Max 5 lines per transaction
                    next_line = lines[j].strip()
                    if not next_line:
                        break
                    
                    # If next line starts with date, it's a new transaction
                    if re.search(self.alternative_patterns['date_only'], next_line):
                        break
                    
                    transaction_lines.append(next_line)
                    j += 1
                
                # Combine lines and try to parse
                combined_line = ' '.join(transaction_lines)
                transaction = self._parse_transaction_line(combined_line)
                if transaction:
                    transactions.append(transaction)
                
                i = j
            else:
                i += 1
        
        return transactions
    
    def _extract_fallback_transactions(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Fallback method - look for any line with date and amount"""
        transactions = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
            
            # Look for any line that has both date and amount patterns
            has_date = re.search(self.transaction_patterns['date'], line)
            has_amount = re.search(self.transaction_patterns['amount'], line)
            
            if has_date and has_amount:
                transaction = self._parse_transaction_line(line)
                if transaction:
                    transactions.append(transaction)
        
        return transactions
    
    def _is_transaction_line(self, line: str) -> bool:
        """Check if line contains transaction data - more flexible approach"""
        line = line.strip()
        
        # Skip empty lines or very short lines
        if len(line) < 5:
            return False
        
        # Look for date pattern and amount pattern
        has_date = re.search(self.transaction_patterns['date'], line)
        has_amount = re.search(self.transaction_patterns['amount'], line)
        
        # Check for transaction indicators
        transaction_indicators = [
            'debit card', 'check', 'zelle', 'transfer', 'payment', 'purchase',
            'withdrawal', 'deposit', 'fee', 'charge', 'refund', 'credit'
        ]
        has_transaction_indicator = any(indicator in line.lower() for indicator in transaction_indicators)
        
        # Check for common non-transaction keywords to skip
        skip_keywords = [
            'balance', 'statement', 'page', 'account', 'summary', 'total',
            'beginning', 'ending', 'previous', 'current', 'available',
            'date', 'description', 'amount', 'deposits', 'withdrawals'
        ]
        has_skip_keyword = any(keyword in line.lower() for keyword in skip_keywords)
        
        # More flexible: either has date+amount OR has transaction indicator with amount
        is_transaction = (has_date and has_amount) or (has_transaction_indicator and has_amount)
        
        return is_transaction and not has_skip_keyword
    
    def _parse_transaction_line(self, line: str) -> Dict[str, Any]:
        """Parse individual transaction line - more flexible approach"""
        try:
            # Try to find date and amount in the line
            date_str = None
            amount_str = None
            
            # Look for date patterns
            date_match = re.search(self.transaction_patterns['date'], line)
            if date_match:
                date_str = date_match.group(1)
            
            # Look for amount patterns (try multiple approaches)
            amount_matches = re.findall(self.transaction_patterns['amount'], line)
            if amount_matches:
                # Take the last amount found (usually the transaction amount)
                amount_str = amount_matches[-1]
            
            # If no date found, try alternative patterns
            if not date_str:
                alt_date_match = re.search(self.alternative_patterns['date_only'], line)
                if alt_date_match:
                    date_str = alt_date_match.group(1)
            
            # If no amount found, try alternative patterns
            if not amount_str:
                alt_amount_match = re.search(self.alternative_patterns['amount_only'], line)
                if alt_amount_match:
                    amount_str = alt_amount_match.group(1)
            
            if not date_str or not amount_str:
                print(f"Missing date or amount in line: {line}")
                return None
            
            # Clean amount
            amount = float(amount_str.replace('$', '').replace(',', ''))
            
            # Extract description (everything except date and amount)
            description = line
            if date_str:
                description = description.replace(date_str, '', 1)
            if amount_str:
                description = description.replace(amount_str, '', 1)
            
            # Clean up description
            description = re.sub(r'\s+', ' ', description).strip()
            
            # Skip if description is too short or empty
            if len(description) < 3:
                print(f"Description too short in line: {line}")
                return None
            
            # Determine transaction type based on context
            transaction_type = self._determine_transaction_type(line, amount)
            
            return {
                'date': self._parse_date(date_str),
                'amount': amount,
                'description': description,
                'type': transaction_type
            }
        
        except Exception as e:
            print(f"Error parsing line: {line} - {e}")
            return None
    
    def _determine_transaction_type(self, line: str, amount: float) -> str:
        """Determine transaction type based on line content and amount"""
        line_lower = line.lower()
        
        # Check for specific transaction types
        if any(keyword in line_lower for keyword in ['debit card', 'purchase', 'withdrawal', 'fee', 'charge']):
            return 'debit'
        elif any(keyword in line_lower for keyword in ['deposit', 'credit', 'refund', 'transfer in']):
            return 'credit'
        elif any(keyword in line_lower for keyword in ['zelle', 'payment', 'transfer']):
            return 'debit' if amount < 0 else 'credit'
        else:
            # Default based on amount
            return 'debit' if amount < 0 else 'credit'
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object - handles MM/DD format"""
        try:
            # Clean date string
            date_str = date_str.strip()
            
            # Handle MM/DD format (assume current year)
            if re.match(r'^\d{1,2}[/\-]\d{1,2}$', date_str):
                # Add current year
                current_year = datetime.now().year
                if '/' in date_str:
                    date_str = f"{date_str}/{current_year}"
                else:
                    date_str = f"{date_str}-{current_year}"
            
            # Try different date formats
            formats = [
                '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
                '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y', '%d-%m-%y',
                '%Y-%m-%d', '%y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            print(f"Could not parse date: {date_str}")
            return datetime.now()
        except Exception as e:
            print(f"Error parsing date {date_str}: {e}")
            return datetime.now()
    
    def _create_dataframe(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create pandas DataFrame from transactions"""
        if not transactions:
            return pd.DataFrame(columns=['date', 'amount', 'description', 'type'])
        
        df = pd.DataFrame(transactions)
        df['id'] = range(1, len(df) + 1)
        return df[['id', 'date', 'amount', 'description', 'type']]
