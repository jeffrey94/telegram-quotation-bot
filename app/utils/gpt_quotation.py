"""
GPT-powered quotation data extraction and validation.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from openai import AsyncOpenAI  # Use AsyncOpenAI instead of OpenAI
from app.config import Config
from app.utils.models import QuotationItem

logger = logging.getLogger(__name__)

class GPTQuotationParser:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"  # Using a more widely available model
        
    async def extract_quotation_data(self, text: str) -> Tuple[Dict, List[str]]:
        """
        Extract structured quotation data from freeform text.
        Returns a tuple of (extracted_data, missing_fields).
        """
        prompt = f"""Extract quotation data from the following text. 
        If the text has both "Previous information" and "Additional information" sections, merge them intelligently.
        
        Return a JSON object with these fields:
        - customer_name: Customer's full name
        - customer_company: Company name
        - customer_address: Full address
        - customer_phone: Phone number
        - customer_email: Email address
        - items: List of items, each with name, quantity, and unit_price
        - terms: Payment terms and conditions
        - discount: Discount percentage (if any)
        - issued_by: Name of person issuing the quote

        If a field value is "No" or "None" or similar negative, convert it to empty string or appropriate null value.
        For missing/unclear fields, use null or empty values.

        Text to analyze:
        {text}

        If any required field is missing or unclear, include it in the missing_fields list.
        Required fields are: customer_name, customer_company, customer_address, customer_phone, customer_email, items, terms

        Format the response as:
        {{
            "data": {{...}},
            "missing_fields": ["field1", "field2", ...]
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a quotation data extraction assistant. Extract structured data from freeform text. Be thorough and look for all required information, even if it's in different sections or formats."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent output
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON string into a Python dictionary
            content = response.choices[0].message.content
            logger.info(f"GPT response: {content}")
            
            result = json.loads(content)
            
            # Process the data to handle common issues
            data = result.get("data", {})
            
            # Handle "no discount" or "none" values consistently
            if "discount" in data:
                if isinstance(data["discount"], str) and data["discount"].lower() in ["no", "none", "no discount", "0", "not provided"]:
                    data["discount"] = 0
            
            # Handle "no notes" or "none" values consistently  
            if "notes" in data:
                if isinstance(data["notes"], str) and data["notes"].lower() in ["no", "none", "no notes", "not provided"]:
                    data["notes"] = ""
            
            # Make sure items is always a list
            if "items" in data and not isinstance(data["items"], list):
                data["items"] = []
            
            # Make sure missing_fields doesn't include fields that have valid data
            missing_fields = result.get("missing_fields", [])
            cleaned_missing_fields = []
            for field in missing_fields:
                if field not in data or not data[field]:
                    cleaned_missing_fields.append(field)
                    
            return data, cleaned_missing_fields
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}, Content: {content if 'content' in locals() else 'No content'}")
            return {}, ["Error: Invalid JSON response"]
        except Exception as e:
            logger.error(f"Error in GPT extraction: {e}")
            return {}, ["Error processing text"]

    async def validate_quotation_data(self, data: Dict) -> List[str]:
        """
        Validate the extracted quotation data for completeness and format.
        Also normalizes values where possible.
        Returns a list of validation issues.
        """
        issues = []
        modified_data = data.copy()
        
        # Required fields
        required_fields = [
            "customer_name", "customer_company", "customer_address",
            "customer_phone", "customer_email", "items", "terms"
        ]
        
        # Check for missing fields
        for field in required_fields:
            if not data.get(field):
                if field != "items":  # Items need special handling
                    if data.get(field, "").lower() in ["n/a", "na", "not applicable"]:
                        # Accept "N/A" as valid for required text fields
                        if field not in modified_data or not modified_data[field]:
                            modified_data[field] = "N/A"
                    else:
                        issues.append(f"Missing required field: {field}")
        
        # Normalize fields
        if "discount" in data:
            try:
                if isinstance(data["discount"], str):
                    # Remove any non-numeric characters except decimal point
                    discount_str = data["discount"].strip()
                    if discount_str.lower() in ["no", "none", "no discount", "0", "", "not provided", "n/a", "na"]:
                        modified_data["discount"] = 0
                    else:
                        # Try to extract numeric value, removing currency symbols and %
                        import re
                        numeric_part = re.sub(r'[^0-9.]', '', discount_str)
                        if numeric_part:
                            modified_data["discount"] = float(numeric_part)
                        else:
                            modified_data["discount"] = 0
            except (ValueError, TypeError):
                issues.append(f"Invalid discount format, please provide a numeric value")
                modified_data["discount"] = 0
        
        # Process "issued_by" field
        if "issued_by" in data:
            if not data["issued_by"] or data["issued_by"].lower() in ["n/a", "na", "not applicable", "none"]:
                modified_data["issued_by"] = "N/A"
        
        # Validate and normalize items
        if "items" in data and data["items"]:
            normalized_items = []
            for i, item in enumerate(data["items"]):
                normalized_item = item.copy()
                
                # Ensure required item fields exist
                if not all(k in item for k in ["name", "quantity", "unit_price"]):
                    issues.append(f"Item {i+1} is missing required fields (name, quantity, or price)")
                    continue
                
                # Handle N/A in item name
                if not item.get("name") or item.get("name", "").lower() in ["n/a", "na", "not applicable"]:
                    normalized_item["name"] = f"Item {i+1}"
                
                # Normalize quantity
                try:
                    if isinstance(item.get("quantity"), str):
                        qty_str = item["quantity"].strip()
                        import re
                        numeric_part = re.sub(r'[^0-9.]', '', qty_str)
                        if numeric_part:
                            normalized_item["quantity"] = float(numeric_part)
                        else:
                            normalized_item["quantity"] = 1
                            issues.append(f"Invalid quantity for item {i+1}, using default value 1")
                    elif not isinstance(item.get("quantity"), (int, float)) or item["quantity"] <= 0:
                        normalized_item["quantity"] = 1
                        issues.append(f"Invalid quantity for item {i+1}, using default value 1")
                except (ValueError, TypeError):
                    normalized_item["quantity"] = 1
                    issues.append(f"Invalid quantity format for item {i+1}, using default value 1")
                
                # Normalize price
                try:
                    if isinstance(item.get("unit_price"), str):
                        price_str = item["unit_price"].strip()
                        # Remove currency symbols and other non-numeric characters
                        import re
                        numeric_part = re.sub(r'[^0-9.]', '', price_str)
                        if numeric_part:
                            normalized_item["unit_price"] = float(numeric_part)
                        else:
                            issues.append(f"Invalid price for item {i+1}, please provide a valid number")
                    elif not isinstance(item.get("unit_price"), (int, float)) or item["unit_price"] <= 0:
                        issues.append(f"Invalid price for item {i+1}, please provide a positive number")
                except (ValueError, TypeError):
                    issues.append(f"Invalid price format for item {i+1}, please provide a valid number")
                
                normalized_items.append(normalized_item)
            
            modified_data["items"] = normalized_items
            
            # If no valid items, that's a problem
            if not normalized_items:
                issues.append("No valid items found in the quotation")
        else:
            issues.append("No items provided for the quotation")
        
        # Update the original data with normalized values
        data.update(modified_data)
        
        return issues

    async def generate_summary(self, data: Dict) -> str:
        """
        Generate a natural language summary of the quotation data.
        """
        prompt = f"""Generate a friendly, natural summary of this quotation data:
        {data}
        
        Format it as a clear, concise message that highlights:
        1. Customer details
        2. Items with quantities and prices
        3. Terms and conditions
        4. Discount (if any)
        5. Issued by (if provided)
        """
        
        try:
            logger.info(f"Generating summary for data: {json.dumps(data)[:100]}...")
            
            # Call the OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a quotation summary assistant. Generate clear, friendly summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            summary = response.choices[0].message.content
            logger.info(f"Generated summary: {summary[:100]}...")  # Log first 100 chars
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Create a fallback summary from the data
            try:
                items_text = ""
                if "items" in data and data["items"]:
                    items = data["items"]
                    for item in items:
                        items_text += f"- {item.get('name', 'Unknown item')}: {item.get('quantity', 0)} x ${item.get('unit_price', 0.0)}\n"
                
                return (
                    f"Summary of quotation for {data.get('customer_name', 'Customer')} at {data.get('customer_company', 'Company')}:\n\n"
                    f"Contact: {data.get('customer_email', 'No email')} / {data.get('customer_phone', 'No phone')}\n"
                    f"Address: {data.get('customer_address', 'No address')}\n\n"
                    f"Items:\n{items_text}\n"
                    f"Terms & Conditions: {data.get('terms', 'None')}\n"
                    f"Discount: {data.get('discount', 0)}%\n"
                    f"Issued by: {data.get('issued_by', 'Not specified')}\n"
                )
            except Exception as inner_e:
                logger.error(f"Error creating fallback summary: {inner_e}")
                return "Error generating summary. Please check your data and try again." 