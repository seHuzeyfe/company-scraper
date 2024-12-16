class ContactExtractor:
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
            \.[a-zA-Z]{2,})''',

        # URI encoded email pattern
        r'''(?x)
        (?:%[0-9A-Fa-f]{2})+          # URI encoded characters
        %40                            # @ symbol (URI encoded)
        (?:%[0-9A-Fa-f]{2})+          # Domain part (URI encoded)
        ''',
        
        # JavaScript encoded email pattern
        r'''(?x)
        (?:unescape\(|decodeURIComponent\()  # JavaScript decode functions
        ['"]                                 # Quote
        (?:%[0-9A-Fa-f]{2}|\\x[0-9A-Fa-f]{2})+ # Encoded email
        ['"]                                 # Closing quote
        \)                                   # Closing parenthesis
        ''',
        
        # Base64 encoded email pattern
        r'''(?x)
        (?:^|[^a-zA-Z0-9+/])          # Not part of another base64 string
        ([a-zA-Z0-9+/]{4})*           # Base64 chunks of 4
        ([a-zA-Z0-9+/]{4}|            # Either complete chunk
        [a-zA-Z0-9+/]{3}=|            # or 3 chars + 1 pad
        [a-zA-Z0-9+/]{2}==)           # or 2 chars + 2 pad
        (?:[^a-zA-Z0-9+/]|$)          # End of base64 string
        '''

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
            ''',
        # Asian phone format (China, Japan, Korea)
        r'''(?x)
        (?:
            (?:\+?86|0086)\s*          # China
            (?:
                1[3-9]\d{9}|           # Mobile
                [2-9][1-9]\d{8}        # Landline
            )
            |
            (?:\+?81|0081)\s*          # Japan
            (?:
                [789]0\d{8}|           # Mobile
                \d{2,4}\d{7,8}         # Landline
            )
            |
            (?:\+?82|0082)\s*          # Korea
            (?:
                1[0-9]{8,9}|           # Mobile
                2\d{7,8}|              # Seoul
                [3-6]\d{8}             # Other regions
            )
        )
        ''',
        
        # Middle Eastern format
        r'''(?x)
        (?:
            (?:\+?9[0-9][0-9]|009[0-9][0-9])\s*  # Country codes 90-99
            [1-9]\d{8,11}                         # Rest of number
        )
        ''',
        
        # VoIP and special numbers
        r'''(?x)
        (?:
            (?:sip|tel):[+]?                      # SIP/TEL protocol
            (?:[0-9]{8,20})                       # Number
            (?:;ext=[0-9]{2,5})?                  # Extension
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
            ],
            
        'rdfa': {
            # RDFa patterns
            'contact': [
                r'typeof="schema:ContactPoint"[^>]*>(.*?)</\w+>',
                r'property="schema:contactPoint"[^>]*>(.*?)</\w+>'
            ]
        }

        }