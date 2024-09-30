import requests
import urllib3
import sys

print(f"Python version: {sys.version}")
print(f"requests version: {requests.__version__}")
print(f"urllib3 version: {urllib3.__version__}")

try:
    from pytrends.request import TrendReq
    print("pytrends is successfully imported")
except ImportError:
    print("pytrends is not installed or cannot be imported")
    sys.exit(1)

from requests.auth import HTTPProxyAuth
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
from datetime import datetime, timedelta
import time
import random
import csv
from tqdm import tqdm
import re

# Suppress only the single InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of proxies
PROXIES = [
    'http://ba13396172373555b0b863c3af19140fdda923d662584dc9620401ee0ccbe2f66f6e34452a1b8324a28115027daf1439-country-us-const-session-cdf5f:25eb72i179pk@proxy.oculus-proxy.com:31115',
    'http://ba13396172373555b0b863c3af19140fdda923d662584dc9620401ee0ccbe2f66f6e34452a1b8324a28115027daf1439-country-us-const-session-cdf60:25eb72i179pk@proxy.oculus-proxy.com:31115',
    'http://ba13396172373555b0b863c3af19140fdda923d662584dc9620401ee0ccbe2f66f6e34452a1b8324a28115027daf1439-country-us-const-session-cdf61:25eb72i179pk@proxy.oculus-proxy.com:31115',
    'http://ba13396172373555b0b863c3af19140fdda923d662584dc9620401ee0ccbe2f66f6e34452a1b8324a28115027daf1439-country-us-const-session-cdf62:25eb72i179pk@proxy.oculus-proxy.com:31115',
    'http://ba13396172373555b0b863c3af19140fdda923d662584dc9620401ee0ccbe2f66f6e34452a1b8324a28115027daf1439-country-us-const-session-cdf63:25eb72i179pk@proxy.oculus-proxy.com:31115'
]

def get_next_proxy():
    return random.choice(PROXIES)

def create_pytrends_object(proxy=None):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # Create a session
    session = requests.Session()
    
    if proxy:
        # Parse the proxy URL
        parsed_proxy = urlparse(proxy)
        proxy_host = f"{parsed_proxy.scheme}://{parsed_proxy.hostname}:{parsed_proxy.port}"
        proxy_auth = HTTPProxyAuth(parsed_proxy.username, parsed_proxy.password)
        
        # Set up the proxy
        session.proxies = {
            'http': proxy_host,
            'https': proxy_host
        }
        session.auth = proxy_auth
    
    # Set up the session headers
    session.headers.update({'User-Agent': user_agent})
    
    # Create TrendReq object with the custom session
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(30,60), requests_args={'verify':False})
    
    # Manually set the session for pytrends
    pytrends.requests = session
    
    return pytrends

def get_with_retries(pytrends, query, timeframe, retries=5, backoff_factor=0.1):
    for i in range(retries):
        try:
            pytrends.build_payload([query], timeframe=timeframe)
            return pytrends.interest_over_time()
        except requests.exceptions.RequestException as e:
            if i == retries - 1:  # last attempt
                raise
            time.sleep(backoff_factor * (2 ** i))  # exponential backoff
    return None

def sanitize_query(query):
    # Remove special characters and limit length
    return re.sub(r'[^a-zA-Z0-9\s]', '', query)[:100]

def detect_spike(trend_data):
    if len(trend_data) < 14:  # Require two weeks of data
        return 0

    try:
        # Calculate very short-term average (last 2 days)
        very_short_term_avg = sum(trend_data[-2:]) / 2

        # Calculate short-term average (last 5 days)
        short_term_avg = sum(trend_data[-5:]) / 5

        # Calculate medium-term average (last 14 days)
        medium_term_avg = sum(trend_data[-14:]) / 14

        # Calculate the spike ratios
        spike_ratio_short = very_short_term_avg / (short_term_avg + 1)
        spike_ratio_medium = very_short_term_avg / (medium_term_avg + 1)

        # Calculate spike percentages
        spike_percentage_short = (spike_ratio_short - 1) * 100
        spike_percentage_medium = (spike_ratio_medium - 1) * 100

        # Return the larger of the two spike percentages
        return max(spike_percentage_short, spike_percentage_medium, 0)

    except Exception as e:
        print(f"Error in detect_spike: {str(e)}")
        return 0

