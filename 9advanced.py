import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

class URLShortenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced URL Shortener")
        self.root.geometry("550x300")
        self.root.resizable(False, False)

        # Style
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # --- Input Frame ---
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        input_frame.pack(fill="x", pady=5)
        
        ttk.Label(input_frame, text="Long URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.long_url_var = tk.StringVar()
        long_url_entry = ttk.Entry(input_frame, textvariable=self.long_url_var, width=60)
        long_url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ttk.Label(input_frame, text="Service:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.service_var = tk.StringVar(value="TinyURL")
        service_menu = ttk.OptionMenu(input_frame, self.service_var, "TinyURL", "TinyURL", "is.gd", "Bitly", command=self.toggle_bitly_token)
        service_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Bitly Token (hidden by default)
        self.bitly_token_label = ttk.Label(input_frame, text="Bitly Token:")
        self.bitly_token_var = tk.StringVar()
        self.bitly_token_entry = ttk.Entry(input_frame, textvariable=self.bitly_token_var, width=30, show="*")
        
        # --- Action Frame ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)
        shorten_button = ttk.Button(action_frame, text="Shorten URL", command=self.handle_shorten)
        shorten_button.pack()

        # --- Result Frame ---
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")
        result_frame.pack(fill="x", pady=5)
        
        self.short_url_var = tk.StringVar(value="Shortened URL will appear here.")
        result_entry = ttk.Entry(result_frame, textvariable=self.short_url_var, state="readonly", width=60)
        result_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.copy_button = ttk.Button(result_frame, text="Copy", command=self.copy_to_clipboard, state="disabled")
        self.copy_button.grid(row=0, column=1, padx=5, pady=5)
        if not PYPERCLIP_AVAILABLE:
            self.copy_button.config(text="Copy N/A")

    def toggle_bitly_token(self, selected_service):
        if selected_service == "Bitly":
            self.bitly_token_label.grid(row=1, column=2, padx=(10, 5), pady=5, sticky="w")
            self.bitly_token_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        else:
            self.bitly_token_label.grid_remove()
            self.bitly_token_entry.grid_remove()

    def handle_shorten(self):
        long_url = self.long_url_var.get().strip()
        if not self.is_valid_url(long_url):
            messagebox.showerror("Invalid URL", "Please enter a valid URL, including http:// or https://")
            return

        service = self.service_var.get()
        short_url = ""

        try:
            if service == "TinyURL":
                short_url = self._shorten_tinyurl(long_url)
            elif service == "is.gd":
                short_url = self._shorten_isgd(long_url)
            elif service == "Bitly":
                token = self.bitly_token_var.get().strip()
                if not token:
                    messagebox.showerror("Missing Token", "Bitly requires an API access token.")
                    return
                short_url = self._shorten_bitly(long_url, token)
            
            self.short_url_var.set(short_url)
            self.copy_button.config(state="normal" if PYPERCLIP_AVAILABLE else "disabled")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.short_url_var.set("Failed to shorten URL.")
            self.copy_button.config(state="disabled")

    def _shorten_tinyurl(self, url):
        api_url = f"http://tinyurl.com/api-create.php?url={url}"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text

    def _shorten_isgd(self, url):
        api_url = "https://is.gd/create.php"
        params = {'format': 'json', 'url': url}
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()['shorturl']

    def _shorten_bitly(self, url, token):
        api_url = "https://api-ssl.bitly.com/v4/shorten"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"long_url": url}
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 403:
             raise Exception("Bitly API Error: Forbidden. Check your API token and permissions.")
        response.raise_for_status()
        return response.json()['link']

    def is_valid_url(self, url):
        regex = re.compile(
            r'^(https?://)'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def copy_to_clipboard(self):
        url_to_copy = self.short_url_var.get()
        if url_to_copy and "Failed" not in url_to_copy and PYPERCLIP_AVAILABLE:
            pyperclip.copy(url_to_copy)
            messagebox.showinfo("Copied!", "The shortened URL has been copied to your clipboard.")

if __name__ == "__main__":
    root = tk.Tk()
    app = URLShortenerApp(root)
    root.mainloop()
