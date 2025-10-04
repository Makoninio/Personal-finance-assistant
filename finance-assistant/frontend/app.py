"""
Streamlit frontend for Personal Finance AI Assistant
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ingestion import StatementIngestion
from categorize import TransactionCategorizer
from insights import FinancialInsights
from explain import TransactionExplainer
from translate import FinancialTranslator
from db import TransactionDB

# Page configuration
st.set_page_config(
    page_title="Personal Finance AI Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'transactions_df' not in st.session_state:
    st.session_state.transactions_df = pd.DataFrame()
if 'db' not in st.session_state:
    st.session_state.db = TransactionDB()
if 'categorizer' not in st.session_state:
    st.session_state.categorizer = TransactionCategorizer()
if 'explainer' not in st.session_state:
    st.session_state.explainer = TransactionExplainer()
if 'translator' not in st.session_state:
    st.session_state.translator = FinancialTranslator()

def main():
    st.title("💰 Personal Finance AI Assistant")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["📈 Dashboard", "📄 Upload Data", "🔍 Explain Transaction", "🌍 Multilingual Reports", "⚙️ Settings"]
        )
        
        st.markdown("---")
        st.header("💡 Quick Actions")
        
        if st.button("🗑️ Clear All Data"):
            clear_all_data()
    
    # Main content area
    if page == "📈 Dashboard":
        show_dashboard()
    elif page == "📄 Upload Data":
        show_upload_page()
    elif page == "🔍 Explain Transaction":
        show_explain_page()
    elif page == "🌍 Multilingual Reports":
        show_translation_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def clear_all_data():
    """Clear all transaction data"""
    if st.session_state.db.clear_all_transactions():
        st.session_state.transactions_df = pd.DataFrame()
        st.success("All data cleared!")
        st.rerun()
    else:
        st.error("Failed to clear data")

def show_dashboard():
    """Display the main dashboard"""
    if st.session_state.transactions_df.empty:
        st.info("No transaction data available. Please upload data or load sample data.")
        return
    
    # Get insights
    insights = FinancialInsights(st.session_state.transactions_df)
    
    # Key metrics
    st.header("📊 Financial Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    net_worth = insights.get_net_worth_snapshot()
    
    with col1:
        st.metric("Total Income", f"${net_worth['total_income']:,.2f}")
    
    with col2:
        st.metric("Total Expenses", f"${net_worth['total_expenses']:,.2f}")
    
    with col3:
        st.metric("Net Worth", f"${net_worth['net_worth']:,.2f}")
    
    with col4:
        velocity = insights.get_spending_velocity()
        st.metric("Daily Avg Spending", f"${velocity['daily_avg']:,.2f}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Spending by Category")
        category_breakdown = insights.get_category_breakdown()
        
        if not category_breakdown.empty:
            fig = px.pie(
                category_breakdown, 
                values='total_spent', 
                names='category',
                title="Category Breakdown"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorized transactions available")
    
    with col2:
        st.subheader("📈 Monthly Trends")
        monthly_trends = insights.get_monthly_trends()
        
        if not monthly_trends.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly_trends['month'].astype(str),
                y=monthly_trends['total_income'],
                mode='lines+markers',
                name='Income',
                line=dict(color='green')
            ))
            fig.add_trace(go.Scatter(
                x=monthly_trends['month'].astype(str),
                y=monthly_trends['total_expenses'],
                mode='lines+markers',
                name='Expenses',
                line=dict(color='red')
            ))
            fig.update_layout(
                title="Monthly Income vs Expenses",
                xaxis_title="Month",
                yaxis_title="Amount ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available")
    
    # Financial Health Score
    st.subheader("💚 Financial Health Score")
    health_score = insights.get_financial_health_score()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Health Score", f"{health_score['score']}/100")
    
    with col2:
        st.write("**Factors:**")
        for factor in health_score['factors']:
            st.write(f"• {factor}")
    
    # Recommendations
    st.subheader("💡 Budget Recommendations")
    recommendations = insights.get_budget_recommendations()
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Recurring Subscriptions
    st.subheader("🔄 Recurring Subscriptions")
    subscriptions = insights.detect_recurring_subscriptions()
    
    if subscriptions:
        sub_df = pd.DataFrame(subscriptions)
        st.dataframe(sub_df, use_container_width=True)
    else:
        st.info("No recurring subscriptions detected")
    
    # Transaction Table
    st.subheader("📋 Recent Transactions")
    recent_transactions = st.session_state.transactions_df.head(20)
    st.dataframe(recent_transactions, use_container_width=True)

def show_upload_page():
    """Show data upload page"""
    st.header("📄 Upload Bank Statement")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'csv'],
        help="Upload a bank statement PDF or CSV file"
    )
    
    if uploaded_file is not None:
        # Process file
        ingestion = StatementIngestion()
        
        if uploaded_file.type == "application/pdf":
            # Save uploaded PDF temporarily
            with open("temp_upload.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Parse PDF
            with st.spinner("Parsing PDF..."):
                df = ingestion.parse_pdf("temp_upload.pdf")
            
            # Clean up temp file
            os.remove("temp_upload.pdf")
        
        elif uploaded_file.type == "text/csv":
            # Save uploaded CSV temporarily
            with open("temp_upload.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Parse CSV
            with st.spinner("Parsing CSV..."):
                df = ingestion.parse_csv("temp_upload.csv")
            
            # Clean up temp file
            os.remove("temp_upload.csv")
        
        if not df.empty:
            st.success(f"Successfully parsed {len(df)} transactions!")
            
            # Show preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10))
            
            # Show column info
            st.subheader("📊 Column Information")
            st.write(f"Columns found: {list(df.columns)}")
            st.write(f"Data types: {df.dtypes.to_dict()}")
            
            # Categorize transactions
            if st.button("🤖 Categorize Transactions"):
                with st.spinner("Categorizing transactions..."):
                    categorized_df = st.session_state.categorizer.categorize_batch(df)
                    
                    # Store in database
                    st.session_state.db.insert_transactions(categorized_df)
                    
                    # Update session state
                    st.session_state.transactions_df = categorized_df
                    
                    st.success("Transactions categorized and stored!")
                    st.rerun()
        else:
            st.error("Failed to parse file. Please check the format.")
            st.info("""
            **Supported formats:**
            - **PDF**: Bank statement PDFs with transaction data
            - **CSV**: Transaction files with columns like date, amount, description
            
            **CSV format should have columns:**
            - date (or Date)
            - amount (or Amount) 
            - description (or Description)
            - type (or Type) - optional
            """)

def show_explain_page():
    """Show transaction explanation page"""
    st.header("🔍 Explain Transaction")
    
    if st.session_state.transactions_df.empty:
        st.info("No transaction data available. Please upload data first.")
        return
    
    # Transaction selector
    st.subheader("Select a Transaction")
    
    # Create a selectbox with transaction descriptions
    transaction_options = []
    for idx, row in st.session_state.transactions_df.iterrows():
        option = f"{row['date'].strftime('%Y-%m-%d')} - {row['description']} - ${row['amount']:.2f}"
        transaction_options.append((option, idx))
    
    selected_option = st.selectbox(
        "Choose a transaction:",
        options=[opt[0] for opt in transaction_options],
        index=0
    )
    
    if selected_option:
        # Get selected transaction
        selected_idx = next(opt[1] for opt in transaction_options if opt[0] == selected_option)
        transaction = st.session_state.transactions_df.iloc[selected_idx]
        
        # Display transaction details
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Date", transaction['date'].strftime('%Y-%m-%d'))
        
        with col2:
            st.metric("Amount", f"${transaction['amount']:.2f}")
        
        with col3:
            st.metric("Type", transaction['type'].title())
        
        with col4:
            st.metric("Category", transaction.get('category', 'Uncategorized'))
        
        # Get AI explanations
        if st.button("🤖 Get AI Explanation"):
            with st.spinner("Getting AI explanation..."):
                explanations = st.session_state.explainer.explain_transaction(
                    transaction['description'],
                    transaction['amount'],
                    transaction.get('category')
                )
                
                # Display explanations
                for service, explanation in explanations.items():
                    st.subheader(f"Explanation ({service.title()}):")
                    st.write(explanation)
                
                # Get merchant context
                st.subheader("🏪 Merchant Context")
                context = st.session_state.explainer.get_merchant_context(transaction['description'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Type:** {context['type']}")
                with col2:
                    st.write(f"**Website:** {context['website']}")
                with col3:
                    st.write(f"**Description:** {context['description']}")
                
                # Budget suggestions
                st.subheader("💡 Budget Suggestions")
                suggestions = st.session_state.explainer.suggest_budget_adjustments(
                    transaction['description'],
                    transaction['amount'],
                    transaction.get('category', 'Other')
                )
                
                if suggestions:
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
                else:
                    st.write("No specific suggestions for this transaction.")

def show_translation_page():
    """Show multilingual reports page"""
    st.header("🌍 Multilingual Reports")
    
    if st.session_state.transactions_df.empty:
        st.info("No transaction data available. Please upload data first.")
        return
    
    # Language selection
    st.subheader("Select Language")
    
    translator = st.session_state.translator
    supported_langs = translator.get_supported_languages()
    
    selected_lang = st.selectbox(
        "Choose target language:",
        options=list(supported_langs.keys()),
        format_func=lambda x: f"{supported_langs[x]} ({x.upper()})"
    )
    
    if st.button("🌍 Translate Report"):
        with st.spinner("Translating report..."):
            # Get financial summary
            insights = FinancialInsights(st.session_state.transactions_df)
            net_worth = insights.get_net_worth_snapshot()
            category_breakdown = insights.get_category_breakdown()
            
            # Translate summary
            translated_summary = translator.translate_financial_summary(net_worth, selected_lang)
            
            # Display translated summary
            st.subheader(f"📊 Financial Summary ({supported_langs[selected_lang]})")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Income", f"${net_worth['total_income']:,.2f}")
                st.write(translated_summary.get('total_income', ''))
            
            with col2:
                st.metric("Total Expenses", f"${net_worth['total_expenses']:,.2f}")
                st.write(translated_summary.get('total_expenses', ''))
            
            with col3:
                st.metric("Net Worth", f"${net_worth['net_worth']:,.2f}")
                st.write(translated_summary.get('net_worth', ''))
            
            # Translate category breakdown
            if not category_breakdown.empty:
                st.subheader(f"📊 Category Breakdown ({supported_langs[selected_lang]})")
                
                translated_categories = translator.translate_category_names(
                    category_breakdown['category'].tolist(),
                    selected_lang
                )
                
                # Create translated dataframe
                translated_df = category_breakdown.copy()
                translated_df['category_translated'] = translated_df['category'].map(translated_categories)
                
                st.dataframe(translated_df[['category_translated', 'total_spent', 'percentage']], 
                           use_container_width=True)
            
            # Translate insights
            st.subheader(f"💡 Insights ({supported_langs[selected_lang]})")
            recommendations = insights.get_budget_recommendations()
            translated_insights = translator.translate_insights(recommendations, selected_lang)
            
            for i, insight in enumerate(translated_insights, 1):
                st.write(f"{i}. {insight}")

def show_settings_page():
    """Show settings page"""
    st.header("⚙️ Settings")
    
    st.subheader("🔑 API Keys")
    st.write("Configure API keys for enhanced features:")
    
    with st.expander("OpenAI API Key"):
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Required for AI-powered categorization and explanations"
        )
        if openai_key:
            st.success("OpenAI API key configured!")
    
    with st.expander("Perplexity API Key"):
        perplexity_key = st.text_input(
            "Perplexity API Key",
            type="password",
            help="Required for enhanced transaction explanations"
        )
        if perplexity_key:
            st.success("Perplexity API key configured!")
    
    with st.expander("DeepL API Key"):
        deepl_key = st.text_input(
            "DeepL API Key",
            type="password",
            help="Required for multilingual translations"
        )
        if deepl_key:
            st.success("DeepL API key configured!")
    
    st.subheader("📊 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Data"):
            if not st.session_state.transactions_df.empty:
                csv = st.session_state.transactions_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data to export")
    
    with col2:
        if st.button("🗑️ Clear All Data"):
            if st.session_state.db.clear_all_transactions():
                st.session_state.transactions_df = pd.DataFrame()
                st.success("All data cleared!")
                st.rerun()
            else:
                st.error("Failed to clear data")
    
    st.subheader("ℹ️ About")
    st.write("""
    **Personal Finance AI Assistant** v1.0
    
    This application helps you:
    - 📄 Parse bank statements (PDF/CSV)
    - 🤖 Categorize transactions with AI
    - 📊 Generate financial insights
    - 🔍 Explain transactions
    - 🌍 Create multilingual reports
    
    Built for hackathon demo in under 5 hours!
    """)

if __name__ == "__main__":
    main()