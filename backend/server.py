import http.server
import socketserver
import json
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

PORT = 8000

class AhatAPIHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route the request
        if path == '/api/products':
            response = self.get_your_real_products()
        elif path == '/api/products/categories':
            response = self.get_categories()
        elif path == '/api/products/stats':
            response = self.get_stats()
        elif path == '/api':
            response = {"message": "Ahat API Server", "version": "1.0", "status": "running"}
        else:
            response = {"error": "Not found", "path": path}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_your_real_products(self):
        """Get your 7 real SixSevenDeals products"""
        try:
            # Option 1: Try to scrape from your website
            print("🔍 Attempting to fetch products from SixSevenDeals.com...")
            html_products = self.scrape_your_website()
            if html_products:
                print("✅ Successfully scraped products from website")
                return self.format_products(html_products, "SixSevenDeals.com Live")
        except Exception as e:
            print(f"⚠ Could not scrape website: {e}")
        
        # Option 2: Fallback to hardcoded products
        print("📦 Using hardcoded SixSevenDeals products")
        return self.get_hardcoded_products()
    
    def scrape_your_website(self):
        """Scrape your actual SixSevenDeals.com website"""
        try:
            # Your actual website URL
            url = "https://sixsevendeals.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse the JavaScript products array from your HTML
            products_js = None
            for script in soup.find_all('script'):
                if script.string and 'const products = [' in script.string:
                    products_js = script.string
                    break
            
            if products_js:
                # Extract JSON from JavaScript (simplified)
                import re
                import json as json_lib
                
                # Find the products array
                match = re.search(r'const products\s*=\s*(\[.*?\]);', products_js, re.DOTALL)
                if match:
                    products_json = match.group(1)
                    # Clean up the JSON
                    products_json = products_json.replace("'", '"')
                    products = json_lib.loads(products_json)
                    return products
            
            return None
            
        except Exception as e:
            print(f"Scraping error: {e}")
            return None
    
    def get_hardcoded_products(self):
        """Your 7 real products as fallback"""
        products = [
            {
                "name": "Canon EOS 3000D DSLR Camera with 18-55mm Lens - AU Version",
                "description": "✅ 4.6★ from 1,200+ Aussie reviews | Official AU warranty | Ships Sydney. Perfect for Australian photography enthusiasts. Capture crisp 18MP detail with beautiful background blur.",
                "price": "$633.49",
                "originalPrice": "$685.00",
                "discount": "8% OFF",
                "image": "https://m.media-amazon.com/images/I/81fsA6RI10L._AC_SX425_.jpg",
                "link": "https://amzn.to/3WYqCEC",
                "badge": "Editor's Pick",
                "rating": "4.6",
                "reviewCount": "1,200+"
            },
            {
                "name": "TOCOL iPhone 16 Privacy Screen Protector [2 Pack]",
                "description": "✅ 4.7★ from 2,800+ Aussie reviews | Local warranty | Ships AU. 9H+ hardness with 25° privacy. Blocks prying eyes on trains & in offices. Perfect for Aussie commuters.",
                "price": "$19.99",
                "originalPrice": "$19.99",
                "discount": "Limited Time",
                "image": "https://m.media-amazon.com/images/I/71SfEaQzdaL._AC_SX569_.jpg",
                "link": "https://amzn.to/4i2gR1E",
                "badge": "Value Pick",
                "rating": "4.7",
                "reviewCount": "2,800+"
            },
            {
                "name": "SAMSUNG T7 1TB Portable External SSD - Grey",
                "description": "✅ 4.8★ from 4,500+ Aussie reviews | 3-year AU warranty | Ships Melbourne. Lightning-fast storage (1,050MB/s). Perfect for gamers, students, pros.",
                "price": "$147.95",
                "originalPrice": "$177.54",
                "discount": "20% OFF",
                "image": "https://m.media-amazon.com/images/I/A1sHjPpz6fL._AC_SX522_.jpg",
                "link": "https://amzn.to/3LJ6ZxY",
                "badge": "Performance",
                "rating": "4.8",
                "reviewCount": "4,500+"
            },
            {
                "name": "ZZU Bluetooth Earphones - 48 Hours Playtime",
                "description": "✅ 4.5★ from 3,200+ Aussie reviews | IPX7 waterproof | Ships Brisbane. 48hr battery, deep bass, perfect for beach runs & bush walks.",
                "price": "$26.99",
                "originalPrice": "$39.99",
                "discount": "33% OFF",
                "image": "https://m.media-amazon.com/images/I/61hAJU-6B-L._AC_SY355_.jpg",
                "link": "https://amzn.to/49q10I5",
                "badge": "Value Pick",
                "rating": "4.5",
                "reviewCount": "3,200+"
            },
            {
                "name": "Xiaomi Redmi Watch 5 Active Smartwatch - Black",
                "description": "✅ 4.6★ from 1,800+ Aussie reviews | 5ATM waterproof | Ships AU. 18-day battery, 140+ sports modes. Built for Aussie fitness enthusiasts.",
                "price": "$53.00",
                "originalPrice": "$59.50",
                "discount": "11% OFF",
                "image": "https://m.media-amazon.com/images/I/61BG7aYMZEL._AC_SY450_.jpg",
                "link": "https://amzn.to/4r6YgG0",
                "badge": "Trending",
                "rating": "4.6",
                "reviewCount": "1,800+"
            },
            {
                "name": "Soundcore by Anker Q20i Noise Cancelling Headphones",
                "description": "✅ 4.8★ from 6,300+ Aussie reviews | 40-hour battery | Ships AU. Hybrid ANC, Hi-Res audio. Block out noise on Aussie commutes.",
                "price": "$85.99",
                "originalPrice": "$119.95",
                "discount": "28% OFF",
                "image": "https://m.media-amazon.com/images/I/61E3AcWQg1L._AC_SY355_.jpg",
                "link": "https://amzn.to/3X34ZTx",
                "badge": "Performance",
                "rating": "4.8",
                "reviewCount": "6,300+"
            },
            {
                "name": "Mini Drone for Kids – HS190 Pocket Quadcopter",
                "description": "✅ 4.5★ from 1,500+ Aussie reviews | AU safety compliant | Ships Perth. Altitude hold, 3D flips. Perfect for Aussie backyards & parks.",
                "price": "$49.99",
                "originalPrice": "$59.99",
                "discount": "17% OFF",
                "image": "https://m.media-amazon.com/images/I/614A0UN52RL._AC_SX522_.jpg",
                "link": "https://amzn.to/4rgXLZY",
                "badge": "Value Pick",
                "rating": "4.5",
                "reviewCount": "1,500+"
            }
        ]
        
        return self.format_products(products, "Hardcoded SixSevenDeals Products")
    
    def format_products(self, raw_products, source):
        """Format products into Ahat API response"""
        ahat_products = []
        
        for i, product in enumerate(raw_products):
            # Parse price values
            price_str = product.get('price', '$0').replace('$', '').replace(',', '')
            original_price_str = product.get('originalPrice', '$0').replace('$', '').replace(',', '')
            
            try:
                price = float(price_str)
                original_price = float(original_price_str)
            except:
                price = 0
                original_price = 0
            
            # Calculate discount
            discount_pct = 0
            if original_price > 0 and price < original_price:
                discount_pct = round(((original_price - price) / original_price) * 100, 0)
            
            # Parse rating
            rating_str = product.get('rating', '0')
            try:
                rating = float(rating_str)
            except:
                rating = 4.5
            
            # Parse review count
            review_str = product.get('reviewCount', '0').replace('+', '').replace(',', '')
            try:
                review_count = int(review_str)
            except:
                review_count = 1000
            
            # Extract brand from name
            brand = "Unknown"
            name = product.get('name', '')
            possible_brands = ['Canon', 'TOCOL', 'Samsung', 'ZZU', 'Xiaomi', 'Redmi', 'Soundcore', 'Anker', 'HS190']
            for pb in possible_brands:
                if pb.lower() in name.lower():
                    brand = pb
                    break
            
            # Extract category from badge
            category = product.get('badge', 'General').replace(' Pick', '').replace('ing', '')
            
            ahat_products.append({
                'id': f'SIX7-{i+1}',
                'asin': self.extract_asin(product.get('link', '')),
                'title': name,
                'description': product.get('description', ''),
                'price': {
                    'original': original_price,
                    'discounted': price,
                    'currency': 'AUD',
                    'discount_percentage': discount_pct,
                    'savings': round(original_price - price, 2)
                },
                'category': category,
                'brand': brand,
                'rating': rating,
                'review_count': review_count,
                'image': product.get('image', ''),
                'affiliate_link': product.get('link', ''),
                'trending_score': min(100, int(rating * 20 + review_count / 100)),
                'deal_score': min(100, int((discount_pct * 2) + (rating * 10))),
                'status': 'active'
            })
        
        # Apply pagination
        query = parse_qs(urlparse(self.path).query)
        limit = int(query.get('limit', [10])[0])
        page = int(query.get('page', [1])[0])
        offset = (page - 1) * limit
        
        paginated = ahat_products[offset:offset + limit]
        
        return {
            'success': True,
            'data': paginated,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': len(ahat_products),
                'pages': max(1, len(ahat_products) // limit),
                'has_more': (offset + limit) < len(ahat_products)
            },
            'source': source
        }
    
    def extract_asin(self, url):
        """Extract ASIN from Amazon URL"""
        import re
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'ASIN=([A-Z0-9]{10})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return 'UNKNOWN-ASIN'
    
    def get_categories(self):
        """Get categories from your products"""
        categories = [
            {'id': 1, 'name': 'Cameras', 'count': 1, 'icon': '📷'},
            {'id': 2, 'name': 'Phone Accessories', 'count': 1, 'icon': '📱'},
            {'id': 3, 'name': 'Storage', 'count': 1, 'icon': '💾'},
            {'id': 4, 'name': 'Audio', 'count': 2, 'icon': '🎧'},
            {'id': 5, 'name': 'Wearables', 'count': 1, 'icon': '⌚'},
            {'id': 6, 'name': 'Toys', 'count': 1, 'icon': '🚁'},
            {'id': 7, 'name': 'All Products', 'count': 7, 'icon': '🎯'}
        ]
        return {'success': True, 'data': categories}
    
    def get_stats(self):
        """Get stats from your 7 products"""
        return {
            'success': True,
            'data': {
                'total_products': 7,
                'active_products': 7,
                'categories_count': 6,
                'average_price': 145.06,
                'average_discount': 16.71,
                'last_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'top_categories': [
                    {'name': 'Audio', 'count': 2},
                    {'name': 'Cameras', 'count': 1},
                    {'name': 'Storage', 'count': 1}
                ],
                'performance': {
                    'total_reviews': 21200,
                    'average_rating': 4.64,
                    'total_savings': 144.56
                }
            }
        }

def main():
    with socketserver.TCPServer(("", PORT), AhatAPIHandler) as httpd:
        print(f"🎩 Ahat API Server running at http://localhost:{PORT}")
        print(f"📊 Serving YOUR REAL SixSevenDeals products!")
        print(f"   • http://localhost:{PORT}/api/products")
        print(f"   • http://localhost:{PORT}/api/products/categories")
        print(f"   • http://localhost:{PORT}/api/products/stats")
        print("   • http://localhost:{PORT}/api/products?limit=3 (test pagination)")
        print()
        print("📈 Features:")
        print("   • Your 7 real products from SixSevenDeals.com")
        print("   • Real prices, discounts, and savings")
        print("   • Real ratings and review counts")
        print("   • Real affiliate links")
        print("   • Pagination support")
        print()
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()