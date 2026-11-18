import requests
from bs4 import BeautifulSoup
import csv
import time

# ==========================================
# 1. HTTP Requests & Error Handling
# ==========================================
def fetch_page(url):
    """Sends an HTTP request to the target website and returns the HTML."""
    # Responsible scraping practice: Set a User-Agent so the website knows 
    # a real browser (or bot) is making the request.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Send Request
        response = requests.get(url, headers=headers, timeout=10)
        # Check if the request was successful (Status Code 200)
        response.raise_for_status() 
        return response.text
    except requests.exceptions.HTTPError as errh:
        print(f"❌ HTTP Error: {errh}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Please check your internet connection.")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: The website took too long to respond.")
    except requests.exceptions.RequestException as err:
        print(f"❌ Something went wrong: {err}")
    
    return None

# ==========================================
# 2. Parsing & Data Extraction
# ==========================================
def parse_books(html_content):
    """Parses the HTML using BeautifulSoup and extracts book data."""
    if not html_content:
        return []

    # Parse Elements
    soup = BeautifulSoup(html_content, 'html.parser')
    books_data = []

    # Find all book containers on the page
    # (Looking at the HTML structure of books.toscrape.com)
    book_containers = soup.find_all('article', class_='product_pod')

    for book in book_containers:
        try:
            # Extract Title (It's inside an 'a' tag within an 'h3' tag)
            title = book.find('h3').find('a')['title']
            
            # Extract Price (It's inside a 'p' tag with class 'price_color')
            raw_price = book.find('p', class_='price_color').text
            
            # Extract Availability (Inside a 'p' tag with class 'instock availability')
            raw_availability = book.find('p', class_='instock availability').text.strip()

            # --- CLEAN DATA ---
            # 1. Clean Price: Remove the '£' symbol and convert to a float number
            clean_price = float(raw_price.replace('£', '').replace('Â', '').strip())
            
            # 2. Clean Availability: Remove extra spaces and newlines
            clean_availability = " ".join(raw_availability.split())

            # Structure Data into a Dictionary
            book_info = {
                "Title": title,
                "Price (£)": clean_price,
                "Availability": clean_availability
            }
            
            books_data.append(book_info)

        except AttributeError as e:
            # If one book is missing a specific tag, skip it and continue
            print(f"⚠️ Skipped a book due to missing data: {e}")
            continue

    return books_data

# ==========================================
# 3. Saving to CSV (Structured Storage)
# ==========================================
def save_to_csv(data, filename="scraped_books.csv"):
    """Saves the extracted dictionary data to a CSV file."""
    if not data:
        print("📭 No data to save.")
        return

    # Define the columns based on the dictionary keys
    fieldnames = ["Title", "Price (£)", "Availability"]

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()
            
            # Write the data rows
            writer.writerows(data)
            
        print(f"✅ Successfully saved {len(data)} records to '{filename}'!")
    except IOError as e:
        print(f"❌ Error saving file: {e}")

# ==========================================
# 4. The Main Pipeline (Flowchart Logic)
# ==========================================
def main():
    print("🕸️ Starting Web Data Scraper...")
    
    # Step 1: Target Website
    target_url = "http://books.toscrape.com/"
    print(f"🌐 Target URL: {target_url}")

    # Step 2: Send Request & Receive HTML
    print("📥 Fetching HTML...")
    html = fetch_page(target_url)

    if html:
        print("🔍 Parsing HTML and extracting data...")
        # Step 3 & 4: Parse Elements, Clean Data, Structure Data
        extracted_data = parse_books(html)
        
        if extracted_data:
            print(f"📚 Found {len(extracted_data)} books.")
            # Step 5: Save Dataset
            save_to_csv(extracted_data)
        else:
            print("⚠️ No data was extracted. The website structure might have changed.")
    else:
        print("❌ Scraping failed. Could not retrieve the webpage.")

    # Responsible Scraping Practice: 
    # If scraping multiple pages, you should always add a delay between requests
    # so you don't overload the website's server. 
    # time.sleep(2) 

if __name__ == "__main__":
    main()