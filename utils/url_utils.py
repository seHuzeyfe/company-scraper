from urllib.parse import urlparse
from config.scraping_config import ScrapingConfig
class UrlUtils:
    scraping_config = ScrapingConfig()
    
    @staticmethod
    def is_valid_url(url: str, check_business_directories: bool = False) -> bool:
        """
        Validate URL format and domain with optional business directory checking.
        
        Args:
            url (str): URL to validate
            check_business_directories (bool): If True, also checks against business directory list
            
        Returns:
            bool: True if URL is valid according to specified criteria
        """
        try:
            parsed = urlparse(url)
            
            # Base validation criteria
            base_valid = all([
                parsed.scheme in ['http', 'https'],
                parsed.netloc,
                len(parsed.netloc) > 3,
                '.' in parsed.netloc,
                not any(excluded in parsed.netloc 
                       for excluded in ['facebook.com', 'twitter.com', 'linkedin.com'])
            ])
            
            # Return early if base validation fails
            if not base_valid:
                return False
                
            # Additional check for business directories if requested
            if check_business_directories:
                return not any(bd in parsed.netloc 
                             for bd in ScrapingConfig.BUSINESS_DIRECTORIES)
                             
            return True
            
        except Exception:
            return False