from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import random
from app.config.settings import (
    COMPANY_NAME, COMPANY_REG_NO, COMPANY_ADDRESS, COMPANY_PHONE,
    COMPANY_FAX, COMPANY_EMAIL, FACTORY_ADDRESS, FACTORY_PHONE,
    FACTORY_FAX, CURRENCY_SYMBOL
)


class QuotationItem(BaseModel):
    """Model for a single line item in a quotation."""
    item_name: str
    quantity: int
    unit_price: float
    
    @property
    def total_price(self) -> float:
        """Calculate the total price for this line item."""
        return self.quantity * self.unit_price
    
    @field_validator('quantity', 'unit_price')
    def validate_positive_number(cls, v):
        if v <= 0:
            raise ValueError("Value must be greater than zero")
        return v


class QuotationData(BaseModel):
    """Model for the complete quotation data."""
    # Customer Details
    customer_name: str
    customer_company: str
    customer_address: str
    customer_phone: str
    customer_email: str

    # Quotation Details
    quotation_number: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    issued_by: str
    terms: str
    notes: Optional[str] = None
    items: List[QuotationItem]
    discount: float = 0

    # Company Details (from settings)
    company_name: str = COMPANY_NAME
    company_reg_no: str = COMPANY_REG_NO
    company_address: str = COMPANY_ADDRESS
    company_phone: str = COMPANY_PHONE
    company_fax: str = COMPANY_FAX
    company_email: str = COMPANY_EMAIL
    factory_address: str = FACTORY_ADDRESS
    factory_phone: str = FACTORY_PHONE
    factory_fax: str = FACTORY_FAX

    @field_validator('customer_name')
    def validate_customer_name(cls, v):
        if not v:
            raise ValueError('Customer name cannot be empty')
        return v
    
    @field_validator('quotation_number')
    def generate_quotation_number(cls, v):
        if not v:
            random_number = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            return f"QUO-{random_number}"
        return v

    def model_post_init(self, __context):
        super().model_post_init(__context)
        if self.expiry_date is None:
            self.expiry_date = self.created_date + timedelta(days=14)
        if self.quotation_number is None:
            random_number = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            self.quotation_number = f"QUO-{random_number}"

    @property
    def formatted_created_date(self) -> str:
        """Get the formatted creation date."""
        return self.created_date.strftime(DATE_FORMAT)
    
    @property
    def formatted_expiry_date(self) -> str:
        """Get the formatted expiry date."""
        return self.expiry_date.strftime(DATE_FORMAT)
    
    @property
    def subtotal(self) -> float:
        """Calculate the subtotal of all items."""
        return sum(item.total_price for item in self.items)
    
    @property
    def grand_total(self) -> float:
        """Calculate the grand total after discount."""
        return self.subtotal - self.discount
    
    @property
    def filename(self) -> str:
        """Generate a filename for the quotation PDF."""
        date_str = self.created_date.strftime('%Y-%m-%d')
        return f"{self.customer_company.replace(' ', '_')}_Quotation_{date_str}"
