import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import logging
import re
import time
from random import uniform, choice
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from datetime import timedelta
import tldextract
from selenium.common.exceptions import TimeoutException
from collections import defaultdict
import sys

class EnhancedScrapingConfig:
    """Enhanced configuration settings for the scraper"""
    def __init__(self):

        self.CACHE_DIR = 'cache'
        self.CACHE_DURATION = timedelta(days=7)
        self.MAX_RETRIES = 2
        self.BASE_DELAY = 1/5
        self.MAX_WORKERS = 8
        self.TIMEOUT = 20
        self.USER_AGENTS = self._load_user_agents()
        self.SEARCH_ENGINES = [
            ('https://www.google.com/search?q={}', 'div.g'), # Google
            ('https://www.bing.com/search?q={}', 'li.b_algo'),  # Bing
            ('https://duckduckgo.com/?q={}', 'div.result__body'),  # DuckDuckGo
            ('https://www.ecosia.org/search?q={}', 'a.result-title'),  # Ecosia
            ('https://search.yahoo.com/search?p={}', 'div.Sr'),  # Yahoo
            # Add more search engines here...
        ]

        # Enhanced contact paths including multiple languages

        self.CONTACT_PATHS = {
        'english': [
            'contact', 'contact-us', 'about/contact', 'about-us/contact',
            'reach-us', 'get-in-touch', 'support', 'help', 'customer-service',
            'customer-support', 'contact-support', 'contact-form', 'feedback',
            'enquiry', 'inquiry', 'reach-out', 'connect', 'talk-to-us',
            'contact/sales', 'contact/support', 'helpdesk', 'help-center'
        ],
        'german': [
            'kontakt', 'uber-uns/kontakt', 'impressum', 'kontaktformular',
            'kundendienst', 'kundenservice', 'hilfe', 'uber-uns', 'support-de',
            'kontaktieren-sie-uns', 'schreiben-sie-uns'
        ],
        'spanish': [
            'contacto', 'contactenos', 'sobre-nosotros', 'contactar',
            'atencion-al-cliente', 'ayuda', 'soporte', 'servicio-al-cliente',
            'contactanos', 'escribenos', 'donde-estamos'
        ],
        'french': [
            'nous-contacter', 'contact-france', 'contactez-nous', 'aide',
            'service-client', 'support-fr', 'assistance', 'nous-ecrire',
            'coordonnees', 'service-clientele'
        ],
        'italian': [
            'contatti', 'contattaci', 'chi-siamo', 'assistenza',
            'servizio-clienti', 'supporto', 'dove-siamo', 'scrivici'
        ],
        'portuguese': [
            'contato', 'contacte-nos', 'fale-conosco', 'atendimento',
            'suporte', 'ajuda', 'onde-estamos', 'assistencia'
        ],
        'dutch': [
            'contact', 'neem-contact-op', 'klantenservice', 'over-ons',
            'hulp', 'ondersteuning', 'contact-opnemen'
        ],
        'file_extensions': [
            'contact.html', 'contact.php', 'contact.asp', 'contact.jsp',
            'contact.aspx', 'contact.shtml', 'contact.cfm', 'contact.py',
            'contact/', 'contact/index.html'
        ],
        'api_endpoints': [
            '/api/contact', '/api/v1/contact', '/api/support',
            '/api/feedback', '/contact/api', '/v1/contact'
        ]
    }
        # Business directories for fallback searches
        self.BUSINESS_DIRECTORIES = [
            'linkedin.com/company',
            'facebook.com/pages',
            'yellowpages.com',
            'yelp.com/biz'
        ]
    @staticmethod
    def _load_user_agents():
        """Load rotating list of user agents with extended browser coverage"""
        ua = UserAgent()
        # Get a mix of different browser user agents
        agents = []
        for _ in range(5):  # Get 5 of each type
            agents.extend([
                ua.chrome,
                ua.firefox,
                ua.safari,
                ua.edge,
                ua.random  # Mix in some random ones
            ])
        return list(set(agents))  # Remove duplicates
 


