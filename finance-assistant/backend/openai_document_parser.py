"""
OpenAI-powered document parser for bank statements
Uses LLM to intelligently extract transaction data from various bank statement formats
"""
import openai
import os
import pandas as pd
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class OpenAIDocumentParser:
    def __init__(self):
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def parse_bank_statement_text(self, text: str) -> pd.DataFrame:
        """
        Parse bank statement text using OpenAI to extract transactions
        
        Args:
            text: Raw text extracted from PDF or document
            
        Returns:
            DataFrame with columns: id, date, amount, description, type
        """
        if not self.openai_client:
            print("❌ OpenAI API key not found. Please set OPENAI_API_KEY in .env file")
            return pd.DataFrame()
        
        try:
            # Extract transactions using OpenAI
            transactions = self._extract_transactions_with_openai(text)
            
            if not transactions:
                print("No transactions found in document")
                return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(transactions)
            
            # Add ID column
            df['id'] = range(1, len(df) + 1)
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Convert amount to numeric
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            # Determine transaction type
            df['type'] = df['amount'].apply(lambda x: 'credit' if x > 0 else 'debit')
            
            # Remove rows with missing critical data
            df = df.dropna(subset=['date', 'amount', 'description'])
            
            print(f"✅ Successfully extracted {len(df)} transactions using OpenAI")
            return df[['id', 'date', 'amount', 'description', 'type']]
            
        except Exception as e:
            print(f"Error parsing document with OpenAI: {e}")
            return pd.DataFrame()
    
    def _extract_transactions_with_openai(self, text: str) -> List[Dict[str, Any]]:
        """Use OpenAI to extract transaction data from bank statement text"""
        
        prompt = f"""
        You are a financial document parser. Extract transaction data from this bank statement text.

        Instructions:
        1. Look for transaction sections (usually labeled "Withdrawals/Debits", "Deposits/Credits", "Transactions", etc.)
        2. Extract each transaction with the following information:
           - Date (convert to YYYY-MM-DD format)
           - Amount (as decimal number, negative for debits, positive for credits)
           - Description (merchant name and transaction details)
        3. Ignore header information, account summaries, and non-transaction data
        4. Handle various date formats (MM/DD, MM/DD/YYYY, etc.)
        5. Handle various amount formats ($50.00, 50.00, etc.)
        6. Preserve merchant names and transaction descriptions accurately

        Bank Statement Text:
        {text}

        Return ONLY a valid JSON array of transactions in this exact format:
        [
            {{
                "date": "2025-06-12",
                "amount": -50.93,
                "description": "TARGET T-9801 S - 966175 9801 Sam Furr Rd Huntersville NC"
            }},
            {{
                "date": "2025-06-13", 
                "amount": -50.00,
                "description": "CVS/PHARMACY #06 - 127 SOUTH MAIN S DAVIDSON NC"
            }}
        ]

        Important:
        - Return ONLY the JSON array, no other text
        - Use negative amounts for debits/withdrawals
        - Use positive amounts for credits/deposits
        - Ensure all dates are in YYYY-MM-DD format
        - Include the full merchant name and location in description
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using more capable model for document parsing
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response to extract JSON
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            # Parse JSON
            transactions = json.loads(result)
            
            if not isinstance(transactions, list):
                print("Error: OpenAI returned non-list format")
                return []
            
            return transactions
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from OpenAI response: {e}")
            print(f"Raw response: {result}")
            return []
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return []
    
    def parse_bank_statement_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Parse bank statement PDF using OpenAI
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            DataFrame with transaction data
        """
        try:
            import PyPDF2
            
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            print(f"Extracted {len(text)} characters from PDF")
            
            # Parse with OpenAI
            return self.parse_bank_statement_text(text)
            
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return pd.DataFrame()
    
    def get_statement_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract metadata from bank statement (account info, statement period, etc.)
        
        Args:
            text: Raw text from bank statement
            
        Returns:
            Dictionary with metadata
        """
        if not self.openai_client:
            return {}
        
        prompt = f"""
        Extract key metadata from this bank statement text.

        Bank Statement Text:
        {text}

        Return ONLY a valid JSON object with this structure:
        {{
            "bank_name": "Bank Name",
            "account_number": "Account Number",
            "account_type": "Account Type",
            "statement_period_start": "YYYY-MM-DD",
            "statement_period_end": "YYYY-MM-DD",
            "beginning_balance": 0.00,
            "ending_balance": 0.00,
            "account_holder": "Account Holder Name"
        }}

        Important:
        - Return ONLY the JSON object, no other text
        - Use null for missing information
        - Ensure dates are in YYYY-MM-DD format
        - Extract balances as decimal numbers
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result)
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {}
