"""
Standalone OpenAI API test script
"""

import os
import json
import asyncio
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tests/openai_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Test data
TEST_INPUT = """
- Testing Sdn Bhd 
- Tan Ah Kow 
- 01066907222 
- hijef@gmail.com 
- N33-1, Jalan SS5, Taman Pelangi 
- Table 11238, 5 unit, 1000/unit 
- Chair 12387, 10 unit, 250/unit 
- Payment 25% upfront 
- Remainding payment on delivery
"""

async def test_openai_extraction():
    """Test OpenAI API for data extraction"""
    from openai import AsyncOpenAI
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is not set in environment variables")
        return
    
    logger.info(f"Using OpenAI API key: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=api_key)
        
        # Define prompt
        prompt = f"""Extract quotation data from the following text. 
        Return a JSON object with these fields:
        - customer_name: Customer's full name
        - customer_company: Company name
        - customer_address: Full address
        - customer_phone: Phone number
        - customer_email: Email address
        - items: List of items, each with name, quantity, and unit_price
        - terms: Payment terms
        - notes: Additional notes
        - discount: Discount percentage (if any)
        - issued_by: Name of person issuing the quote

        Text to analyze:
        {TEST_INPUT}

        If any field is missing or unclear, include it in the missing_fields list.
        Format the response as:
        {{
            "data": {{...}},
            "missing_fields": ["field1", "field2", ...]
        }}
        """
        
        # Call OpenAI API
        logger.info("Calling OpenAI API...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a more widely available model
            messages=[
                {"role": "system", "content": "You are a quotation data extraction assistant. Extract structured data from freeform text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Get raw response content
        raw_content = response.choices[0].message.content
        logger.info(f"Raw API Response: {raw_content}")
        
        # Save raw response
        with open("tests/openai_raw_response.json", "w") as f:
            f.write(raw_content)
        
        # Parse JSON
        try:
            result = json.loads(raw_content)
            logger.info(f"Parsed JSON: {json.dumps(result, indent=2)}")
            
            # Save parsed result
            with open("tests/openai_parsed_response.json", "w") as f:
                json.dump(result, f, indent=2)
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None

async def main():
    """Run the OpenAI test"""
    logger.info("Starting OpenAI test")
    
    result = await test_openai_extraction()
    
    if result:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed")
    
    logger.info("Test ended")

if __name__ == "__main__":
    asyncio.run(main()) 