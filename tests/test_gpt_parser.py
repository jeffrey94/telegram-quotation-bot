"""
Test script for GPT Quotation Parser
"""

import os
import sys
import json
import asyncio
import logging
from dotenv import load_dotenv

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.gpt_quotation import GPTQuotationParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tests/gpt_parser_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Test inputs
TEST_INPUTS = [
    """
    Test 1: 
    - Testing Sdn Bhd 
    - Tan Ah Kow 
    - 01066907222 
    - hijef@gmail.com 
    - N33-1, Jalan SS5, Taman Pelangi 
    - Table 11238, 5 unit, 1000/unit 
    - Chair 12387, 10 unit, 250/unit 
    - Payment 25% upfront 
    - Remainding payment on delivery
    """,
    
    """
    Test 2: 
    - Testing Sdn Bhd 
    - Tan Ah Kow 
    - hijef@gmail.com 
    - N33-1, Jalan SS5, Taman Pelangi 
    - Table 11238, 5 unit, 1000/unit 
    - Chair 12387, 10 unit, 250/unit 
    - Payment 25% upfront 
    - Remainding payment on delivery
    """
]

async def test_extraction(parser, text, test_num):
    """Test the extract_quotation_data method"""
    logger.info(f"Running Test {test_num}: Extract Quotation Data")
    logger.info(f"Input: {text}")
    
    try:
        data, missing_fields = await parser.extract_quotation_data(text)
        
        # Save results to file
        with open(f"tests/test{test_num}_extraction_results.json", "w") as f:
            json.dump({
                "data": data,
                "missing_fields": missing_fields
            }, f, indent=2)
        
        logger.info(f"Extracted Data: {data}")
        logger.info(f"Missing Fields: {missing_fields}")
        
        if missing_fields:
            logger.warning(f"Missing fields detected: {missing_fields}")
        
        return data, missing_fields
    
    except Exception as e:
        logger.error(f"Error in extraction test: {e}")
        return None, ["Error occurred during extraction"]

async def test_validation(parser, data, test_num):
    """Test the validate_quotation_data method"""
    logger.info(f"Running Test {test_num}: Validate Quotation Data")
    
    try:
        validation_issues = await parser.validate_quotation_data(data)
        
        # Save results to file
        with open(f"tests/test{test_num}_validation_results.json", "w") as f:
            json.dump({
                "validation_issues": validation_issues
            }, f, indent=2)
        
        logger.info(f"Validation Issues: {validation_issues}")
        
        if validation_issues:
            logger.warning(f"Validation issues detected: {validation_issues}")
        
        return validation_issues
    
    except Exception as e:
        logger.error(f"Error in validation test: {e}")
        return ["Error occurred during validation"]

async def test_summary(parser, data, test_num):
    """Test the generate_summary method"""
    logger.info(f"Running Test {test_num}: Generate Summary")
    
    try:
        summary = await parser.generate_summary(data)
        
        # Save results to file
        with open(f"tests/test{test_num}_summary_results.txt", "w") as f:
            f.write(summary)
        
        logger.info(f"Generated Summary: {summary[:100]}...")
        
        return summary
    
    except Exception as e:
        logger.error(f"Error in summary test: {e}")
        return "Error occurred during summary generation"

async def main():
    """Run all the tests"""
    logger.info("Starting GPT Quotation Parser Tests")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is not set in environment variables")
        return
    
    logger.info(f"Using OpenAI API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Create parser
    parser = GPTQuotationParser()
    
    # Run tests for each input
    for i, text in enumerate(TEST_INPUTS):
        logger.info(f"\n{'='*50}\nRunning Test Set {i+1}\n{'='*50}")
        
        # Test extraction
        data, missing_fields = await test_extraction(parser, text, i+1)
        
        if data:
            # Test validation
            validation_issues = await test_validation(parser, data, i+1)
            
            # Test summary generation
            summary = await test_summary(parser, data, i+1)
    
    logger.info("All tests completed")

if __name__ == "__main__":
    asyncio.run(main()) 