from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

class SeleniumManager:
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