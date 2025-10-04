"""
Database operations for storing and retrieving transactions
"""
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

class TransactionDB:
    def __init__(self, db_path: str = "data/transactions.db"):
        self.db_path = db_path
        self._ensure_data_dir()
        self._create_tables()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Create necessary database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT,
                    subcategory TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    color TEXT
                )
            ''')
            
            # Insert default categories
            self._insert_default_categories()
            
            conn.commit()
    
    def _insert_default_categories(self):
        """Insert default category mappings"""
        default_categories = [
            ('Entertainment', 'Movies, music, streaming services', '#FF6B6B'),
            ('Groceries', 'Food and household items', '#4ECDC4'),
            ('Transportation', 'Gas, parking, public transport', '#45B7D1'),
            ('Income', 'Salary, bonuses, refunds', '#96CEB4'),
            ('Housing', 'Rent, mortgage, utilities', '#FFEAA7'),
            ('Subscriptions', 'Monthly recurring services', '#DDA0DD'),
            ('Dining', 'Restaurants, coffee shops', '#98D8C8'),
            ('Utilities', 'Electricity, water, internet', '#F7DC6F'),
            ('Other', 'Uncategorized expenses', '#BB8FCE')
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for name, desc, color in default_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, description, color)
                    VALUES (?, ?, ?)
                ''', (name, desc, color))
            conn.commit()
    
    def insert_transactions(self, transactions_df: pd.DataFrame) -> bool:
        """Insert transactions into database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                transactions_df.to_sql('transactions', conn, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"Error inserting transactions: {e}")
            return False
    
    def get_all_transactions(self) -> pd.DataFrame:
        """Retrieve all transactions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT t.*, c.name as category_name, c.color as category_color
                    FROM transactions t
                    LEFT JOIN categories c ON t.category = c.name
                    ORDER BY t.date DESC
                '''
                return pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error retrieving transactions: {e}")
            return pd.DataFrame()
    
    def update_transaction_category(self, transaction_id: int, category: str, subcategory: str = None) -> bool:
        """Update transaction category"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE transactions 
                    SET category = ?, subcategory = ?
                    WHERE id = ?
                ''', (category, subcategory, transaction_id))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error updating category: {e}")
            return False
    
    def get_transactions_by_category(self, category: str) -> pd.DataFrame:
        """Get transactions filtered by category"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT t.*, c.name as category_name, c.color as category_color
                    FROM transactions t
                    LEFT JOIN categories c ON t.category = c.name
                    WHERE t.category = ?
                    ORDER BY t.date DESC
                '''
                return pd.read_sql_query(query, conn, params=(category,))
        except Exception as e:
            print(f"Error retrieving transactions by category: {e}")
            return pd.DataFrame()
    
    def get_category_summary(self) -> pd.DataFrame:
        """Get spending summary by category"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT 
                        COALESCE(t.category, 'Uncategorized') as category,
                        COUNT(*) as transaction_count,
                        SUM(CASE WHEN t.type = 'debit' THEN ABS(t.amount) ELSE 0 END) as total_debits,
                        SUM(CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END) as total_credits,
                        SUM(t.amount) as net_amount,
                        c.color as category_color
                    FROM transactions t
                    LEFT JOIN categories c ON t.category = c.name
                    GROUP BY t.category, c.color
                    ORDER BY total_debits DESC
                '''
                return pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error retrieving category summary: {e}")
            return pd.DataFrame()
    
    def get_monthly_summary(self) -> pd.DataFrame:
        """Get monthly spending summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT 
                        strftime('%Y-%m', date) as month,
                        COUNT(*) as transaction_count,
                        SUM(CASE WHEN type = 'debit' THEN ABS(amount) ELSE 0 END) as total_debits,
                        SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) as total_credits,
                        SUM(amount) as net_amount
                    FROM transactions
                    GROUP BY strftime('%Y-%m', date)
                    ORDER BY month DESC
                '''
                return pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error retrieving monthly summary: {e}")
            return pd.DataFrame()
    
    def clear_all_transactions(self) -> bool:
        """Clear all transactions from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM transactions')
                conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing transactions: {e}")
            return False