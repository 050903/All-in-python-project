import requests
from bs4 import BeautifulSoup
import csv
import os

def fetch_page(url):
    """
    Fetches the content of a web page.

    Args:
        url (str): The URL of the web page to fetch.

    Returns:
        str: The HTML content of the page, or None if an error occurs.
    """
    try:
        # Set a user-agent to mimic a real browser visit
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Check if the URL is correct.")
    except requests.exceptions.RequestException as req_err:
        print(f"A network error occurred: {req_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
    return None

def parse_quotes(html_content):
    """
    Parses the HTML to extract quote information.

    Args:
        html_content (str): The HTML content of the page.

    Returns:
        list: A list of dictionaries, where each dictionary represents a quote.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    quotes_data = []
    
    # Find all 'div' elements with the class 'quote'
    quote_elements = soup.find_all('div', class_='quote')

    for quote_element in quote_elements:
        # Extract the text of the quote
        text = quote_element.find('span', class_='text').get_text(strip=True)
        
        # Extract the author of the quote
        author = quote_element.find('small', class_='author').get_text(strip=True)
        
        # Extract the tags associated with the quote
        tags_elements = quote_element.find_all('a', class_='tag')
        tags = [tag.get_text(strip=True) for tag in tags_elements]
        
        quotes_data.append({
            'text': text,
            'author': author,
            'tags': ', '.join(tags) # Join tags into a single string
        })
        
    return quotes_data

def save_to_csv(data, filename='quotes.csv'):
    """
    Saves the extracted data to a CSV file.

    Args:
        data (list): A list of dictionaries to save.
        filename (str): The name of the output CSV file.
    """
    if not data:
        print("No data to save.")
        return

    # Define the fieldnames from the keys of the first dictionary
    fieldnames = data[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()
            
            # Write the data rows
            writer.writerows(data)
        
        print(f"\nSuccessfully saved {len(data)} quotes to '{os.path.abspath(filename)}'.")

    except IOError as e:
        print(f"Error writing to file {filename}: {e}")
    except Exception as err:
        print(f"An unexpected error occurred during file writing: {err}")

def main():
    """
    Main function to run the web scraper.
    """
    print("--- Python Web Scraper ---")
    
    # URL of the website to scrape
    target_url = "http://quotes.toscrape.com/"
    
    print(f"Attempting to scrape data from: {target_url}")
    
    # Step 1: Fetch the web page content
    html = fetch_page(target_url)
    
    if html:
        # Step 2: Parse the data from the HTML
        scraped_data = parse_quotes(html)
        
        if scraped_data:
            # Step 3: Save the data to a CSV file
            save_to_csv(scraped_data)
        else:
            print("Could not find any quotes to parse. The website structure might have changed.")

if __name__ == "__main__":
    main()