class EnhancedSeleniumManager:
    """Enhanced Selenium WebDriver manager with better error handling"""
    def __init__(self):
        self.options = self._configure_options()
    def _configure_options(self):
        """Configure Chrome WebDriver options for optimal performance and security"""
        options = Options()

        # Headless and security settings
        options.add_argument('--headless=new')  # New headless implementation
        options.add_argument('--no-sandbox')  # Required for running in containers
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        
        # Performance optimizations
        options.add_argument('--disable-extensions')  # Disable extensions
        options.add_argument('--disable-default-apps')  # Disable default apps
        options.add_argument('--disable-features=TranslateUI')  # Disable translation UI
        options.add_argument('--disable-plugins')  # Disable plugins
        options.add_argument('--disable-background-networking')  # Disable background network traffic
        options.add_argument('--disable-background-timer-throttling')  # Disable timer throttling
        options.add_argument('--disable-backgrounding-occluded-windows')  # Disable background throttling
        options.add_argument('--disable-breakpad')  # Disable crash reporting
        options.add_argument('--disable-component-extensions-with-background-pages')  # Disable background extensions
        
        # Memory optimizations
        options.add_argument('--disable-ipc-flooding-protection')  # Disable IPC flooding protection
        options.add_argument('--disable-renderer-backgrounding')  # Prevent renderer code from being deprioritized
        options.add_argument('--memory-pressure-off')  # Disable memory pressure checks
        options.add_argument('--no-zygote')  # Disable the zygote process
        
        # Browser behavior
        options.add_argument('--disable-notifications')  # Disable notifications
        options.add_argument('--disable-popup-blocking')  # Disable popup blocking
        options.add_argument('--disable-prompt-on-repost')  # Disable repost prompting
        options.add_argument('--disable-hang-monitor')  # Disable hang monitor
        options.add_argument('--disable-client-side-phishing-detection')  # Disable phishing detection
        
        # Logging and debugging
        options.add_argument('--log-level=3')  # Set log level to WARNING
        options.add_argument('--silent')  # Suppress console logging
        options.add_argument('--disable-logging')  # Disable logging
        options.add_argument('--ignore-certificate-errors')  # Ignore SSL certificate errors
        options.add_argument('--allow-insecure-localhost')  # Allow insecure localhost
        
        
        # Additional optimization preferences
        prefs = {
            'profile.default_content_setting_values.notifications': 2,  # Disable notification prompts
            'profile.default_content_setting_values.media_stream_mic': 2,  # Disable mic prompts
            'profile.default_content_setting_values.media_stream_camera': 2,  # Disable camera prompts
            'profile.default_content_setting_values.geolocation': 2,  # Disable location prompts
            'profile.managed_default_content_settings.images': 2,  # Disable images (optional)
            'disk-cache-size': 4096,  # Limit disk cache size
            'profile.password_manager_enabled': False,  # Disable password manager
            'credentials_enable_service': False,  # Disable credential service
            'profile.default_content_settings.popups': 0,  # Disable popups
            'download.prompt_for_download': False,  # Auto-download without prompting
            'download.default_directory': '/dev/null',  # Prevent downloads from taking space
        }
        options.add_experimental_option('prefs', prefs)
        
        # Exclude logging and automation flags
        options.add_experimental_option('excludeSwitches', [
            'enable-automation',
            'enable-logging',
            'enable-blink-features=AutomationControlled'
        ])
        
        # Additional experimental options
        options.add_experimental_option('useAutomationExtension', False)
        
        return options

    def get_driver(self):
        try:
            driver = webdriver.Chrome(options=self.options)
            driver.set_page_load_timeout(15)
            # Set window size to ensure consistent rendering
            driver.set_window_size(1920, 1080)
            return driver
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

