from datetime import timedelta
from fake_useragent import UserAgent

class ScrapingConfig:
    """Enhanced configuration settings for the scraper"""
    def __init__(self):

        self.CACHE_DIR = 'cache'
        self.CACHE_DURATION = timedelta(days=7)
        self.MAX_RETRIES = 2
        self.BASE_DELAY = 0.05
        self.MAX_WORKERS = 12
        self.TIMEOUT = 5
        self.USER_AGENTS = self._load_user_agents()
        self.SEARCH_ENGINES = [
            ('https://www.google.com/search?q={}', 'div.g'), # Google
            ('https://www.bing.com/search?q={}', 'li.b_algo'),  # Bing
            #('https://duckduckgo.com/?q={}', 'div.result__body'),  # DuckDuckGo
            #('https://www.ecosia.org/search?q={}', 'a.result-title'),  # Ecosia
            #('https://search.yahoo.com/search?p={}', 'div.Sr'),  # Yahoo
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

        'turkish': [
            'iletisim', 'bize-ulasin', 'bizimle-iletisime-gecin', 'destek',
            'musteri-hizmetleri', 'iletisim-formu', 'bize-yazin', 'kunye',
            'firma-iletisim', 'kurumsal-iletisim', 'hakkimizda/iletisim',
            'bayi-iletisim', 'merkez-iletisim', 'genel-merkez'
        ],
        
        'russian': [
            'kontakty', 'svyaz', 'o-nas/kontakty', 'podderzhka',
            'obratnaya-svyaz', 'napisat-nam', 'sluzhba-podderzhki',
            'pomoshch', 'kontaktnaya-informatsiya', 'svyazatsya-s-nami'
        ],
        
        'chinese': [
            'lian-xi-wo-men', 'guan-yu-wo-men', 'ke-fu-zhong-xin',
            'bang-zhu-zhong-xin', 'lian-xi-fang-shi', 'jiu-zhu'
        ],
        
        'japanese': [
            'otoiawase', 'contact-jp', 'support-jp', 'help-jp',
            'o-toiawase', 'contact-japan', 'support-japan'
        ],
        
        'korean': [
            'munui', 'munuihagi', 'contact-kr', 'support-kr',
            'gokaek-sente', 'contact-korea', 'support-korea'
        ],
        
        'arabic': [
            'ittisal', 'tawasol-maana', 'contact-ar', 'support-ar',
            'musaeada', 'aldaem', 'contact-arabic'
        ],
        
        'common_variations': [
            'contact-info', 'contact-information', 'business-contact',
            'corporate-contact', 'global-contact', 'sales-contact',
            'office-contact', 'headquarters-contact', 'branch-contact',
            'regional-contact', 'international-contact', 'local-contact',
            'contact-details', 'contact-directory', 'contact-locations',
            'contact-addresses', 'general-contact', 'main-contact'
        ],
        
        'industry_specific': [
            'dealer-contact', 'supplier-contact', 'vendor-contact',
            'distributor-contact', 'partner-contact', 'reseller-contact',
            'wholesaler-contact', 'manufacturer-contact', 'factory-contact',
            'industrial-contact', 'commercial-contact', 'retail-contact'
        ],
        
        'url_patterns': [
            'contact.*/.*html?', 'about.*/.*contact.*', '.*/contact$',
            '.*/contact-.*', '.*/.*-contact', '.*/reach-.*', '.*/connect.*',
            'help.*/contact.*', 'support.*/contact.*', '.*/enquiry.*',
            '.*/inquiry.*', '.*/feedback.*', '.*/support.*'
        ],
        
        'subdomain_patterns': [
            'contact.', 'support.', 'help.', 'info.',
            'customerservice.', 'cs.', 'enquiry.', 'feedback.'
        ],
        
        'dynamic_paths': [
            'contact/[0-9]+', 'contact/[a-z]{2}', 'contact/[a-z]{2}-[a-z]{2}',
            'contact/region/[a-z]+', 'contact/office/[a-z]+',
            'contact/department/[a-z]+', 'support/[a-z]+/contact'
        ],
        
        'special_cases': [
            '^\/$contact', '^\/.*#contact', '^\/.*#reach-us',
            '^\/.*#get-in-touch', '^\/.*#connect', '^\/.*#support',
            'contact\?.*', 'support\?.*', 'help\?.*'
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