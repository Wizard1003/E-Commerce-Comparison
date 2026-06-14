# About Project
A real-time product price comparison tool built with Python and Streamlit that scrapes and aggregates listings from Amazon India and Flipkart in a single search, helping consumers instantly identify the best deal across platforms.

# Features
Dual-source scraping — Fetches live listings from Amazon India (via ScraperAPI) and Flipkart (via SerpAPI / Google Shopping) in parallel
Automatic data normalisation — Standardises titles, prices (₹), and image fields into a consistent schema regardless of source
Best price highlight — Automatically identifies and badges the lowest-priced listing across both platforms
Interactive filters — Filter by source (Amazon / Flipkart), price range slider, and sort by price or source
List & Grid view — Toggle between a detailed list layout and a compact 2-column grid
Graceful fallback — Silently falls back to mock data if either API is unavailable, keeping the UI error-free
Placeholder image generation — Generates branded PIL-rendered thumbnails for listings missing product images

# Run Project:
streamlit run app.py 