import sys
import pandas as pd
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import os
from collections import defaultdict
from typing import List, Dict, Optional

from core.scraper import CompanyScraper

class BatchProcessor:
    """
    Handles batch processing of company data mining operations.
    Responsible for managing batch operations, logging, and result handling.
    """
    
    def __init__(self, output_file: str):
        """
        Initialize BatchProcessor with configuration.
        
        Args:
            output_file (str): Path to the output Excel file
        """
        self.output_file = output_file
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging with UTF-8 encoding support"""
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler('scraper.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.handlers = []
        root_logger.addHandler(file_handler)
        root_logger.addHandler(stream_handler)
    
    def process_batch(self, companies: List[str], batch_number: int, 
                     absolute_start_index: int, max_workers: int) -> List[Dict]:
        """
        Process a single batch of companies.
        
        Args:
            companies (List[str]): List of company names to process
            batch_number (int): Current batch number
            absolute_start_index (int): Starting index in the overall dataset
            max_workers (int): Maximum number of concurrent workers
            
        Returns:
            List[Dict]: Results of processing each company
        """
        logging.info(f"Processing batch {batch_number} with {len(companies)} companies")
        
        scraper = CompanyScraper()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_company = {
                executor.submit(scraper.process_company, company): company 
                for company in companies
            }
            
            for future in future_to_company:
                company = future_to_company[future]
                try:
                    result = future.result()
                    results.append(result)
                    logging.info(f"Completed {company}: {result['status']}")
                except Exception as e:
                    logging.error(f"Failed to process {company}: {str(e)}")
                    results.append(self._create_failed_result(company))
        
        self._save_batch_results(results, batch_number, absolute_start_index)
        return results
    
    def _create_failed_result(self, company: str) -> Dict:
        """Create a standardized failed result entry."""
        return {
            'company_name': company,
            'website': None,
            'email': None,
            'phone': None,
            'status': 'failed'
        }
    
    def _save_batch_results(self, results: List[Dict], batch_number: int, 
                           absolute_start_index: int) -> None:
        """Save batch results to Excel file."""
        df_results = pd.DataFrame(results)
        
        if not os.path.exists(self.output_file):
            with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
                df_results.to_excel(writer, index=False)
        else:
            with pd.ExcelWriter(self.output_file, mode='a', engine='openpyxl', 
                              if_sheet_exists='overlay') as writer:
                current_position = absolute_start_index + (batch_number * len(results))
                start_row = current_position + 1
                df_results.to_excel(writer, index=False, startrow=start_row, header=False)
    
    def process_companies(self, input_file: str, start_index: int = 0, 
                         batch_size: int = 100, total_limit: Optional[int] = None,
                         max_workers: int = 5) -> None:
        """
        Process all companies from input file in batches.
        
        Args:
            input_file (str): Path to input Excel file
            start_index (int): Starting index in the dataset
            batch_size (int): Number of companies to process per batch
            total_limit (Optional[int]): Maximum number of companies to process
            max_workers (int): Maximum number of concurrent workers
        """
        try:
            df = pd.read_excel(input_file)
            all_companies = df.iloc[:, 0].tolist()
            total_companies = len(all_companies)
            
            if total_limit:
                total_companies = min(total_companies, total_limit)
            
            remaining_companies = total_companies - start_index
            num_batches = (remaining_companies + batch_size - 1) // batch_size
            
            logging.info(f"Starting processing of {remaining_companies} companies in {num_batches} batches")
            
            all_results = []
            
            for batch_num in range(num_batches):
                batch_start = start_index + (batch_num * batch_size)
                batch_end = min(batch_start + batch_size, total_companies)
                
                logging.info(f"Processing batch {batch_num + 1}/{num_batches} (companies {batch_start}-{batch_end})")
                
                batch_companies = [
                    str(company).strip() 
                    for company in all_companies[batch_start:batch_end] 
                    if pd.notna(company)
                ]
                
                batch_results = self.process_batch(
                    batch_companies, batch_num, start_index, max_workers
                )
                all_results.extend(batch_results)
                
                self._print_batch_summary(batch_results, batch_num + 1)
                
                if batch_num < num_batches - 1:
                    time.sleep(5)
            
            self._print_final_summary(all_results)
            
        except Exception as e:
            logging.error(f"Error processing companies: {str(e)}")
            raise
    
    def _print_batch_summary(self, results: List[Dict], batch_num: int) -> None:
        """Print summary for a single batch."""
        print(f"\nBatch {batch_num} Summary:")
        self._print_summary(results)
    
    def _print_final_summary(self, results: List[Dict]) -> None:
        """Print final summary of all results."""
        print("\nFinal Summary:")
        self._print_summary(results)
    
    def _print_summary(self, results: List[Dict]) -> None:
        """Print detailed summary statistics."""
        total = len(results)
        with_website = sum(1 for r in results if r['website'])
        with_email = sum(1 for r in results if r['email'])
        with_phone = sum(1 for r in results if r['phone'])
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        print("\nDetailed Summary Statistics:")
        print(f"Total companies processed: {total}")
        print(f"Successfully processed: {success_count} ({(success_count/total)*100:.1f}%)")
        print(f"Companies with website: {with_website} ({(with_website/total)*100:.1f}%)")
        print(f"Companies with email: {with_email} ({(with_email/total)*100:.1f}%)")
        print(f"Companies with phone: {with_phone} ({(with_phone/total)*100:.1f}%)")
        
        status_counts = defaultdict(int)
        for result in results:
            status_counts[result['status']] += 1
        
        print("\nStatus Breakdown:")
        for status, count in status_counts.items():
            print(f"{status}: {count} ({(count/total)*100:.1f}%)")