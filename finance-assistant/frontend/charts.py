"""
Chart utilities for the Streamlit frontend
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any

class ChartGenerator:
    def __init__(self):
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
    
    def create_category_pie_chart(self, category_data: pd.DataFrame) -> go.Figure:
        """Create pie chart for category breakdown"""
        if category_data.empty:
            return go.Figure()
        
        fig = px.pie(
            category_data,
            values='total_spent',
            names='category',
            title="Spending by Category",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            font=dict(size=12),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    def create_monthly_trend_chart(self, monthly_data: pd.DataFrame) -> go.Figure:
        """Create line chart for monthly trends"""
        if monthly_data.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Add income line
        fig.add_trace(go.Scatter(
            x=monthly_data['month'].astype(str),
            y=monthly_data['total_income'],
            mode='lines+markers',
            name='Income',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=8)
        ))
        
        # Add expenses line
        fig.add_trace(go.Scatter(
            x=monthly_data['month'].astype(str),
            y=monthly_data['total_expenses'],
            mode='lines+markers',
            name='Expenses',
            line=dict(color='#DC143C', width=3),
            marker=dict(size=8)
        ))
        
        # Add net worth line
        fig.add_trace(go.Scatter(
            x=monthly_data['month'].astype(str),
            y=monthly_data['net'],
            mode='lines+markers',
            name='Net Worth',
            line=dict(color='#4169E1', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Monthly Financial Trends",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            hovermode='x unified',
            font=dict(size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_spending_bar_chart(self, category_data: pd.DataFrame) -> go.Figure:
        """Create horizontal bar chart for spending by category"""
        if category_data.empty:
            return go.Figure()
        
        fig = px.bar(
            category_data,
            x='total_spent',
            y='category',
            orientation='h',
            title="Spending by Category",
            color='total_spent',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Amount ($)",
            yaxis_title="Category",
            font=dict(size=12),
            height=400
        )
        
        return fig
    
    def create_daily_spending_chart(self, transactions_df: pd.DataFrame) -> go.Figure:
        """Create daily spending trend chart"""
        if transactions_df.empty:
            return go.Figure()
        
        # Filter debit transactions and group by date
        daily_spending = transactions_df[transactions_df['type'] == 'debit'].copy()
        daily_spending['amount'] = abs(daily_spending['amount'])
        daily_spending = daily_spending.groupby('date')['amount'].sum().reset_index()
        
        fig = px.line(
            daily_spending,
            x='date',
            y='amount',
            title="Daily Spending Trend",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            font=dict(size=12)
        )
        
        return fig
    
    def create_income_vs_expenses_chart(self, monthly_data: pd.DataFrame) -> go.Figure:
        """Create stacked bar chart for income vs expenses"""
        if monthly_data.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Add income bars
        fig.add_trace(go.Bar(
            name='Income',
            x=monthly_data['month'].astype(str),
            y=monthly_data['total_income'],
            marker_color='#2E8B57'
        ))
        
        # Add expenses bars (negative for visual effect)
        fig.add_trace(go.Bar(
            name='Expenses',
            x=monthly_data['month'].astype(str),
            y=-monthly_data['total_expenses'],
            marker_color='#DC143C'
        ))
        
        fig.update_layout(
            title="Monthly Income vs Expenses",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            barmode='group',
            font=dict(size=12)
        )
        
        return fig
    
    def create_financial_health_gauge(self, health_score: int) -> go.Figure:
        """Create gauge chart for financial health score"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Financial Health Score"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(font={'color': "darkblue", 'family': "Arial"})
        return fig
    
    def create_subscription_timeline(self, subscriptions: List[Dict]) -> go.Figure:
        """Create timeline chart for recurring subscriptions"""
        if not subscriptions:
            return go.Figure()
        
        # Create timeline data
        timeline_data = []
        for i, sub in enumerate(subscriptions):
            timeline_data.append({
                'subscription': sub['description'],
                'amount': sub['amount'],
                'frequency': sub['frequency'],
                'y_position': i
            })
        
        df = pd.DataFrame(timeline_data)
        
        fig = px.scatter(
            df,
            x='amount',
            y='subscription',
            size='amount',
            color='frequency',
            title="Recurring Subscriptions",
            hover_data=['frequency']
        )
        
        fig.update_layout(
            xaxis_title="Monthly Amount ($)",
            yaxis_title="Subscription",
            font=dict(size=12)
        )
        
        return fig
    
    def create_category_trend_chart(self, transactions_df: pd.DataFrame) -> go.Figure:
        """Create trend chart for spending by category over time"""
        if transactions_df.empty or 'category' not in transactions_df.columns:
            return go.Figure()
        
        # Prepare data
        monthly_category = transactions_df[transactions_df['type'] == 'debit'].copy()
        monthly_category['amount'] = abs(monthly_category['amount'])
        monthly_category['month'] = monthly_category['date'].dt.to_period('M')
        
        monthly_spending = monthly_category.groupby(['month', 'category'])['amount'].sum().reset_index()
        
        # Get top 5 categories
        top_categories = monthly_spending.groupby('category')['amount'].sum().nlargest(5).index
        
        fig = go.Figure()
        
        for category in top_categories:
            category_data = monthly_spending[monthly_spending['category'] == category]
            fig.add_trace(go.Scatter(
                x=category_data['month'].astype(str),
                y=category_data['amount'],
                mode='lines+markers',
                name=category,
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title="Top Categories - Monthly Spending Trend",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            hovermode='x unified',
            font=dict(size=12)
        )
        
        return fig