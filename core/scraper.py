import json
import logging
import re
from bs4 import BeautifulSoup
import requests
import tldextract
from random import uniform, choice
from urllib.parse import urljoin, urlparse
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.scraping_config import ScrapingConfig
from core.contact_extractor import ContactExtractor
from managers.selenium_manager import SeleniumManager
from utils.validators import ContactValidators
from utils.url_utils import UrlUtils


class CompanyScraper:
    """Enhanced scraper with improved contact information extraction"""
    def __init__(self):
        self.config = ScrapingConfig()
        self.selenium_manager = SeleniumManager()
        self.contact_extractor = ContactExtractor()
        self.contact_validator = ContactValidators()
        self.url_validator = UrlUtils()
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
                    if self.url_validator.is_valid_url(href):
                        return href
            return None
        except Exception as e:
            logging.error(f"Directory extraction error: {str(e)}")
            return None



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
            delay = self.config.BASE_DELAY + uniform(0.01, 0.1)
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
        """Enhanced contact page discovery with improved page relevance scoring"""
        contact_pages = set()
        
        # First check if current page has contact section
        main_page_score = self._evaluate_page_contact_relevance(soup)
        if main_page_score > 0.6:  # High confidence threshold
            contact_pages.add(base_url)
        
        # Search in primary navigation areas with priority scoring
        nav_areas = {
            'header': soup.find_all(['header', 'nav']),
            'footer': soup.find_all('footer'),
            'main-nav': soup.find_all(class_=re.compile(r'(main|primary|global)-nav', re.I))
        }
        
        for area_type, elements in nav_areas.items():
            for element in elements:
                self._extract_contact_links(element, base_url, contact_pages)
        
        # Check structured data for contact pages
        self._extract_structured_contact_pages(soup, base_url, contact_pages)
        
        # Search in sitemaps with improved parsing
        sitemap_links = soup.find_all('a', href=re.compile(r'sitemap', re.I))
        for link in sitemap_links:
            try:
                sitemap_url = urljoin(base_url, link['href'])
                sitemap_response = self._make_request(sitemap_url)
                if sitemap_response:
                    sitemap_soup = BeautifulSoup(sitemap_response.text, 'html.parser')
                    self._process_sitemap_content(sitemap_soup, base_url, contact_pages)
            except Exception as e:
                logging.error(f"Sitemap processing error: {str(e)}")
        
        # Additional search in common contact page locations
        self._search_common_contact_locations(base_url, contact_pages)
        
        # Sort pages by relevance score
        scored_pages = [(page, self._score_contact_page(page)) for page in contact_pages]
        sorted_pages = sorted(scored_pages, key=lambda x: x[1], reverse=True)
        
        # Return top 3 most relevant contact pages
        return [page for page, score in sorted_pages[:3]]

    def _evaluate_page_contact_relevance(self, soup):
        """
        Evaluate how likely a page contains contact information
        Returns a score between 0 and 1
        """
        score = 0
        max_score = 7  # Total possible points
        
        # Check for contact-specific sections
        contact_sections = soup.find_all(['div', 'section'], class_=re.compile(
            r'contact|connect|reach|touch|location', re.I))
        if contact_sections:
            score += 1
        
        # Check for contact form presence
        contact_forms = soup.find_all('form', class_=re.compile(r'contact|enquiry|message', re.I))
        if contact_forms:
            score += 1
        
        # Check for business hours or location information
        if soup.find_all(string=re.compile(r'(business|opening|office)\s*hours|location|address', re.I)):
            score += 1
        
        # Check for social media links section
        social_section = soup.find_all(['div', 'ul'], class_=re.compile(r'social|follow', re.I))
        if social_section:
            score += 0.5
        
        # Check for contact information patterns
        text_content = soup.get_text()
        if any(re.search(pattern, text_content) for pattern in self.contact_extractor.email_patterns):
            score += 1.5
        if any(re.search(pattern, text_content) for pattern in self.contact_extractor.phone_patterns):
            score += 1.5
        
        # Check for embedded maps
        if soup.find_all(['iframe', 'div'], class_=re.compile(r'map|location', re.I)):
            score += 0.5
        
        return score / max_score

    def _extract_structured_contact_pages(self, soup, base_url, contact_pages):
        """Extract contact pages from structured data and metadata"""
        # Check JSON-LD data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                contact_url = self._extract_contact_from_jsonld(data)
                if contact_url:
                    contact_pages.add(urljoin(base_url, contact_url))
            except:
                continue
        
        # Check meta tags
        meta_tags = soup.find_all('meta', attrs={'name': re.compile(r'contact|email', re.I)})
        for tag in meta_tags:
            content = tag.get('content', '')
            if content.startswith(('http://', 'https://', '/')):
                contact_pages.add(urljoin(base_url, content))

    def _process_sitemap_content(self, sitemap_soup, base_url, contact_pages):
        """Process sitemap content with improved contact page detection"""
        # Process XML sitemaps
        urls = sitemap_soup.find_all(['url', 'loc'])  # Handle both XML sitemap and HTML sitemap
        for url in urls:
            url_text = url.get_text().lower()
            if any(term in url_text for term in self.config.CONTACT_PATHS):
                if self.url_validator.is_valid_url(url_text):
                    contact_pages.add(url_text)
        
        # Process HTML sitemaps
        links = sitemap_soup.find_all('a', href=True)
        for link in links:
            href = link['href'].lower()
            text = link.get_text().lower()
            if any(term in href or term in text for term in self.config.CONTACT_PATHS):
                full_url = urljoin(base_url, link['href'])
                if self.url_validator.is_valid_url(full_url):
                    contact_pages.add(full_url)

    def _search_common_contact_locations(self, base_url, contact_pages):
        """Search for contact pages in common URL patterns"""
        common_paths = [
            '/contact', '/contact-us', '/contactus', '/connect', 
            '/reach-us', '/reach', '/get-in-touch', '/about/contact',
            '/support/contact', '/help/contact', '/locations'
        ]
        
        for path in common_paths:
            potential_url = urljoin(base_url, path)
            try:
                response = self._make_request(potential_url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Verify it's actually a contact page
                    if self._evaluate_page_contact_relevance(soup) > 0.4:
                        contact_pages.add(potential_url)
            except Exception as e:
                logging.debug(f"Error checking common path {path}: {str(e)}")
                continue

    def _score_contact_page(self, url):
        """
        Score contact page relevance based on URL structure
        Returns a score between 0 and 1
        """
        score = 0
        url_lower = url.lower()
        
        # Direct contact page indicators
        if '/contact' in url_lower:
            score += 0.8
        elif any(term in url_lower for term in ['reach', 'touch', 'connect']):
            score += 0.6
        elif '/about' in url_lower:
            score += 0.4
        elif '/support' in url_lower or '/help' in url_lower:
            score += 0.5
        
        # Penalize deep paths
        path_depth = url.count('/') - 2  # Subtract 2 for http://
        if path_depth > 2:
            score -= 0.1 * (path_depth - 2)
        
        # Normalize score
        return max(0, min(1, score))


    def _extract_contact_links(self, element, base_url, contact_pages):
        """Extract contact page links from element"""
        for anchor in element.find_all('a', href=True):
            href = anchor['href'].lower()
            text = anchor.get_text().lower()

            # Check both href and text for contact-related terms
            if any(path in href or path in text for path in self.config.CONTACT_PATHS):
                full_url = urljoin(base_url, anchor['href'])
                if self.url_validator.is_valid_url(full_url):
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
                        if self.contact_validator._validate_email(email):
                            contact_info['email'] = email
                            break
                            
            if not contact_info['phone']:
                # Search for phone patterns in JavaScript variables
                for pattern in self.contact_extractor.phone_patterns:
                    matches = re.finditer(pattern, script_content)
                    for match in matches:
                        phone = match.group(0)
                        if self.contact_validator._validate_phone(phone):
                            contact_info['phone'] = self.contact_validator._format_phone(phone)
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
                    if isinstance(value, str) and self.contact_validator._validate_email(value):
                        contact_info['email'] = value
                        
                if 'phone' in key_lower or 'tel' in key_lower:
                    if isinstance(value, str) and self.contact_validator._validate_phone(value):
                        contact_info['phone'] = self.contact_validator._format_phone(value)
                        
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
                if self.contact_validator._validate_phone(phone):
                    contact_info['phone'] = self.contact_validator._format_phone(phone)
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
            if self.contact_validator._validate_email(email):
                contact_info['email'] = email
                break

        # Check for tel links
        phone_links = element.find_all('a', href=re.compile(r'tel:', re.I))
        for link in phone_links:
            phone = link.get('href', '').replace('tel:', '').strip()
            if self.contact_validator._validate_phone(phone):
                contact_info['phone'] = self.contact_validator._format_phone(phone)
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
                        if self.contact_validator._validate_email(email):
                            contact_info['email'] = email
                            break
            
            # Extract phone if not found yet
            if not contact_info['phone']:
                for pattern in self.contact_extractor.phone_patterns:
                    matches = re.finditer(pattern, text_content)
                    for match in matches:
                        phone = match.group(0)
                        if self.contact_validator._validate_phone(phone):
                            contact_info['phone'] = self.contact_validator._format_phone(phone)
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
                    if self.contact_validator._validate_email(email):
                        contact_info['email'] = email
                        break

        # Extract phone if not found yet
        if not contact_info['phone']:
            for pattern in self.contact_extractor.phone_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    phone = match.group(0)
                    if self.contact_validator._validate_phone(phone):
                        contact_info['phone'] = self.contact_validator._format_phone(phone)
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
                            if pattern_type == 'email' and self.contact_validator._validate_email(extracted):
                                contact_info['email'] = extracted
                                break
                            elif pattern_type == 'phone' and self.contact_validator._validate_phone(extracted):
                                contact_info['phone'] = self.contact_validator._format_phone(extracted)
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
                    if self.contact_validator._validate_email(email):
                        contact_info['email'] = email

            if not contact_info['phone']:
                phone_elem = element.find(itemprop='telephone')
                if phone_elem:
                    phone = phone_elem.get('content', phone_elem.get_text())
                    if self.contact_validator._validate_phone(phone):
                        contact_info['phone'] = self.contact_validator._format_phone(phone)


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