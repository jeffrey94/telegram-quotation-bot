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
from app.config.settings import (
    TEMP_DIR,
    TEMPLATES_DIR,
    COMPANY_NAME,
    COMPANY_REG_NO,
    COMPANY_ADDRESS,
    COMPANY_PHONE,
    COMPANY_FAX,
    COMPANY_EMAIL,
    FACTORY_ADDRESS,
    FACTORY_PHONE,
    FACTORY_FAX,
    CURRENCY_SYMBOL
)

# Add the project root to the Python path if running this script directly
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

def format_currency(amount: float) -> str:
    return f"{CURRENCY_SYMBOL}{amount:,.2f}"

def create_sample_quotation() -> QuotationData:
    """Create a sample quotation for testing."""
    items = [
        QuotationItem(
            item_name="Interior Design Consultation",
            quantity=1,
            unit_price=2500.00
        ),
        QuotationItem(
            item_name="3D Visualization - Living Room",
            quantity=2,
            unit_price=1800.00
        ),
        QuotationItem(
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
        quotation_number=quotation.quotation_number,
        created_date=quotation.created_date.strftime('%d %b %Y'),
        expiry_date=quotation.expiry_date.strftime('%d %b %Y'),
        customer_name=quotation.customer_name,
        customer_company=quotation.customer_company,
        customer_address=quotation.customer_address,
        customer_phone=quotation.customer_phone,
        customer_email=quotation.customer_email,
        items=quotation.items,
        subtotal=quotation.subtotal,
        discount=quotation.discount,
        grand_total=quotation.grand_total,
        terms=quotation.terms,
        notes=quotation.notes,
        issued_by=quotation.issued_by,
        company_name=quotation.company_name,
        company_reg_no=quotation.company_reg_no,
        company_address=quotation.company_address,
        company_phone=quotation.company_phone,
        company_fax=quotation.company_fax,
        company_email=quotation.company_email,
        factory_address=quotation.factory_address,
        factory_phone=quotation.factory_phone,
        factory_fax=quotation.factory_fax,
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

    except Exception as e:
        print(f"Error generating quotation: {e}")

if __name__ == '__main__':
    main()
