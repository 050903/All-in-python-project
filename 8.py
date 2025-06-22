import requests
import os

def get_weather_data(city, api_key):
    """
    Fetches weather data for a specified city using the WeatherAPI.com API.

    Args:
        city (str): The name of the city.
        api_key (str): Your WeatherAPI.com API key.

    Returns:
        dict: A dictionary containing the weather data in JSON format,
              or None if an error occurs.
    """
    # API endpoint for current weather data
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    # Parameters for the API request
    params = {
        'key': api_key,
        'q': city
    }

    try:
        # Make the GET request to the API
        response = requests.get(base_url, params=params)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        # Return the JSON response as a Python dictionary
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        # WeatherAPI often returns error details in the JSON body even for HTTP errors
        try:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'An unknown HTTP error occurred.')
            print(f"Error: {error_message}")
        except ValueError: # If the response is not JSON
            print(f"An HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"A network error occurred: {req_err}")
        return None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None

def display_weather(data):
    """
    Parses and displays the weather data in a user-friendly format.

    Args:
        data (dict): The dictionary containing weather data from the API.
    """
    if not data:
        print("Cannot display weather data.")
        return

    # Extract relevant information from the data dictionary
    location_data = data.get('location', {})
    current_data = data.get('current', {})
    
    city_name = location_data.get('name', 'N/A')
    country = location_data.get('country', 'N/A')
    condition = current_data.get('condition', {}).get('text', 'N/A')
    temp_celsius = current_data.get('temp_c')
    temp_fahrenheit = current_data.get('temp_f')
    humidity = current_data.get('humidity')

    print("\n--- Current Weather ---")
    print(f"City: {city_name}, {country}")
    print(f"Condition: {condition}")
    
    if temp_celsius is not None and temp_fahrenheit is not None:
        print(f"Temperature: {temp_celsius}°C / {temp_fahrenheit}°F")
    else:
        print("Temperature: N/A")
        
    if humidity is not None:
        print(f"Humidity: {humidity}%")
    else:
        print("Humidity: N/A")
    print("-----------------------")


def main():
    """
    Main function to run the weather app.
    """
    print("--- Python Weather App ---")
    
    # API key is now hardcoded for convenience.
    api_key = "e1be24f806884bf1ad664228252206"

    if not api_key:
        print("API key is required to run this application. Exiting.")
        return

    while True:
        city = input("\nEnter a city name to get the weather (or 'quit' to exit): ").strip()
        if city.lower() == 'quit':
            break
        
        if not city:
            print("Please enter a valid city name.")
            continue

        weather_data = get_weather_data(city, api_key)
        
        if weather_data:
            display_weather(weather_data)

    print("\nThanks for using the weather app!")


if __name__ == "__main__":
    main()
