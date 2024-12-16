from batch_processors.batch_processor import BatchProcessor
from batch_processors.reprocessor import ReProcessor
from config.scraping_config import ScrapingConfig
import logging

def setup_logging():
    """Configure logging for the main script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('main_process.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

if __name__ == "__main__":
    setup_logging()
    config = ScrapingConfig()
    
    # Configuration parameters
    INPUT_FILE = 'data.xlsx'
    OUTPUT_FILE = 'data.xlsx'
    REPROCESSED_OUTPUT_FILE = 'data.xlsx'  # Optional: use same as OUTPUT_FILE to overwrite-
    BATCH_SIZE = 5
    
    try:
        #################################################
        # STAGE 1: Initial Batch Processing
        # Uncomment this section to run initial processing
        #################################################
        
        # logging.info("Starting initial batch processing...")
        # processor = BatchProcessor(output_file=OUTPUT_FILE)
        
        # processor.process_companies(
        #     input_file=INPUT_FILE,
        #     start_index=15500,
        #     total_limit=None,
        #     max_workers=config.MAX_WORKERS,
        #     batch_size=50
        # )
        
        #################################################
        # STAGE 2: Re-Processing for Missing Data
        # Uncomment this section to run re-processing
        #################################################
        
        logging.info("Starting re-processing of incomplete data...")
        reprocessor = ReProcessor(
            input_file=OUTPUT_FILE,
            output_file=REPROCESSED_OUTPUT_FILE,
            max_workers=config.MAX_WORKERS
        )
        reprocessor.reprocess_companies(BATCH_SIZE, start_index=0)
        
        #################################################
        # You can run either:
        # 1. Just Stage 1 (initial processing)
        # 2. Just Stage 2 (re-processing)
        # 3. Both stages sequentially
        # 
        # To run Stage 2 independently:
        # 1. Comment out Stage 1 code
        # 2. Uncomment Stage 2 code
        # 3. Make sure OUTPUT_FILE exists from a previous run
        #################################################
        
        logging.info("All processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        raise