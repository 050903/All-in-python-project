import requests
import re

def is_valid_url(url):
    """
    Validates the URL format using a regular expression.
    Checks if the URL starts with http:// or https://.
    """
    # Regex to check for a valid URL format
    regex = re.compile(
        r'^(https?://)'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None

def shorten_url(long_url):
    """
    Shortens a long URL using the TinyURL API.

    Args:
        long_url (str): The original, long URL.

    Returns:
        str: The shortened URL, or an error message if something goes wrong.
    """
    api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.HTTPError as http_err:
        return f"Error: An HTTP error occurred - {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Error: A network error occurred - {req_err}"
    except Exception as err:
        return f"Error: An unexpected error occurred - {err}"

def main():
    """
    Main function to run the URL shortener app.
    """
    print("--- Simple URL Shortener (using TinyURL) ---")

    while True:
        long_url = input("\nEnter a long URL to shorten (or 'quit' to exit): ").strip()
        
        if long_url.lower() == 'quit':
            break
        
        if not is_valid_url(long_url):
            print("Invalid URL format. Please enter a full URL (e.g., 'https://www.google.com').")
            continue

        shortened_url = shorten_url(long_url)
        
        print("\n--- Result ---")
        print(f"Shortened URL: {shortened_url}")
        print("--------------")

    print("\nThanks for using the URL shortener!")

if __name__ == "__main__":
    main()