class EnhancedContactExtractor:
    """Enhanced contact information extraction with improved patterns"""
    def __init__(self):
        self.setup_patterns()
    def setup_patterns(self):
        """Setup enhanced regex patterns for contact information"""
        self.email_patterns = [
            # Standard email with improved validation and TLD support
            r'''(?x)                     # Verbose mode for readability
            (?:mailto:|e-?mail:?\s*)?    # Optional mailto: or email: prefix
            ([a-zA-Z0-9]                 # Username must start with alphanumeric
            [a-zA-Z0-9._%+-]{0,63}       # Rest of username (max 64 chars)
            @                            # @ symbol
            [a-zA-Z0-9]                 # Domain must start with alphanumeric
            [a-zA-Z0-9.-]*              # Rest of domain
            \.                          # Dot
            [a-zA-Z]{2,}                # TLD
            (?:\.[a-zA-Z]{2,})?         # Optional secondary TLD (e.g., .co.uk)
            )''',
            
            # Obfuscated email with improved flexibility
            r'''(?x)
            ([a-zA-Z0-9._%+-]+          # Username
            \s*[\[\({⟨<]?\s*           # Optional opening bracket with flexible spacing
            (?:at|@)\s*                 # @ symbol or 'at' with flexible spacing
            [\]\)}⟩>]?\s*              # Optional closing bracket with flexible spacing
            [a-zA-Z0-9][a-zA-Z0-9.-]*   # Domain
            \s*[\[\({⟨<]?\s*           # Optional opening bracket
            (?:dot|\.)\s*              # Dot or 'dot' with flexible spacing
            [\]\)}⟩>]?\s*              # Optional closing bracket
            [a-zA-Z]{2,}                # TLD
            (?:\s*[\[\({⟨<]?\s*        # Optional secondary TLD section
            (?:dot|\.)\s*
            [\]\)}⟩>]?\s*
            [a-zA-Z]{2,})?              # Secondary TLD
            )''',

            # Add to email_patterns
            r'''(?x)
            (?:mailto:)?
            ([a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})
            ''',
                        
            # HTML encoded email with hex and decimal entities
            r'''(?x)
            ((?:&#[x0-9a-fA-F]+;|      # Hex entities
            &#\d+;|                     # Decimal entities
            &[a-zA-Z]+;|               # Named entities
            [a-zA-Z0-9._%+-])+         # Regular characters
            @
            (?:&#[x0-9a-fA-F]+;|
            &#\d+;|
            &[a-zA-Z]+;|
            [a-zA-Z0-9.-])+
            \.[a-zA-Z]{2,})'''
        ]

        # Phone patterns with improved international support
        self.phone_patterns = [
            # International format with flexible grouping
            r'''(?x)
            (?:\+|00)                   # International prefix (+ or 00)
            [1-9]\d{0,3}               # Country code (1-4 digits)
            (?:[\s.-]*\d){8,12}        # Rest of the number with flexible separators
            [\s.-]?                     # Optional separator
            \(?                         # Optional opening parenthesis
            \d{1,4}                    # Area/city code
            \)?                         # Optional closing parenthesis
            [\s.-]?                     # Optional separator
            \d{1,4}                    # First group of digits
            [\s.-]?                     # Optional separator
            \d{2,10}                   # Remaining digits
            ''',
            
            # North American format with extension support
            r'''(?x)
            (?:\+?1[\s.-]?)?           # Optional country code
            \(?[2-9]\d{2}\)?          # Area code (200-999)
            [\s.-]?
            [2-9]\d{2}                # Exchange code (200-999)
            [\s.-]?
            \d{4}                     # Subscriber number
            (?:                       # Extension part
                \s*(?:ext|x|extension)
                [\s.:-]*
                \d{2,5}
            )?''',

            r'tel:[\+]?[0-9]{11}',
            
            # European format with variable lengths
            r'''(?x)
            \+[1-9][0-9]{1,2}         # Country code
            [\s.-]?
            (?:\([1-9]\d{0,4}\)|     # Area code in parentheses
            [1-9]\d{0,4})         # or without parentheses
            [\s.-]?
            \d{4,10}                  # Main number
            ''',
            
            # General format with common labels
            r'''(?x)
            (?:tel|tél|phone|telephone|contact|call|fax|mobile|cell)
            [\s:]+                    # Separator after label
            [\+\d\s\(\)-\.]{8,20}    # Number with flexible formatting
            ''',

            # For UK phone numbers
            r'''(?x)
            (?:
                (?:0|\+44)\s*
                [1-9]\d{2,4}\s*
                \d{6}
            )
            '''
        ]

        # Schema.org and structured data patterns
        self.schema_patterns = {
            'email': [
                r'"email"\s*:\s*"([^"]+?@[^"]+?\.[^"]+)"',
                r'"contactPoint"\s*:\s*{[^}]*"email"\s*:\s*"([^"]+?@[^"]+?\.[^"]+)"',
                r'<meta\s+(?:property|name)="(?:og:)?email"\s+content="([^"]+?@[^"]+?\.[^"]+)"',
                r'data-email="([^"]+?@[^"]+?\.[^"]+)"'
            ],
            'phone': [
                r'"telephone"\s*:\s*"([\+\d\s\(\)-\.]{8,20})"',
                r'"contactPoint"\s*:\s*{[^}]*"telephone"\s*:\s*"([\+\d\s\(\)-\.]{8,20})"',
                r'<meta\s+(?:property|name)="(?:og:)?phone_number"\s+content="([\+\d\s\(\)-\.]{8,20})"',
                r'data-phone="([\+\d\s\(\)-\.]{8,20})"'
            ],
            'website': [
                r'"url"\s*:\s*"((?:https?:)?//[^"]+)"',
                r'"website"\s*:\s*"((?:https?:)?//[^"]+)"',
                r'<meta\s+(?:property|name)="(?:og:)?url"\s+content="((?:https?:)?//[^"]+)"',
                r'data-website="((?:https?:)?//[^"]+)"'
            ]
        }

