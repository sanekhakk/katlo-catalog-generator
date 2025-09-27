from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
import requests
from .models import WhatsAppCatalogue
from .scraper import WhatsAppCatalogueScraper
import logging

logger = logging.getLogger(__name__)

@staff_member_required
def debug_catalogue_url(request, catalogue_id):
    """
    Debug endpoint to test URL accessibility and structure
    """
    catalogue = get_object_or_404(WhatsAppCatalogue, id=catalogue_id)
    
    debug_info = {
        'catalogue_name': catalogue.name,
        'url': catalogue.url,
        'url_accessible': False,
        'url_type': 'unknown',
        'response_status': None,
        'content_type': None,
        'page_title': None,
        'has_structured_data': False,
        'product_indicators': [],
        'recommendations': []
    }
    
    try:
        scraper = WhatsAppCatalogueScraper()
        
        # Determine URL type
        url_type = scraper._determine_url_type(catalogue.url)
        debug_info['url_type'] = url_type
        
        # Provide recommendations based on URL type
        if url_type == 'wa_me':
            debug_info['recommendations'] = [
                "This is a WhatsApp chat link (wa.me), not a product catalogue.",
                "WhatsApp chat links cannot be scraped for product data.",
                "Please provide a website URL that displays products publicly.",
                "Consider using the business's website or e-commerce store instead."
            ]
            return JsonResponse(debug_info)
        
        # Try to fetch the URL
        try:
            response = scraper._fetch_page(catalogue.url)
            if response:
                debug_info['url_accessible'] = True
                debug_info['response_status'] = response.status_code
                debug_info['content_type'] = response.headers.get('content-type', 'unknown')
                
                # Extract basic page info
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get page title
                title_tag = soup.find('title')
                if title_tag:
                    debug_info['page_title'] = title_tag.get_text().strip()
                
                # Check for structured data
                json_scripts = soup.find_all('script', type='application/ld+json')
                debug_info['has_structured_data'] = len(json_scripts) > 0
                
                # Look for product indicators
                product_indicators = []
                
                # Check for price patterns
                import re
                price_pattern = r'[$₹€£¥]\s*\d+|\d+\s*[$₹€£¥]'
                price_matches = re.findall(price_pattern, response.text)
                if price_matches:
                    product_indicators.append(f"Found {len(price_matches)} price patterns")
                
                # Check for common product selectors
                product_selectors = [
                    '.product', '.product-item', '.product-card',
                    '[data-product]', '.catalogue-item',
                    'h3', 'h2'  # Potential product titles
                ]
                
                for selector in product_selectors:
                    elements = soup.select(selector)
                    if elements:
                        product_indicators.append(f"Found {len(elements)} elements with selector '{selector}'")
                
                debug_info['product_indicators'] = product_indicators
                
                # Provide recommendations
                recommendations = []
                
                if not price_matches:
                    recommendations.append("No price information detected on this page")
                
                if not any('product' in indicator.lower() for indicator in product_indicators):
                    recommendations.append("No obvious product structure detected")
                
                if not debug_info['has_structured_data']:
                    recommendations.append("No structured data (JSON-LD) found - scraping will rely on HTML parsing")
                
                if not recommendations:
                    recommendations.append("Page appears to contain product information and should be scrapeable")
                
                debug_info['recommendations'] = recommendations
                
            else:
                debug_info['recommendations'] = [
                    "URL is not accessible - this could be due to:",
                    "1. Private/protected content that requires login",
                    "2. Geographic restrictions or blocking",
                    "3. Invalid or expired URL",
                    "4. Server or network issues"
                ]
        
        except Exception as e:
            debug_info['error'] = str(e)
            debug_info['recommendations'] = [
                f"Error accessing URL: {str(e)}",
                "Please verify the URL is correct and publicly accessible"
            ]
    
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['recommendations'] = [f"Debug error: {str(e)}"]
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})

@staff_member_required 
def test_sample_data(request, catalogue_id):
    """
    Test endpoint to create sample data for a catalogue
    """
    try:
        from .scraper import scrape_whatsapp_catalogue
        
        scrape_log = scrape_whatsapp_catalogue(catalogue_id, use_sample_data=True)
        
        if scrape_log:
            return JsonResponse({
                'success': True,
                'message': 'Sample data created successfully',
                'data': {
                    'products_found': scrape_log.products_found,
                    'products_added': scrape_log.products_added,
                    'products_updated': scrape_log.products_updated,
                    'status': scrape_log.status
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to create sample data'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating sample data: {str(e)}'
        })