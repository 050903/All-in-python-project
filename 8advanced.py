import requests
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import threading
from datetime import datetime
import json
from io import BytesIO

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather App")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # --- API Key ---
        self.api_key = "e1be24f806884bf1ad664228252206"
        
        # --- Style ---
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # --- State ---
        self.recent_cities = []

        # --- Main Layout ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Top Frame: Input and Recent Searches
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x")
        
        input_frame = ttk.Frame(top_frame)
        input_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ttk.Label(input_frame, text="Enter City:").pack(anchor="w")
        self.city_var = tk.StringVar()
        self.city_entry = ttk.Entry(input_frame, textvariable=self.city_var)
        self.city_entry.pack(fill="x", pady=(0, 5))
        self.city_entry.bind("<Return>", self.handle_search)
        
        search_button = ttk.Button(input_frame, text="Get Weather", command=self.handle_search)
        search_button.pack(anchor="w")

        history_frame = ttk.LabelFrame(top_frame, text="Recent Searches")
        history_frame.pack(side="right", fill="both", expand=True)

        self.history_listbox = tk.Listbox(history_frame, height=5)
        self.history_listbox.pack(fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.handle_history_select)

        # Separator
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

        # Bottom Frame: Weather Display
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill="both", expand=True)

        # Current Weather Frame
        current_frame = ttk.LabelFrame(display_frame, text="Current Weather", padding="10")
        current_frame.pack(fill="x", pady=(0, 10))
        
        self.current_weather_icon = ttk.Label(current_frame)
        self.current_weather_icon.grid(row=0, column=0, rowspan=2, padx=10)
        self.current_weather_label = ttk.Label(current_frame, text="Search for a city to begin.", font=("Helvetica", 12))
        self.current_weather_label.grid(row=0, column=1, sticky="w")
        self.current_details_label = ttk.Label(current_frame, text="")
        self.current_details_label.grid(row=1, column=1, sticky="w")

        # Forecast Frame
        self.forecast_frame = ttk.LabelFrame(display_frame, text="3-Day Forecast", padding="10")
        self.forecast_frame.pack(fill="both", expand=True)

    def handle_search(self, event=None):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return
        self.fetch_and_display_weather(city)

    def handle_history_select(self, event=None):
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            return
        city = self.history_listbox.get(selected_indices[0])
        self.city_var.set(city)
        self.fetch_and_display_weather(city)
        
    def fetch_weather_data(self, city):
        base_url = "http://api.weatherapi.com/v1/forecast.json"
        params = {'key': self.api_key, 'q': city, 'days': 3}
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            try:
                error_data = response.json()
                msg = error_data.get('error', {}).get('message', 'Unknown HTTP error')
                messagebox.showerror("API Error", f"Could not fetch weather data: {msg}")
            except ValueError:
                messagebox.showerror("API Error", "An unrecoverable HTTP error occurred.")
            return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", f"A network error occurred: {e}")
            return None

    def fetch_and_display_weather(self, city):
        weather_data = self.fetch_weather_data(city)
        if not weather_data:
            return

        # --- Update Current Weather ---
        location = weather_data['location']
        current = weather_data['current']
        
        loc_text = f"{location['name']}, {location['country']}"
        condition_text = f"{current['condition']['text']}"
        temp_text = f"{current['temp_c']}°C / {current['temp_f']}°F"
        
        self.current_weather_label.config(text=f"{loc_text}\n{condition_text}\n{temp_text}")
        details = (f"Humidity: {current['humidity']}%    |    "
                   f"Wind: {current['wind_kph']} kph    |    "
                   f"Feels like: {current['feelslike_c']}°C")
        self.current_details_label.config(text=details)

        icon_url = "https:" + current['condition']['icon']
        self.update_image_from_url(self.current_weather_icon, icon_url)

        # --- Update Forecast ---
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
            
        forecast_days = weather_data['forecast']['forecastday']
        for i, day_data in enumerate(forecast_days):
            day_frame = ttk.Frame(self.forecast_frame)
            day_frame.grid(row=0, column=i, padx=10, pady=5, sticky="ns")
            
            date = day_data['date']
            day = day_data['day']
            
            ttk.Label(day_frame, text=date, font=("Helvetica", 10, "bold")).pack()
            
            icon = ttk.Label(day_frame)
            icon.pack()
            self.update_image_from_url(icon, "https:" + day['condition']['icon'])
            
            ttk.Label(day_frame, text=day['condition']['text']).pack()
            temp_range = f"H: {day['maxtemp_c']}°C\nL: {day['mintemp_c']}°C"
            ttk.Label(day_frame, text=temp_range).pack()

        # --- Update History ---
        city_title = city.title()
        if city_title not in self.recent_cities:
            self.recent_cities.insert(0, city_title)
            self.history_listbox.insert(0, city_title)
            if len(self.recent_cities) > 5:
                self.recent_cities.pop()
                self.history_listbox.delete(tk.END)

    def update_image_from_url(self, label, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            photo = ImageTk.PhotoImage(img)
            
            label.config(image=photo)
            label.image = photo
        except Exception as e:
            print(f"Failed to load image: {e}")
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
