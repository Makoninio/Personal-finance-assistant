"""
Test script for Senso integration
"""
import os
import sys
sys.path.append('backend')

from backend.senso_integration import SensoIntegration
from backend.ingestion import StatementIngestion

def test_senso_connection():
    """Test Senso API connection"""
    print("🔍 Testing Senso API connection...")
    
    # Get API key from environment or prompt user
    api_key = os.getenv('SENSO_API_KEY')
    if not api_key:
        api_key = input("Enter your Senso API key: ").strip()
    
    senso = SensoIntegration(api_key)
    
    if senso.test_connection():
        print("✅ Senso connection successful!")
        return senso
    else:
        print("❌ Senso connection failed!")
        return None

def test_pdf_upload():
    """Test PDF upload with Senso integration"""
    print("\n📄 Testing PDF upload with Senso integration...")
    
    # Get API key
    api_key = os.getenv('SENSO_API_KEY')
    if not api_key:
        api_key = input("Enter your Senso API key: ").strip()
    
    # Initialize ingestion with Senso
    ingestion = StatementIngestion(api_key)
    
    # Test with sample PDF (if exists)
    pdf_path = "data/sample_statement.pdf"  # You can replace with your PDF path
    
    if os.path.exists(pdf_path):
        print(f"Processing PDF: {pdf_path}")
        df = ingestion.parse_pdf(pdf_path, upload_to_senso=True)
        print(f"✅ Processed {len(df)} transactions")
        return df
    else:
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please place a PDF file at data/sample_statement.pdf to test")
        return None

def test_manual_upload():
    """Test manual upload to Senso"""
    print("\n📤 Testing manual upload to Senso...")
    
    # Get API key
    api_key = os.getenv('SENSO_API_KEY')
    if not api_key:
        api_key = input("Enter your Senso API key: ").strip()
    
    senso = SensoIntegration(api_key)
    
    # Test raw text upload
    raw_text = "Sample bank statement text with transactions..."
    raw_content_id = senso.upload_raw_text(
        title="Test Raw Text",
        raw_text=raw_text,
        category_id="test"
    )
    
    # Test structured data upload
    sample_transactions = [
        {
            'id': 1,
            'date': '2024-01-01',
            'amount': 100.00,
            'description': 'Test Transaction 1',
            'type': 'debit',
            'category': 'test'
        },
        {
            'id': 2,
            'date': '2024-01-02',
            'amount': -50.00,
            'description': 'Test Transaction 2',
            'type': 'credit',
            'category': 'test'
        }
    ]
    
    structured_content_id = senso.upload_structured_transactions(
        title="Test Structured Data",
        transactions=sample_transactions,
        category_id="test"
    )
    
    print(f"Raw content ID: {raw_content_id}")
    print(f"Structured content ID: {structured_content_id}")
    
    return raw_content_id, structured_content_id

if __name__ == "__main__":
    print("🚀 Senso Integration Test")
    print("=" * 50)
    
    # Test 1: Connection
    senso = test_senso_connection()
    
    if senso:
        # Test 2: Manual upload
        test_manual_upload()
        
        # Test 3: PDF upload (if PDF exists)
        test_pdf_upload()
    
    print("\n✅ Test completed!")
