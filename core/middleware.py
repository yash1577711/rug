# core/middleware.py
from ipware import get_client_ip
import requests
from django.utils.deprecation import MiddlewareMixin

class CurrencyDetectionMiddleware(MiddlewareMixin):  # ✅ Keep this name
    def process_request(self, request):
        # Get client IP
        client_ip, is_routable = get_client_ip(request)
        
        # Default currency
        detected_currency = 'INR'
        
        if client_ip and client_ip != '127.0.0.1':
            try:
                # Use ipapi.co for free IP geolocation
                response = requests.get(f'https://ipapi.co/{client_ip}/json/', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    country_code = data.get('country_code', 'IN')
                    detected_currency = 'USD' if country_code != 'IN' else 'INR'
            except:
                detected_currency = 'INR'
        
        # Store in session (auto-detected)
        if not request.session.get('manual_currency'):
            request.session['detected_currency'] = detected_currency
        
        # Use manual currency if set, otherwise use detected
        request.currency = request.session.get('manual_currency', request.session.get('detected_currency', 'INR'))