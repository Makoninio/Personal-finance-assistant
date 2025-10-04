"""
Financial insights and analytics module
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import re

class FinancialInsights:
    def __init__(self, transactions_df: pd.DataFrame):
        self.df = transactions_df.copy()
        if not self.df.empty:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['month'] = self.df['date'].dt.to_period('M')
            self.df['year'] = self.df['date'].dt.year
    
    def get_net_worth_snapshot(self) -> Dict[str, float]:
        """Calculate current net worth snapshot"""
        if self.df.empty:
            return {'total_income': 0, 'total_expenses': 0, 'net_worth': 0}
        
        total_income = self.df[self.df['type'] == 'credit']['amount'].sum()
        total_expenses = abs(self.df[self.df['type'] == 'debit']['amount'].sum())
        net_worth = total_income - total_expenses
        
        return {
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'net_worth': round(net_worth, 2)
        }
    
def get_category_breakdown(self) -> pd.DataFrame:
    """Get spending breakdown by category"""
    if self.df.empty or 'category' not in self.df.columns:
        return pd.DataFrame()
    
    # Filter only debit transactions for spending analysis
    debit_df = self.df[self.df['type'] == 'debit'].copy()
    debit_df['amount'] = abs(debit_df['amount'])  # Make amounts positive for spending
    
    # Aggregate only on 'amount'
    category_summary = debit_df.groupby('category').agg({
        'amount': ['sum', 'count', 'mean'],
    }).round(2)
    
    # Flatten MultiIndex columns properly (3 names instead of 4)
    category_summary.columns = ['total_spent', 'transaction_count', 'avg_transaction']
    
    category_summary = category_summary.sort_values('total_spent', ascending=False)
    category_summary['percentage'] = (
        category_summary['total_spent'] / category_summary['total_spent'].sum() * 100
    ).round(1)
    
    return category_summary.reset_index()
    
    
    def get_monthly_trends(self) -> pd.DataFrame:
        """Get monthly spending and income trends"""
        if self.df.empty:
            return pd.DataFrame()
        
        monthly_data = self.df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        monthly_data['net'] = monthly_data.get('credit', 0) - abs(monthly_data.get('debit', 0))
        monthly_data['total_income'] = monthly_data.get('credit', 0)
        monthly_data['total_expenses'] = abs(monthly_data.get('debit', 0))
        
        return monthly_data.reset_index()
    
    def detect_recurring_subscriptions(self) -> List[Dict[str, Any]]:
        """Detect recurring subscription payments"""
        if self.df.empty:
            return []
        
        # Look for transactions that appear monthly with similar amounts
        subscriptions = []
        
        # Group by description and analyze patterns
        for desc, group in self.df.groupby('description'):
            if len(group) < 2:  # Need at least 2 occurrences
                continue
            
            # Check if amounts are similar (within 10% variance)
            amounts = group['amount'].abs()
            if amounts.std() / amounts.mean() < 0.1:  # Low variance
                # Check if transactions are roughly monthly
                dates = group['date'].sort_values()
                if len(dates) > 1:
                    intervals = dates.diff().dt.days.dropna()
                    avg_interval = intervals.mean()
                    
                    # If average interval is between 25-35 days, likely monthly
                    if 25 <= avg_interval <= 35:
                        subscriptions.append({
                            'description': desc,
                            'amount': round(amounts.mean(), 2),
                            'frequency': 'monthly',
                            'last_payment': dates.max().strftime('%Y-%m-%d'),
                            'transaction_count': len(group)
                        })
        
        return sorted(subscriptions, key=lambda x: x['amount'], reverse=True)
    
    def get_top_merchants(self, limit: int = 10) -> pd.DataFrame:
        """Get top merchants by spending"""
        if self.df.empty:
            return pd.DataFrame()
        
        # Filter debit transactions and get merchant spending
        debit_df = self.df[self.df['type'] == 'debit'].copy()
        debit_df['amount'] = abs(debit_df['amount'])
        
        merchant_summary = debit_df.groupby('description').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        merchant_summary.columns = ['total_spent', 'transaction_count', 'avg_transaction']
        merchant_summary = merchant_summary.sort_values('total_spent', ascending=False)
        
        return merchant_summary.head(limit).reset_index()
    
    def get_spending_velocity(self) -> Dict[str, float]:
        """Calculate spending velocity (daily average spending)"""
        if self.df.empty:
            return {'daily_avg': 0, 'weekly_avg': 0, 'monthly_avg': 0}
        
        # Get date range
        start_date = self.df['date'].min()
        end_date = self.df['date'].max()
        days = (end_date - start_date).days + 1
        
        # Calculate total spending
        total_spending = abs(self.df[self.df['type'] == 'debit']['amount'].sum())
        
        daily_avg = total_spending / days if days > 0 else 0
        weekly_avg = daily_avg * 7
        monthly_avg = daily_avg * 30
        
        return {
            'daily_avg': round(daily_avg, 2),
            'weekly_avg': round(weekly_avg, 2),
            'monthly_avg': round(monthly_avg, 2)
        }
    
    def get_financial_health_score(self) -> Dict[str, Any]:
        """Calculate a simple financial health score"""
        if self.df.empty:
            return {'score': 0, 'factors': []}
        
        factors = []
        score = 0
        
        # Net worth factor (40% of score)
        net_worth = self.get_net_worth_snapshot()
        if net_worth['net_worth'] > 0:
            score += 40
            factors.append("Positive net worth")
        elif net_worth['net_worth'] > -1000:
            score += 20
            factors.append("Slightly negative net worth")
        else:
            factors.append("Significantly negative net worth")
        
        # Income vs expenses ratio (30% of score)
        if net_worth['total_income'] > 0:
            expense_ratio = net_worth['total_expenses'] / net_worth['total_income']
            if expense_ratio < 0.7:
                score += 30
                factors.append("Low expense ratio")
            elif expense_ratio < 0.9:
                score += 20
                factors.append("Moderate expense ratio")
            else:
                factors.append("High expense ratio")
        
        # Spending consistency (20% of score)
        velocity = self.get_spending_velocity()
        if velocity['daily_avg'] < 50:
            score += 20
            factors.append("Low daily spending")
        elif velocity['daily_avg'] < 100:
            score += 10
            factors.append("Moderate daily spending")
        else:
            factors.append("High daily spending")
        
        # Subscription management (10% of score)
        subscriptions = self.detect_recurring_subscriptions()
        if len(subscriptions) <= 3:
            score += 10
            factors.append("Few subscriptions")
        elif len(subscriptions) <= 6:
            score += 5
            factors.append("Moderate subscriptions")
        else:
            factors.append("Many subscriptions")
        
        return {
            'score': min(score, 100),
            'factors': factors,
            'subscription_count': len(subscriptions)
        }
    
    def get_budget_recommendations(self) -> List[str]:
        """Generate budget recommendations based on spending patterns"""
        recommendations = []
        
        if self.df.empty:
            return ["No data available for recommendations"]
        
        category_breakdown = self.get_category_breakdown()
        if category_breakdown.empty:
            return ["No categorized transactions for recommendations"]
        
        # Check for high spending categories
        for _, row in category_breakdown.iterrows():
            if row['percentage'] > 30:
                recommendations.append(
                    f"Consider reducing spending in {row['category']} "
                    f"({row['percentage']:.1f}% of total expenses)"
                )
        
        # Check for many small transactions
        top_merchants = self.get_top_merchants(5)
        if not top_merchants.empty:
            avg_transaction = top_merchants['avg_transaction'].mean()
            if avg_transaction < 10:
                recommendations.append(
                    "Consider consolidating small purchases to reduce transaction fees"
                )
        
        # Check subscription count
        subscriptions = self.detect_recurring_subscriptions()
        if len(subscriptions) > 5:
            recommendations.append(
                f"Review {len(subscriptions)} recurring subscriptions - "
                "consider canceling unused services"
            )
        
        if not recommendations:
            recommendations.append("Your spending patterns look healthy!")
        
        return recommendations