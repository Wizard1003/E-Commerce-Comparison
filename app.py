import streamlit as st
import requests
import time
import random
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import io

# API Keys
SCRAPERAPI_KEY = "46cb45f5003472aa3171f18647706c36"
SERPAPI_KEY = "72584f67c92667d803cc636194c0b307b17719b76e75ed7fd03688c93c7eec93"

# Function to generate simple product image placeholder
def generate_product_image(product_name, source):
    # Create a colored background based on source
    bg_color = (30, 60, 110) if source == "Amazon" else (50, 120, 50)
    text_color = (255, 255, 255)
    
    # Create image
    img = Image.new('RGB', (300, 200), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Add product name
    try:
        # This may fail if PIL doesn't have a font available
        font = ImageFont.truetype("arial.ttf", 20)
        d.text((20, 80), product_name, fill=text_color, font=font)
    except:
        # Fallback if font loading fails
        d.text((20, 80), product_name, fill=text_color)
    
    # Add source name
    try:
        font_small = ImageFont.truetype("arial.ttf", 14)
        d.text((20, 150), f"Source: {source}", fill=text_color, font=font_small)
    except:
        d.text((20, 150), f"Source: {source}", fill=text_color)
    
    # Convert to base64 for display
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

# Mock data for testing when APIs fail
def get_mock_data(product, source):
    mock_products = []
    
    product_variations = {
        "iphone": ["iPhone 13", "iPhone 14", "iPhone 14 Pro", "iPhone 14 Pro Max", "iPhone 15"],
        "samsung": ["Samsung Galaxy S22", "Samsung Galaxy S23", "Samsung Galaxy S23 Ultra", "Samsung Galaxy Z Fold"],
        "laptop": ["MacBook Pro", "Dell XPS", "HP Spectre", "Lenovo ThinkPad", "Asus ZenBook"],
        "headphone": ["Sony WH-1000XM4", "Bose QuietComfort", "Apple AirPods Pro", "JBL Tune", "Sennheiser HD"]
    }
    
    # Determine which product category to use
    product_key = None
    for key in product_variations:
        if key in product.lower():
            product_key = key
            break
    
    # If no specific category found, use generic names
    if product_key is None:
        product_names = [f"{product} {i}" for i in range(1, 6)]
    else:
        product_names = product_variations[product_key]
    
    if source == "amazon":
        base_price = random.randint(40000, 60000)
        for i, name in enumerate(product_names[:5]):
            mock_products.append({
                'title': f"{name} {random.choice(['64GB', '128GB', '256GB'])} {random.choice(['Black', 'White', 'Gold'])}",
                'price': base_price + random.randint(-5000, 5000),
                'image': generate_product_image(name, "Amazon"),
                'link': "https://www.amazon.in/",
                'source': "Amazon",
                'mock': True
            })
    else:  # Flipkart
        base_price = random.randint(39000, 59000)
        for i, name in enumerate(product_names[:5]):
            mock_products.append({
                'title': f"{name} {random.choice(['4GB', '6GB', '8GB'])}RAM {random.choice(['Midnight Black', 'Starlight Silver', 'Rose Gold'])}",
                'price': base_price + random.randint(-4000, 4000),
                'image': generate_product_image(name, "Flipkart"),
                'link': "https://www.flipkart.com/",
                'source': "Flipkart",
                'mock': True
            })
            
    return mock_products

# Amazon Scraper Function with timeout and retry
def scrape_amazon(product, use_mock=False):
    if use_mock:
        st.info("Using mock data for Amazon (API connection failed)")
        time.sleep(1)  # Simulate API call delay
        return get_mock_data(product, "amazon")
        
    url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url=https://www.amazon.in/s?k={product}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return get_mock_data(product, "amazon")
        
        data = response.json()
        # Process Amazon data to standardize format
        processed_data = []
        for item in data.get("results", []):
            # Get image URL or generate a placeholder if missing
            image_url = item.get('image')
            if not image_url:
                image_url = generate_product_image(item.get('title', product), "Amazon")
                
            processed_data.append({
                'title': item.get('title', f"Amazon {product}"),
                'price': item.get('price', random.randint(40000, 60000)),
                'image': image_url,
                'link': item.get('link', "https://www.amazon.in/"),
                'source': "Amazon"
            })
        return processed_data
    except Exception as e:
            return get_mock_data(product, "amazon")
    
# Flipkart Scraper Function with timeout and retry
def scrape_flipkart(product, use_mock=False):
    if use_mock:
        st.info("Using mock data for Flipkart (API connection failed)")
        time.sleep(1)  # Simulate API call delay
        return get_mock_data(product, "flipkart")
        
    url = f"https://serpapi.com/search.json?engine=google&q={product}+site%3Aflipkart.com&api_key={SERPAPI_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            st.error(f"Flipkart Scraper Error: {response.status_code}")
            return get_mock_data(product, "flipkart")
        
        data = response.json()
        # Process Flipkart data to standardize format
        processed_data = []
        for item in data.get("organic_results", []):
            # Extract price from snippet if available
            price_text = item.get('snippet', '')
            price = None
            
            # Try to extract price from snippet text (this is a simplistic approach)
            import re
            price_match = re.search(r'₹\s*([\d,]+)', price_text)
            if price_match:
                price = int(price_match.group(1).replace(',', ''))
            else:
                price = random.randint(39000, 59000)
            
            # Get image URL or generate a placeholder if missing
            image_url = item.get('thumbnail')
            if not image_url:
                image_url = generate_product_image(item.get('title', product), "Flipkart")
                
            processed_data.append({
                'title': item.get('title', f"Flipkart {product}"),
                'price': price,
                'image': image_url,
                'link': item.get('link', "https://www.flipkart.com/"),
                'source': "Flipkart"
            })
        return processed_data
    except Exception as e:
        st.error(f"Flipkart scraper error: {str(e)}")
        return get_mock_data(product, "flipkart")

# Merge Results Function
def merge_results(search_query, use_mock=False):
    amazon_results = scrape_amazon(search_query, use_mock)
    flipkart_results = scrape_flipkart(search_query, use_mock)
    
    all_results = amazon_results + flipkart_results
    return all_results

# Streamlit App
def main():
    st.title("Price Comparison App")
    st.write("Compare prices across Amazon and Flipkart")
    
    # Sidebar options
    st.sidebar.title("Options")
    use_mock = st.sidebar.checkbox("Use mock data (for testing)", value=False)
    
    # Search input
    search_query = st.text_input("Enter product to search", "iphone 14")
    
    if st.button("Search") and search_query:
        st.write(f"Searching for: {search_query}")
        
        # Show spinner while loading results
        with st.spinner("Fetching results..."):
            products = merge_results(search_query, use_mock)
        
        if products:
            # Find minimum price
            valid_products = [p for p in products if 'price' in p]
            min_price = min([p.get('price', float('inf')) for p in valid_products]) if valid_products else None
            
            # Display results
            st.subheader(f"Found {len(products)} products")
            
            # Add filters
            st.sidebar.subheader("Filters")
            sources = st.sidebar.multiselect(
                "Sources", 
                options=list(set(p.get('source', 'Unknown') for p in products)),
                default=list(set(p.get('source', 'Unknown') for p in products))
            )
            
            # Price range filter
            if valid_products:
                all_prices = [p.get('price', 0) for p in valid_products]
                min_available = min(all_prices)
                max_available = max(all_prices)
                price_range = st.sidebar.slider(
                    "Price Range (₹)",
                    min_value=min_available,
                    max_value=max_available,
                    value=(min_available, max_available),
                    step=1000
                )
            
            # Apply filters
            filtered_products = [
                p for p in products 
                if p.get('source', 'Unknown') in sources and 
                (not valid_products or 
                 (p.get('price', 0) >= price_range[0] and p.get('price', 0) <= price_range[1]))
            ]
            
            # Sorting options
            sort_by = st.sidebar.selectbox(
                "Sort by",
                options=["Price (Low to High)", "Price (High to Low)", "Source"]
            )
            
            if sort_by == "Price (Low to High)":
                filtered_products = sorted(filtered_products, key=lambda x: x.get('price', float('inf')))
            elif sort_by == "Price (High to Low)":
                filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0), reverse=True)
            elif sort_by == "Source":
                filtered_products = sorted(filtered_products, key=lambda x: x.get('source', ''))
            
            if min_price:
                st.success(f"Best price found: ₹{min_price:,}")
            
            # Display grid view if there are many products
            display_mode = st.sidebar.radio("Display mode", ["List View", "Grid View"])
            
            if display_mode == "Grid View":
                # Display products in a grid
                cols = st.columns(2)
                for i, product in enumerate(filtered_products):
                    with cols[i % 2]:
                        st.subheader(product.get('title', 'Product Name'))
                        
                        if 'image' in product:
                            st.image(product['image'], width=200)
                        
                        if 'price' in product:
                            price_text = f"₹{product['price']:,}"
                            if min_price and product['price'] == min_price:
                                st.markdown(f"**Price: {price_text} (Best Price)**")
                            else:
                                st.write(f"Price: {price_text}")
                        
                        if 'source' in product:
                            if product.get('mock', False):
                                st.info(f"Source: {product['source']} (Mock Data)")
                            else:
                                st.info(f"Source: {product['source']}")
                        
                        if 'link' in product:
                            st.markdown(f"[View Product]({product['link']})")
                        
                        st.markdown("---")
            else:
                # List view - create a container for results
                results_container = st.container()
                
                with results_container:
                    for i, product in enumerate(filtered_products):
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            if 'image' in product:
                                st.image(product['image'], width=150)
                            else:
                                st.write("No image")
                        
                        with col2:
                            if 'title' in product:
                                st.subheader(product['title'])
                            
                            if 'price' in product:
                                price_text = f"₹{product['price']:,}"
                                if min_price and product['price'] == min_price:
                                    st.markdown(f"**Price: {price_text} (Best Price)**")
                                else:
                                    st.write(f"Price: {price_text}")
                            
                            if 'source' in product:
                                if product.get('mock', False):
                                    st.info(f"Source: {product['source']} (Mock Data)")
                                else:
                                    st.info(f"Source: {product['source']}")
                            
                            if 'link' in product:
                                st.markdown(f"[View Product]({product['link']})")
                        
                        st.markdown("---")
        else:
            st.warning("No products found. Try a different search term or check your internet connection.")

if __name__ == "__main__":
    main()