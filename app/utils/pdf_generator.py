import os
from pathlib import Path
from datetime import datetime
import jinja2
from weasyprint import HTML
from app.utils.models import QuotationData
from app.config.settings import (
    TEMPLATES_DIR, 
    TEMP_DIR, 
    COMPANY_NAME, 
    COMPANY_ADDRESS, 
    COMPANY_PHONE, 
    COMPANY_EMAIL, 
    COMPANY_WEBSITE,
    COMPANY_LOGO_PATH,
    CURRENCY_SYMBOL,
    SAVE_TO_STORAGE,
    STORAGE_PATH
)


class PDFGenerator:
    """Class to handle PDF generation from quotation data."""
    
    def __init__(self):
        """Initialize the PDF generator with Jinja2 environment."""
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Create temp directory if it doesn't exist
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        # Create storage directory if enabled
        if SAVE_TO_STORAGE:
            os.makedirs(STORAGE_PATH, exist_ok=True)
    
    def _get_template_context(self, quotation_data: QuotationData) -> dict:
        """Prepare the context data for the template."""
        return {
            # Company details
            'company_name': COMPANY_NAME,
            'company_address': COMPANY_ADDRESS,
            'company_phone': COMPANY_PHONE,
            'company_email': COMPANY_EMAIL,
            'company_website': COMPANY_WEBSITE,
            'company_logo': COMPANY_LOGO_PATH if COMPANY_LOGO_PATH else None,
            
            # Quotation details
            'quotation_number': quotation_data.quotation_number,
            'quotation_date': quotation_data.created_date,
            'customer_name': quotation_data.customer_name,
            'items': quotation_data.items,
            'notes': quotation_data.notes,
            
            # Calculations
            'subtotal': quotation_data.subtotal,
            'currency': CURRENCY_SYMBOL,
            
            # Utility for template
            'format_currency': lambda value: f"{CURRENCY_SYMBOL}{value:,.2f}"
        }
    
    def generate_pdf(self, quotation_data: QuotationData) -> Path:
        """Generate a PDF from the quotation data and return the file path."""
        # Get the template
        template = self.env.get_template("quotation_template.html")
        
        # Render the template with context data
        context = self._get_template_context(quotation_data)
        html_content = template.render(**context)
        
        # Define the output path
        pdf_filename = quotation_data.filename
        pdf_path = TEMP_DIR / pdf_filename
        
        # Generate PDF from HTML
        HTML(string=html_content).write_pdf(pdf_path)
        
        # Optionally save to storage
        if SAVE_TO_STORAGE:
            storage_file_path = Path(STORAGE_PATH) / pdf_filename
            with open(pdf_path, 'rb') as src_file:
                with open(storage_file_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
        
        return pdf_path