def get_trending_searches():
    proxy = get_next_proxy()
    pytrends = create_pytrends_object(proxy)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    timeframe = f'{start_date.strftime("%Y-%m-%d")} {end_date.strftime("%Y-%m-%d")}'

    trending_searches = set()  # Use a set to avoid duplicates

    # Expanded and new categories with more diverse search terms
    category_searches = {

  "Home Decor": ["Wall Art", "Throw Pillows", "Candles", "Smart Lighting"],
  "Fitness & Wellness": ["Yoga Mats", "Resistance Bands", "Home Workout Equipment", "Massage Guns"],
  "Beauty & Skincare": ["Face Masks", "Serums", "Natural Haircare", "Makeup Brushes"],
  "Tech Accessories": ["Wireless Chargers", "Bluetooth Speakers", "Phone Cases", "Smart Watches"],
  "Sustainable Products": ["Reusable Water Bottles", "Bamboo Toothbrushes", "Eco-friendly Cleaning Supplies", "Solar Chargers"],
  "Pet Products": ["Pet Beds", "Automatic Feeders", "Pet Grooming Kits", "Interactive Pet Toys"],
  "Outdoor & Camping": ["Portable Grills", "Camping Tents", "Hiking Backpacks", "Survival Kits"],
  "Health & Nutrition": ["Protein Powders", "Keto Snacks", "Herbal Supplements", "Health Trackers"],
  "Fashion & Apparel": ["Athleisure Wear", "Minimalist Jewelry", "Streetwear", "Sustainable Fashion"],
  "Kitchen Gadgets": ["Air Fryers", "Reusable Food Wraps", "Coffee Grinders", "Meal Prep Containers"],
  "Baby & Kids": ["Educational Toys", "Baby Carriers", "Organic Baby Clothes", "Kids’ Furniture"],
  "Gaming & Esports": ["Gaming Chairs", "RGB Keyboards", "Console Accessories", "VR Headsets"],
  "Travel Accessories": ["Travel Pillows", "Packing Cubes", "Passport Holders", "Portable Luggage Scales"],
  "Self-Care & Relaxation": ["Essential Oil Diffusers", "Weighted Blankets", "Bath Bombs", "Aromatherapy Kits"],
  "Crafts & DIY": ["Knitting Kits", "3D Printing Pens", "DIY Home Repair Kits", "Scrapbooking Supplies"],
  "Automotive Accessories": ["Dash Cams", "Car Organizers", "Portable Tire Inflators", "Car Cleaning Tools"],
  "Garden & Outdoor Living": ["Indoor Plant Pots", "Vertical Gardens", "Lawn Care Tools", "Solar-Powered Garden Lights"],
  "Smart Home Products": ["Smart Thermostats", "Smart Plugs", "Robot Vacuums", "Video Doorbells"],
  "Eco-Friendly Fashion": ["Vegan Leather Bags", "Organic Cotton T-Shirts", "Recycled Plastic Shoes", "Hemp Clothing"],
  "Luxury & Niche Products": ["Designer Handbags", "High-End Watches", "Collectible Sneakers", "Fine Jewelry"],
  "Seasonal Products": ["Holiday Decorations", "Outdoor Heaters", "Cooling Fans", "Snow Removal Tools"],
  "Hobbies & Interests": ["Photography Equipment", "Musical Instruments", "Drone Accessories", "Collectible Action Figures"],
  "Office & Productivity": ["Ergonomic Chairs", "Standing Desks", "Blue Light Glasses", "Desk Organizers"],
  "Wellness Gadgets": ["Sleep Trackers", "Posture Correctors", "Foot Massagers", "UV Sanitizers"],
  "Fashion Accessories": ["Watches", "Sunglasses", "Handbags", "Scarves"],
  "Tech Wearables": ["Smart Rings", "Fitness Trackers", "Augmented Reality Glasses", "Smart Clothing"],
  "Home Improvement": ["Power Tools", "Smart Locks", "DIY Furniture Kits", "Wallpaper Decals"],
  "Luxury Beauty": ["High-End Perfumes", "Designer Skincare", "Premium Hair Tools", "Organic Makeup"],
  "Personal Finance": ["Budget Planners", "Expense Trackers", "Financial Literacy Books", "Investment Tools"],
  "Home Office Essentials": ["Noise-Canceling Headphones", "Monitor Stands", "Wireless Keyboards", "Webcams"],
  "Outdoor Sports": ["Mountain Bikes", "Kayaks", "Rock Climbing Gear", "Fitness Trackers"],
  "Green Energy Solutions": ["Solar Panels", "Wind Turbines", "Electric Vehicle Chargers", "Energy Storage Systems"],
  "Fitness Supplements": ["Pre-Workout", "BCAAs", "Vegan Protein Powders", "Meal Replacement Shakes"],
  "Smart Health Devices": ["Blood Pressure Monitors", "Smart Scales", "Pulse Oximeters", "Temperature Sensors"],
  "Luxury Home Items": ["High-End Kitchen Appliances", "Designer Furniture", "Custom Artwork", "Luxury Bedding"],
  "Parenting & Family": ["Baby Monitors", "Child Safety Products", "Family Planners", "Educational Subscriptions"],
  "Digital Nomad Gear": ["Portable Wi-Fi Hotspots", "Travel Power Adapters", "Foldable Keyboards", "Portable Monitors"],
  "Cycling Accessories": ["Bike Locks", "Smart Helmets", "Cycling Computers", "Bike Repair Kits"],
  "Skincare Tools": ["Facial Steamers", "Microcurrent Devices", "Jade Rollers", "LED Light Therapy Masks"],
  "Eco-Friendly Home": ["Compost Bins", "Reusable Paper Towels", "Water-Saving Devices", "Non-Toxic Cleaners"],
  "Sports Equipment": ["Tennis Rackets", "Basketballs", "Soccer Cleats", "Golf Clubs"],
  "Digital Art & Animation": ["Drawing Tablets", "Stylus Pens", "Animation Software", "Graphic Design Courses"],
  "Luxury Travel": ["Private Jet Rentals", "Designer Luggage", "Exclusive Resort Packages", "Custom Travel Experiences"],
  "Outdoor Adventure Gear": ["GPS Watches", "Multi-Tools", "Portable Water Filters", "Thermal Jackets"]
}




    # Use suggestions to get a larger pool of search terms
    for category, searches in category_searches.items():
        for search in searches:
            try:
                sanitized_search = sanitize_query(search)
                suggestions = pytrends.suggestions(sanitized_search)
                trending_searches.update([sanitize_query(item['title']) for item in suggestions])
                print(f"Added {len(suggestions)} suggestions for '{sanitized_search}' in category '{category}'")
                time.sleep(random.uniform(5, 10))  # Increased delay to avoid rate limiting
            except Exception as e:
                print(f"Error processing '{sanitized_search}': {str(e)}")
                time.sleep(10)  # Longer delay on error

    # Try to add rising queries
    try:
        rising_searches = pytrends.trending_searches(pn='US')  # Get rising searches for the US
        trending_searches.update([sanitize_query(search) for search in rising_searches.values.flatten()])
        print(f"Added {len(rising_searches)} rising searches")
    except Exception as e:
        print(f"Couldn't get rising searches: {str(e)}")

    # Convert set back to list
    all_trends = list(trending_searches)

    # Estimate total time (4 seconds per trend)
    total_estimated_time = len(all_trends) * 4
    print(f"Estimated total time: {total_estimated_time/60:.2f} minutes")
    print(f"Total trends to analyze: {len(all_trends)}")

    analyzed_trends = []
    skipped_trends = []

    # Use tqdm for progress bar
    for query in tqdm(all_trends, desc="Analyzing trends", unit="trend"):
        retries = 0
        success = False
        while retries < 3:  # Reduced max retries to 3
            try:
                interest_over_time = get_with_retries(pytrends, query, timeframe)

                if interest_over_time is not None and not interest_over_time.empty:
                    trend_data = interest_over_time[query].tolist()
                    spike_percentage = detect_spike(trend_data)  # This now uses the modified algorithm
                    analyzed_trends.append({
                        "query": query,
                        "spike_percentage": spike_percentage,
                        "trend_data": trend_data
                    })
                    tqdm.write(f"Analyzed '{query}': {spike_percentage:.2f}% spike")
                else:
                    tqdm.write(f"No data available for '{query}'")
                    analyzed_trends.append({
                        "query": query,
                        "spike_percentage": 0,
                        "trend_data": []
                    })
                success = True
                break  # Success, exit retry loop
            except requests.exceptions.RequestException as e:
                retries += 1
                tqdm.write(f"Error with proxy {proxy}: {str(e)}. Switching proxy and retrying. Retry {retries}/3")
                proxy = get_next_proxy()
                pytrends = create_pytrends_object(proxy)
                time.sleep(60 * retries)  # Longer exponential backoff
            except Exception as e:
                retries += 1
                tqdm.write(f"Unexpected error for {query}: {str(e)}. Retry {retries}/3")
                time.sleep(30 * retries)  # Shorter exponential backoff for other errors

        if not success:
            skipped_trends.append(query)
            tqdm.write(f"Skipped '{query}' after 3 failed attempts")

        time.sleep(random.uniform(10, 20))  # Increased delay between queries

    # Sort trending searches by spike percentage
    analyzed_trends.sort(key=lambda x: x['spike_percentage'], reverse=True)

    print(f"Skipped {len(skipped_trends)} trends due to persistent errors:")
    for trend in skipped_trends:
        print(f"- {trend}")

    return analyzed_trends

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Query", "Spike Percentage", "Trend Data"])
        for item in data:
            writer.writerow([item['query'], f"{item['spike_percentage']:.2f}%", ', '.join(map(str, item['trend_data']))])

if __name__ == "__main__":
    start_time = time.time()
    trends = get_trending_searches()
    end_time = time.time()
    
    # Save to JSON for complete data
    with open('trending_searches.json', 'w', encoding='utf-8') as f:
        json.dump(trends, f, ensure_ascii=False, indent=4)
    
    # Save to CSV for easy manual review
    save_to_csv(trends, 'trending_searches.csv')
    
    print(f"Analysis complete. Found {len(trends)} trending searches.")
    print("Results saved to 'trending_searches.json' and 'trending_searches.csv'.")
    print(f"Total time taken: {(end_time - start_time)/60:.2f} minutes")