import requests
from bs4 import BeautifulSoup
import csv
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

def fetch_page(url):
    """
    Fetches the content of a web page.

    Args:
        url (str): The URL of the web page to fetch.

    Returns:
        tuple: (HTML content as string, error message as string)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text, None
    except requests.exceptions.HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return None, f"Network error: {req_err}"
    except Exception as err:
        return None, f"An unexpected error occurred: {err}"

def parse_quotes(html_content):
    """
    Parses the HTML to extract quote information from quotes.toscrape.com.

    Args:
        html_content (str): The HTML content of the page.

    Returns:
        list: A list of dictionaries, where each dictionary represents a quote.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    quotes_data = []
    quote_elements = soup.find_all('div', class_='quote')

    for quote_element in quote_elements:
        text = quote_element.find('span', class_='text').get_text(strip=True)
        author = quote_element.find('small', class_='author').get_text(strip=True)
        tags_elements = quote_element.find_all('a', class_='tag')
        tags = ', '.join([tag.get_text(strip=True) for tag in tags_elements])
        
        quotes_data.append({
            'Text': text,
            'Author': author,
            'Tags': tags
        })
    return quotes_data

class ScraperApp(tk.Tk):
    """A GUI application for scraping web data."""
    def __init__(self):
        super().__init__()
        self.title("Web Scraper")
        self.geometry("800x600")

        self.scraped_data = []
        self.create_widgets()

    def create_widgets(self):
        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- URL Input Frame ---
        url_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        url_frame.pack(fill=tk.X, pady=5)

        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT, padx=(0, 5))
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.insert(0, "http://quotes.toscrape.com/")
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.scrape_button = ttk.Button(url_frame, text="Scrape", command=self.start_scraping_thread)
        self.scrape_button.pack(side=tk.LEFT, padx=(10, 0))

        # --- Results Frame ---
        results_frame = ttk.LabelFrame(main_frame, text="Scraped Data", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ('Text', 'Author', 'Tags')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- Actions & Status Frame ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)

        self.save_button = ttk.Button(action_frame, text="Save to CSV", command=self.save_to_csv, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(action_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10,0))

    def start_scraping_thread(self):
        """Starts the scraping process in a separate thread to keep the UI responsive."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        self.scrape_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.status_label.config(text=f"Scraping {url}...")
        
        # Clear previous results
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.scraped_data = []

        # Run the scraping logic in a background thread
        thread = threading.Thread(target=self.scrape_worker, args=(url,))
        thread.daemon = True
        thread.start()

    def scrape_worker(self, url):
        """Worker function that performs the scraping."""
        html, error = fetch_page(url)
        if error:
            self.update_ui_with_error(error)
            return

        data = parse_quotes(html)
        if not data:
            self.update_ui_with_error("No quotes found. The website structure may have changed.")
            return

        self.scraped_data = data
        self.after(0, self.update_ui_with_results)

    def update_ui_with_results(self):
        """Updates the Treeview with the scraped data from the main UI thread."""
        if not self.scraped_data:
            return

        for item in self.scraped_data:
            self.tree.insert('', tk.END, values=[item['Text'], item['Author'], item['Tags']])
        
        self.status_label.config(text=f"Success! Found {len(self.scraped_data)} items.")
        self.save_button.config(state=tk.NORMAL)
        self.scrape_button.config(state=tk.NORMAL)

    def update_ui_with_error(self, message):
        """Displays an error message in the UI."""
        self.after(0, lambda: messagebox.showerror("Scraping Error", message))
        self.status_label.config(text=f"Error: {message}")
        self.scrape_button.config(state=tk.NORMAL)

    def save_to_csv(self):
        """Saves the extracted data to a CSV file."""
        if not self.scraped_data:
            messagebox.showinfo("No Data", "There is no data to save.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Scraped Data"
        )

        if not filepath:
            return # User cancelled the save dialog

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = self.scraped_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.scraped_data)
            messagebox.showinfo("Success", f"Data successfully saved to\n{os.path.abspath(filepath)}")
            self.status_label.config(text=f"Data saved to {os.path.basename(filepath)}")
        except IOError as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")

if __name__ == "__main__":
    app = ScraperApp()
    app.mainloop()
