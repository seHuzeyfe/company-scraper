import re

class ContactValidators:
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