"""
Test script for the quotation generator.

This script creates a sample quotation and generates HTML for testing.
The generated HTML can be opened in a browser and saved/printed as PDF if needed.
Run this script directly from the project root to test the generation:
    python -m app.utils.test_pdf
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import jinja2
from app.utils.models import QuotationData, QuotationItem
from app.config import Config

# Add the project root to the Python path if running this script directly
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Define constants for backward compatibility
TEMP_DIR = Path(Config.STORAGE_PATH)
TEMPLATES_DIR = Path(__file__).parent.parent / 'templates'

def format_currency(amount: float) -> str:
    """Format currency values with 2 decimal places."""
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0.0
    return f"${amount:.2f}"

def create_sample_quotation() -> QuotationData:
    """Create a sample quotation for testing."""
    items = [
        QuotationItem(
            item_no="001",
            item_name="Interior Design Consultation",
            quantity=1,
            unit_price=2500.00
        ),
        QuotationItem(
            item_no="002",
            item_name="3D Visualization - Living Room",
            quantity=2,
            unit_price=1800.00
        ),
        QuotationItem(
            item_no="003",
            item_name="Detailed Construction Drawing",
            quantity=1,
            unit_price=3500.00
        )
    ]
    
    return QuotationData(
        # Customer details
        customer_name="Mr. Ahmad bin Abdullah",  # Contact person name
        customer_company="Modern Living Sdn. Bhd.",  # Company name
        customer_address="123 Jalan Maju,\nTaman Modern,\n81300 Johor Bahru, Johor",
        customer_phone="012-345 6789",
        customer_email="ahmad@modernliving.com.my",
        
        # Quotation details
        items=items,
        terms="1. 50% deposit upon confirmation\n2. Balance payment upon completion\n3. Delivery within 4 weeks",
        issued_by="John Doe",
        discount=500.00,
        notes="Please contact us if you have any questions."
    )

def generate_quotation_html(quotation: QuotationData) -> str:
    """Generate HTML content for the quotation."""
    # Defensive check to ensure we receive a QuotationData object
    if not isinstance(quotation, QuotationData):
        raise TypeError(f"Expected QuotationData object, got {type(quotation).__name__}")
    
    # Ensure all numeric values are proper floats
    subtotal = float(quotation.subtotal)
    discount = float(quotation.discount)
    grand_total = float(quotation.grand_total)
    
    # Set up Jinja2 environment with autoescape enabled for security
    template_dir = Path(__file__).parent.parent / 'templates'
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    env.filters['format_currency'] = format_currency

    # Get the template
    template = env.get_template('quotation_template.html')

    # Render the template with escaped variables
    html = template.render(
        env=Config.get_company_info(),
        quotation_number=quotation.quotation_number,
        quotation_date=quotation.formatted_created_date,
        expiry_date=quotation.formatted_expiry_date,
        client_company=quotation.customer_company,
        client_address=quotation.customer_address,
        client_contact=quotation.customer_name,
        client_phone=quotation.customer_phone,
        client_email=quotation.customer_email,
        items=quotation.items,
        subtotal=subtotal,
        discount=discount,
        total_quoted_amount=grand_total,
        terms_and_conditions=quotation.terms.split('\n') if quotation.terms and '\n' in quotation.terms else ([quotation.terms] if quotation.terms else ["Payment terms not specified"]),
        notes=quotation.notes,
        issued_by=quotation.issued_by,
        format_currency=format_currency
    )

    return html

def main():
    try:
        # Create a sample quotation
        quotation = create_sample_quotation()

        # Generate the HTML with proper escaping
        html = generate_quotation_html(quotation)

        # Create output directory if it doesn't exist
        output_dir = Path(__file__).parent.parent.parent / 'temp'
        output_dir.mkdir(exist_ok=True)

        # Save HTML file with proper encoding
        html_file = output_dir / f"{quotation.filename}.html"
        html_file.write_text(html, encoding='utf-8')
        print(f"HTML file saved at: {html_file}")
        print("You can open this HTML file in your browser and use the browser's built-in 'Save as PDF' or 'Print to PDF' feature.")
        
        # Open the file in the default browser - properly handling paths with spaces
        try:
            if sys.platform == 'win32':
                import subprocess
                subprocess.Popen(['start', '', str(html_file)], shell=True)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{html_file}"')
            else:  # Linux
                os.system(f'xdg-open "{html_file}"')
        except Exception as browser_error:
            print(f"Note: Could not automatically open the file in browser: {browser_error}")
            print(f"Please open the file manually at: {html_file}")

    except Exception as e:
        print(f"Error generating quotation: {e}")

if __name__ == '__main__':
    main()
