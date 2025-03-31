"""
Test script for the GPT quotation parser.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.gpt_quotation import GPTQuotationParser
from app.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('tests/gpt_test_results.log')  # Log to file
    ]
)
logger = logging.getLogger(__name__)

# Test inputs
TEST_INPUTS = [
    # Test 1
    """
    - Testing Sdn Bhd 
    - Tan Ah Kow 
    - hijef@gmail.com 
    - N33-1, Jalan SS5, Taman Pelangi 
    - Table 11238, 5 unit, 1000/unit 
    - Chair 12387, 10 unit, 250/unit 
    - Payment 25% upfront 
    - Remainding payment on delivery
    """,
    
    # Test 2
    """
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
]

async def run_test(parser, test_input, test_num):
    """Run a single test on the parser."""
    logger.info(f"Running Test {test_num}")
    logger.info(f"Input: {test_input}")
    
    try:
        # Test extraction
        data, missing_fields = await parser.extract_quotation_data(test_input)
        
        logger.info(f"Extracted data: {json.dumps(data, indent=2)}")
        logger.info(f"Missing fields: {missing_fields}")
        
        # Save results to file
        output_dir = Path(__file__).resolve().parent.parent / 'temp'
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / f"test_{test_num}_extraction.json", "w") as f:
            json.dump({"data": data, "missing_fields": missing_fields}, f, indent=2)
        
        # Test validation
        validation_issues = await parser.validate_quotation_data(data)
        logger.info(f"Validation issues: {validation_issues}")
        
        # Test summary generation
        if data:  # Only generate summary if we have data
            summary = await parser.generate_summary(data)
            logger.info(f"Generated summary: {summary}")
            
            with open(output_dir / f"test_{test_num}_summary.txt", "w") as f:
                f.write(summary)
        
        logger.info(f"Test {test_num} completed")
        return True
    
    except Exception as e:
        logger.error(f"Error in test {test_num}: {e}", exc_info=True)
        return False

async def main():
    """Run all tests."""
    logger.info("Starting GPT Quotation Parser tests")
    logger.info(f"Using OpenAI API key ending with: ...{Config.OPENAI_API_KEY[-4:]}")
    logger.info(f"Model being used: {GPTQuotationParser().model}")
    
    parser = GPTQuotationParser()
    
    for i, test_input in enumerate(TEST_INPUTS, 1):
        logger.info("-" * 80)
        success = await run_test(parser, test_input, i)
        logger.info(f"Test {i} {'succeeded' if success else 'failed'}")
        logger.info("-" * 80)
    
    logger.info("All tests completed")

if __name__ == "__main__":
    asyncio.run(main()) 