class EnhancedCompanyScraper:
    """Enhanced scraper with improved contact information extraction"""
    def __init__(self):
        self.config = EnhancedScrapingConfig()
        self.selenium_manager = EnhancedSeleniumManager()
        self.contact_extractor = EnhancedContactExtractor()
        self.session = self._create_session()
        self.cache = {}
    def _create_session(self):
        """Create a persistent session with retry mechanism"""
        session = requests.Session()
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5,de;q=0.3,es;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        return session


    def _get_company_domain(self, company_name):
        """Enhanced company domain search with multiple search engines and fallbacks"""
        for search_engine, selector in self.config.SEARCH_ENGINES:
            try:
                domain = self._search_engine_lookup(company_name, search_engine, selector)
                if domain:
                    return domain  

                # Try with additional search terms
                domain = self._search_engine_lookup(
                    f"{company_name} official website contact",
                    search_engine,
                    selector
                )
                if domain:
                    return domain            
            except Exception as e:
                logging.error(f"Search engine error ({search_engine}): {str(e)}")
                continue
       
        # Fallback to business directories
        return self._search_business_directories(company_name)

    def _search_engine_lookup(self, query, search_engine, selector):
        """Perform search engine lookup with enhanced error handling"""
        driver = None
        try:
            driver = self.selenium_manager.get_driver()
            search_url = search_engine.format(query.replace(' ', '+'))         
            driver.get(search_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            results = driver.find_elements(By.CSS_SELECTOR, selector)
            for result in results[:5]:  # Check top 5 results
                try:
                    link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    if self._is_valid_company_site(link, query):
                        return link
                except:
                    continue                    
            return None            
        except TimeoutException:
            logging.warning(f"Timeout during search for: {query}")
            return None
        except Exception as e:
            logging.error(f"Search error for {query}: {str(e)}")
            return None         
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def _search_business_directories(self, company_name):
        """Search business directories for company information"""
        for directory in self.config.BUSINESS_DIRECTORIES:
            try:
                response = self._make_request(
                    f"https://www.google.com/search?q=site:{directory}+{company_name}"
                )
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.select('.g a')
                    for result in results:
                        href = result.get('href', '')
                        if directory in href and company_name.lower() in href.lower():
                            return self._extract_website_from_directory(href)
            except Exception as e:
                logging.error(f"Directory search error ({directory}): {str(e)}")
                continue
        return None

    def _extract_website_from_directory(self, directory_url):
        """Extract website from business directory listing"""
        try:
            response = self._make_request(directory_url)
            if not response:
                return None
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for website links
            website_patterns = [
                r'website|official site|homepage|web page',
                r'visit.*site|view.*website'
            ]
            for pattern in website_patterns:
                links = soup.find_all('a', text=re.compile(pattern, re.I))
                for link in links:
                    href = link.get('href', '')
                    if self._is_valid_website_url(href):
                        return href
            return None
        except Exception as e:
            logging.error(f"Directory extraction error: {str(e)}")
            return None


    def _is_valid_website_url(self, url):
        """Validate if URL is a legitimate website"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ['http', 'https'],
                len(parsed.netloc) > 3,
                '.' in parsed.netloc,
                not any(bd in parsed.netloc for bd in self.config.BUSINESS_DIRECTORIES)
            ])
        except:
            return False



    def _is_valid_company_site(self, url, company_name):
        """Enhanced validation of company website"""
        try:
            # Extract domain information
            ext = tldextract.extract(url)
            domain = ext.domain.lower()           
            # Clean company name and create variations
            company_clean = re.sub(r'[^\w\s]', '', company_name.lower())
            company_words = set(company_clean.split())
            company_initials = ''.join(word[0] for word in company_clean.split())
            # Excluded domains and patterns
            excluded_domains = {
                'facebook', 'linkedin', 'twitter', 'instagram', 'youtube',
                'amazon', 'wikipedia', 'bloomberg', 'crunchbase'
            }
            if ext.domain in excluded_domains:
                return False
                
            # Check various matching criteria
            domain_matches = [
                any(word in domain for word in company_words if len(word) > 2),
                company_initials == domain,
                company_clean.replace(' ', '') == domain,
                self._calculate_similarity(company_clean, domain) > 0.8
            ]
            return any(domain_matches)
        except Exception as e:
            logging.error(f"Domain validation error: {str(e)}")
            return False


    def _calculate_similarity(self, str1, str2):
        """Calculate string similarity ratio"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()


    def _make_request(self, url, retry_count=0):
        """Enhanced request handling with smart retries"""
        if retry_count >= self.config.MAX_RETRIES:
            return None
        try:
            # Update headers with random user agent
            self.session.headers.update({
                'User-Agent': choice(self.config.USER_AGENTS)
            })
            # Add jitter to delay
            delay = self.config.BASE_DELAY + uniform(0.1, 0.5)
            time.sleep(delay)
            response = self.session.get(
                url,
                timeout=self.config.TIMEOUT,
                allow_redirects=True
            )
            if response.status_code == 200:
                return response
            # Handle specific status codes
            if response.status_code == 429:  # Too many requests
                time.sleep(delay * (retry_count + 1))
                return self._make_request(url, retry_count + 1)

            if response.status_code in [301, 302, 303, 307, 308]:  # Redirects
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    return self._make_request(redirect_url, retry_count)
            return None
        except requests.exceptions.Timeout:
            time.sleep(delay)
            return self._make_request(url, retry_count + 1)
        except requests.exceptions.ConnectionError:
            time.sleep(delay * 2)
            return self._make_request(url, retry_count + 1)
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {url}: {str(e)}")
            return None

    def _find_contact_pages(self, soup, base_url):
        """Enhanced contact page discovery"""
        contact_pages = set()
        # Search in navigation menus
        for nav in soup.find_all(['nav', 'header', 'footer']):
            self._extract_contact_links(nav, base_url, contact_pages)
        # Search in sitemaps
        sitemap_links = soup.find_all('a', href=re.compile(r'sitemap', re.I))
        for link in sitemap_links:
            try:
                sitemap_url = urljoin(base_url, link['href'])
                sitemap_response = self._make_request(sitemap_url)
                if sitemap_response:
                    sitemap_soup = BeautifulSoup(sitemap_response.text, 'html.parser')
                    self._extract_contact_links(sitemap_soup, base_url, contact_pages)
            except Exception as e:
                logging.error(f"Sitemap error: {str(e)}")

        # Look for contact information in JSON-LD
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                json_data = json.loads(script.string)
                contact_url = self._extract_contact_from_jsonld(json_data)
                if contact_url:
                    contact_pages.add(urljoin(base_url, contact_url))
            except:
                continue
        return list(contact_pages)


    def _extract_contact_links(self, element, base_url, contact_pages):
        """Extract contact page links from element"""
        for anchor in element.find_all('a', href=True):
            href = anchor['href'].lower()
            text = anchor.get_text().lower()

            # Check both href and text for contact-related terms
            if any(path in href or path in text for path in self.config.CONTACT_PATHS):
                full_url = urljoin(base_url, anchor['href'])
                if self._is_valid_url(full_url):
                    contact_pages.add(full_url)

    def _extract_contact_from_jsonld(self, json_data):
        """Extract contact URL from JSON-LD data"""
        if isinstance(json_data, dict):
            if 'contactPoint' in json_data:
                return json_data.get('contactPoint', {}).get('url')
            if 'url' in json_data and any(term in json_data.get('url', '').lower() 
                                        for term in self.config.CONTACT_PATHS):
                return json_data['url']
        return None


    def _is_valid_url(self, url):
        """Validate URL format and domain"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ['http', 'https'],
                parsed.netloc,
                not any(excluded in parsed.netloc 
                       for excluded in ['facebook.com', 'twitter.com', 'linkedin.com'])
            ])
        except:
            return False

    def _extract_contact_info(self, url):
        """Enhanced contact information extraction with additional method"""
        contact_info = {'website': url, 'email': None, 'phone': None}
        visited_urls = set()
        try:
            # Get main page
            response = self._make_request(url)
            if not response:
                return contact_info
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract from schema.org metadata
            self._extract_schema_contact_info(soup, contact_info)

            # Find contact pages
            contact_pages = self._find_contact_pages(soup, url)

            # Process each page
            for page_url in [url] + contact_pages:
                if page_url in visited_urls:
                    continue

                visited_urls.add(page_url)
                try:
                    if page_url != url:
                        response = self._make_request(page_url)
                        if not response:
                            continue
                        soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract contact information using multiple methods
                    self._extract_visible_contact_info(soup, contact_info)
                    self._extract_metadata_contact_info(soup, contact_info)
                    self._extract_microdata_contact_info(soup, contact_info)
                    self._extract_javascript_contact_info(soup, contact_info)  # New method

                    # Additional extraction from frames and iframes
                    frames = soup.find_all(['frame', 'iframe'])
                    for frame in frames:
                        frame_url = frame.get('src', '')
                        if frame_url and frame_url.startswith(('http://', 'https://')):
                            try:
                                frame_response = self._make_request(frame_url)
                                if frame_response:
                                    frame_soup = BeautifulSoup(frame_response.text, 'html.parser')
                                    self._extract_visible_contact_info(frame_soup, contact_info)
                                    self._extract_metadata_contact_info(frame_soup, contact_info)
                                    self._extract_microdata_contact_info(frame_soup, contact_info)
                                    self._extract_javascript_contact_info(frame_soup, contact_info)
                            except Exception as e:
                                logging.error(f"Error extracting from frame {frame_url}: {str(e)}")
                                continue

                    # If we found both email and phone, we can stop
                    if contact_info['email'] and contact_info['phone']:
                        break
                        
                except Exception as e:
                    logging.error(f"Error extracting from {page_url}: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error processing {url}: {str(e)}")
            
        return contact_info

    def _extract_javascript_contact_info(self, soup, contact_info):
        """
        Extract contact information embedded in JavaScript/JSON data and dynamic content
        """
        # Find all script tags
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if not script.string:
                continue
                
            script_content = script.string.strip()
            
            # Look for contact info in JavaScript object literals
            if not contact_info['email']:
                # Search for email patterns in JavaScript variables
                for pattern in self.contact_extractor.email_patterns:
                    matches = re.finditer(pattern, script_content, re.I)
                    for match in matches:
                        email = match.group(1)
                        if self._validate_email(email):
                            contact_info['email'] = email
                            break
                            
            if not contact_info['phone']:
                # Search for phone patterns in JavaScript variables
                for pattern in self.contact_extractor.phone_patterns:
                    matches = re.finditer(pattern, script_content)
                    for match in matches:
                        phone = match.group(0)
                        if self._validate_phone(phone):
                            contact_info['phone'] = self._format_phone(phone)
                            break
                            
            # Extract from JSON config objects
            try:
                # Find JSON-like structures in JavaScript
                json_matches = re.finditer(r'(?:window\.|var\s+)?[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*({[^;]+});', script_content)
                
                for json_match in json_matches:
                    try:
                        json_str = json_match.group(1)
                        # Parse potential JSON object
                        json_data = json.loads(json_str)
                        
                        # Recursively search for contact info in JSON structure
                        self._search_json_recursively(json_data, contact_info)
                        
                    except json.JSONDecodeError:
                        continue
                        
            except Exception as e:
                logging.debug(f"Error parsing JavaScript content: {str(e)}")
                continue

    def _search_json_recursively(self, json_data, contact_info):
        """
        Recursively search through JSON structure for contact information
        """
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                # Look for common key patterns
                key_lower = key.lower()
                if 'email' in key_lower or 'mail' in key_lower:
                    if isinstance(value, str) and self._validate_email(value):
                        contact_info['email'] = value
                        
                if 'phone' in key_lower or 'tel' in key_lower:
                    if isinstance(value, str) and self._validate_phone(value):
                        contact_info['phone'] = self._format_phone(value)
                        
                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    self._search_json_recursively(value, contact_info)
                    
        elif isinstance(json_data, list):
            for item in json_data:
                if isinstance(item, (dict, list)):
                    self._search_json_recursively(item, contact_info)

    def _extract_schema_contact_info(self, soup, contact_info):
        """Extract contact information from schema.org markup"""
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Extract from ContactPoint
                    contact_point = data.get('contactPoint', {})
                    if not contact_info['email']:
                        contact_info['email'] = contact_point.get('email')
                    if not contact_info['phone']:
                        contact_info['phone'] = contact_point.get('telephone')

                    # Extract from Organization
                    if not contact_info['email']:
                        contact_info['email'] = data.get('email')
                    if not contact_info['phone']:
                        contact_info['phone'] = data.get('telephone')
            except:
                continue

    def _extract_visible_contact_info(self, soup, contact_info):
        """
        Extract contact information from visible content with enhanced nested structure handling
        """
        # Common builder class patterns
        builder_patterns = {
            'uabb': {
                'container': 'uabb-info-list-item',
                'content': 'uabb-info-list-description',
                'title': 'uabb-info-list-title'
            },
            'elementor': {
                'container': 'elementor-widget-container',
                'content': 'elementor-text-editor',
            },
            'wpbakery': {
                'container': 'vc_column_text',
                'content': 'wpb_wrapper',
            }
        }

        # First try to extract from common page builder structures
        for builder, classes in builder_patterns.items():
            # Find all container elements for this builder
            containers = soup.find_all(class_=classes['container'])
            
            for container in containers:
                # Extract from container
                self._extract_from_builder_element(container, contact_info)
                
                # If we found both email and phone, we can stop
                if contact_info['email'] and contact_info['phone']:
                    return

        # If not found in builder structures, try common contact sections
        contact_sections = soup.find_all(['div', 'section'], class_=re.compile(
            r'contact|footer|header|info|details', re.I))
        
        for section in contact_sections:
            # Deep traversal of nested elements
            self._deep_traverse_element(section, contact_info)
            
            if contact_info['email'] and contact_info['phone']:
                return

        phone_links = soup.find_all('a', href=True)
        for link in phone_links:
            href = link.get('href', '').lower()
            if href.startswith('tel:'):
                phone = href.replace('tel:', '').strip()
                if self._validate_phone(phone):
                    contact_info['phone'] = self._format_phone(phone)
                    break

        # Fallback to general content if still not found
        if not (contact_info['email'] and contact_info['phone']):
            text_content = soup.get_text()
            self._extract_from_text(text_content, contact_info)

    def _extract_from_builder_element(self, element, contact_info):
        """
        Extract contact information from a specific builder element
        """
        # Check for mailto links first
        email_links = element.find_all('a', href=re.compile(r'mailto:', re.I))
        for link in email_links:
            email = link.get('href', '').replace('mailto:', '').strip()
            if self._validate_email(email):
                contact_info['email'] = email
                break

        # Check for tel links
        phone_links = element.find_all('a', href=re.compile(r'tel:', re.I))
        for link in phone_links:
            phone = link.get('href', '').replace('tel:', '').strip()
            if self._validate_phone(phone):
                contact_info['phone'] = self._format_phone(phone)
                break

        # Extract from text content within paragraphs and spans
        text_elements = element.find_all(['p', 'span', 'div'])
        for text_elem in text_elements:
            text_content = text_elem.get_text()
            
            # Extract email if not found yet
            if not contact_info['email']:
                for pattern in self.contact_extractor.email_patterns:
                    matches = re.finditer(pattern, text_content, re.I)
                    for match in matches:
                        email = match.group(1)
                        if self._validate_email(email):
                            contact_info['email'] = email
                            break
            
            # Extract phone if not found yet
            if not contact_info['phone']:
                for pattern in self.contact_extractor.phone_patterns:
                    matches = re.finditer(pattern, text_content)
                    for match in matches:
                        phone = match.group(0)
                        if self._validate_phone(phone):
                            contact_info['phone'] = self._format_phone(phone)
                            break

    def _deep_traverse_element(self, element, contact_info):
        """
        Recursively traverse nested elements to find contact information
        """
        # Skip if we've found both email and phone
        if contact_info['email'] and contact_info['phone']:
            return

        # Process current element
        if isinstance(element, str):
            self._extract_from_text(element, contact_info)
            return

        # Check element attributes
        for attr in ['href', 'data-email', 'data-phone', 'content']:
            if attr in element.attrs:
                attr_value = element[attr]
                if isinstance(attr_value, str):
                    self._extract_from_text(attr_value, contact_info)

        # Process element's direct text
        if element.string:
            self._extract_from_text(element.string, contact_info)

        # Recursively process children
        for child in element.children:
            if not isinstance(child, str) or child.strip():
                self._deep_traverse_element(child, contact_info)

    def _extract_from_text(self, text, contact_info):
        """
        Extract contact information from a text string
        """
        if not isinstance(text, str):
            return

        # Extract email if not found yet
        if not contact_info['email']:
            for pattern in self.contact_extractor.email_patterns:
                matches = re.finditer(pattern, text, re.I)
                for match in matches:
                    email = match.group(1)
                    if self._validate_email(email):
                        contact_info['email'] = email
                        break

        # Extract phone if not found yet
        if not contact_info['phone']:
            for pattern in self.contact_extractor.phone_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    phone = match.group(0)
                    if self._validate_phone(phone):
                        contact_info['phone'] = self._format_phone(phone)
                        break

    def _extract_metadata_contact_info(self, soup, contact_info):
        """Extract contact information from metadata with enhanced pattern usage"""
        # Use schema patterns for metadata extraction
        for pattern_type, patterns in self.contact_extractor.schema_patterns.items():
            if pattern_type in ['email', 'phone'] and not contact_info[pattern_type]:
                for pattern in patterns:
                    matches = soup.find_all(string=re.compile(pattern))
                    for match in matches:
                        try:
                            extracted = re.search(pattern, match).group(1)
                            if pattern_type == 'email' and self._validate_email(extracted):
                                contact_info['email'] = extracted
                                break
                            elif pattern_type == 'phone' and self._validate_phone(extracted):
                                contact_info['phone'] = self._format_phone(extracted)
                                break
                        except:
                            continue

    def _extract_microdata_contact_info(self, soup, contact_info):
        """Extract contact information from microdata"""
        # Check itemtype="http://schema.org/Organization"
        org_elements = soup.find_all(itemtype=re.compile(r'schema.org/Organization'))
        for element in org_elements:
            if not contact_info['email']:
                email_elem = element.find(itemprop='email')
                if email_elem:
                    email = email_elem.get('content', email_elem.get_text())
                    if self._validate_email(email):
                        contact_info['email'] = email

            if not contact_info['phone']:
                phone_elem = element.find(itemprop='telephone')
                if phone_elem:
                    phone = phone_elem.get('content', phone_elem.get_text())
                    if self._validate_phone(phone):
                        contact_info['phone'] = self._format_phone(phone)

    def _validate_email(self, email):
        """Enhanced email validation"""
        try:
            email = email.lower().strip()

            # Basic format check
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return False

            # Check domain
            domain = email.split('@')[1]

            # Exclude common invalid domains
            invalid_domains = {
                'example.com', 'domain.com', 'email.com', 'test.com',
                'yourwebsite.com', 'company.com', 'website.com'
            }

            if domain in invalid_domains:
                return False

            # Additional checks
            if len(email) > 254 or len(email) < 3:
                return False
            return True
        except:
            return False

    def _validate_phone(self, phone):
        """Validate phone number"""
        # Clean the phone number
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Check length
        if len(cleaned) < 5 or len(cleaned) > 20:
            return False

        # Must contain at least some digits
        if not re.search(r'\d', cleaned):
            return False
        return True

    def _format_phone(self, phone):
        """Format phone number consistently"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Format international numbers
        if cleaned.startswith('+'):
            return cleaned
      
        # Format US/Canada numbers
        if len(cleaned) == 10:
            return f"+1{cleaned}"      
        return cleaned

    def process_company(self, company_name):
        """Process a single company with enhanced error handling and logging"""
        try:
            # Ensure company_name is properly encoded as UTF-8 if it's not already
            if isinstance(company_name, bytes):
                company_name = company_name.decode('utf-8')           
            logging.info(f"Processing company: {company_name}")
        
            result = {
                'company_name': company_name,
                'website': None,
                'email': None,
                'phone': None,
                'status': 'success'
            }
        
            try:
                # Find company website
                website = self._get_company_domain(company_name)
                if website:
                    result['website'] = website
                    
                    # Extract contact information
                    contact_info = self._extract_contact_info(website)
                    result.update(contact_info)
                else:
                    result['status'] = 'no_website_found'
            except Exception as e:
                logging.error(f"Error processing company {company_name}: {str(e)}")
                result['status'] = 'error'        
            return result
            
        except UnicodeEncodeError as e:
            logging.error(f"Unicode encoding error while processing company: {str(e)}")
            return {
                'company_name': str(company_name.encode('utf-8')),  # Fallback encoding
                'website': None,
                'email': None,
                'phone': None,
                'status': 'encoding_error'
            }

def setup_logging():
    """Configure logging with UTF-8 encoding support"""
    # Create log formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Set up file handler with UTF-8 encoding
    file_handler = logging.FileHandler('scraper.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Set up stream handler with UTF-8 encoding
    stream_handler = logging.StreamHandler(sys.stdout)  # Use sys.stdout instead of default stderr
    stream_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    root_logger.handlers = []
    
    # Add our configured handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

def process_batch(companies, batch_number, output_file, absolute_start_index):
    """Process a single batch of companies"""
    logging.info(f"Processing batch {batch_number} with {len(companies)} companies")
    
    scraper = EnhancedCompanyScraper()
    results = []
    
    # Process companies with thread pool
    with ThreadPoolExecutor(max_workers=EnhancedScrapingConfig().MAX_WORKERS) as executor:
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
                results.append({
                    'company_name': company,
                    'website': None,
                    'email': None,
                    'phone': None,
                    'status': 'failed'
                })
    
    # Save batch results
    df_results = pd.DataFrame(results)
    
    # If this is the first time writing to the file and it doesn't exist, write with headers
    if not os.path.exists(output_file):
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_results.to_excel(writer, index=False)
    else:
        # Read existing file and append
        with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            # Calculate the start row based on absolute_start_index and current batch
            current_position = absolute_start_index + (batch_number * len(companies))
            # Add 1 to account for header row
            start_row = current_position + 1
            df_results.to_excel(writer, index=False, startrow=start_row, header=False)
    
    return results

def process_companies_in_batches(input_file, output_file, start_index=0, batch_size=100, total_limit=None):
    """Process companies from input file in batches"""
    setup_logging()
    
    try:
        # Read the total number of companies with explicit dtype for company column
        df = pd.read_excel(input_file)
        all_companies = df.iloc[:, 0].tolist()
        total_companies = len(all_companies)
        
        # Apply total limit if specified
        if total_limit:
            total_companies = min(total_companies, total_limit)
        
        # Calculate number of batches
        remaining_companies = total_companies - start_index
        num_batches = (remaining_companies + batch_size - 1) // batch_size
        
        logging.info(f"Starting processing of {remaining_companies} companies in {num_batches} batches")
        
        all_results = []
        
        # Process each batch
        for batch_num in range(num_batches):
            batch_start = start_index + (batch_num * batch_size)
            batch_end = min(batch_start + batch_size, total_companies)
            
            logging.info(f"Processing batch {batch_num + 1}/{num_batches} (companies {batch_start}-{batch_end})")
            
            # Get companies for this batch and ensure they're strings
            batch_companies = [
                str(company).strip() 
                for company in all_companies[batch_start:batch_end] 
                if pd.notna(company)
            ]
            
            # Pass start_index to process_batch
            batch_results = process_batch(batch_companies, batch_num, output_file, start_index)
            all_results.extend(batch_results)
            
            # Print batch summary
            print(f"\nBatch {batch_num + 1} Summary:")
            print_summary(batch_results)
            
            # Optional delay between batches
            if batch_num < num_batches - 1:
                time.sleep(10)  # 5 second delay between batches
        
        # Print final summary
        print("\nFinal Summary:")
        print_summary(all_results)
        
    except Exception as e:
        logging.error(f"Error processing companies: {str(e)}")
        raise

def print_summary(results):
    """Print detailed summary statistics"""
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
    
    # Status breakdown
    status_counts = defaultdict(int)
    for result in results:
        status_counts[result['status']] += 1
    
    print("\nStatus Breakdown:")
    for status, count in status_counts.items():
        print(f"{status}: {count} ({(count/total)*100:.1f}%)")

if __name__ == "__main__":
    process_companies_in_batches(
        input_file='data.xlsx',
        output_file='mined_company_data.xlsx',
        start_index=0,  # Start from the beginning
        batch_size=50,  # Process 100 companies at a time
        total_limit=None  # Process all companies (or set a limit)
    )