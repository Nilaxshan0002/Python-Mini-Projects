import tkinter as tk
from tkinter import messagebox
import requests
import json

# ==========================================
# API Configuration
# ==========================================
API_KEY = "bd5e378503939ddaee76f12ad7a97608" 
# ⚠️ FIXED: This is now https:// (Secure Connection)
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# ==========================================
# 1. API Integration & JSON Handling
# ==========================================
class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = BASE_URL

    def get_weather(self, city):
        """Sends request to API and returns JSON data or raises an exception."""
        # API Parameters
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'  # Use 'imperial' for Fahrenheit
        }

        try:
            # HTTP Request
            response = requests.get(self.base_url, params=params, timeout=10)
            
            # Response Validation
            response.raise_for_status() # Raises HTTPError for 4xx/5xx responses
            
            # Receive JSON Data
            return response.json()
            
        except requests.exceptions.HTTPError as errh:
            if response.status_code == 404:
                raise Exception("City not found. Please check the spelling.")
            elif response.status_code == 401:
                raise Exception("Invalid API Key.\n\n1. Check that you copied the key correctly.\n2. OpenWeatherMap takes up to 2 hours to activate a NEW key. If you just created it, please wait and try again.")
            else:
                raise Exception(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError:
            raise Exception("Network Error: Please check your internet connection.")
        except requests.exceptions.Timeout:
            raise Exception("Timeout Error: The server took too long to respond.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def parse_weather_data(self, json_data):
        """Parses specific fields from the JSON response."""
        try:
            # Parsing Fields from the JSON dictionary
            city_name = json_data['name']
            country = json_data['sys']['country']
            temp = json_data['main']['temp']
            feels_like = json_data['main']['feels_like']
            humidity = json_data['main']['humidity']
            condition = json_data['weather'][0]['description'].title()
            
            # Validating that required fields exist
            if not city_name or not temp:
                raise ValueError("Missing required weather data in response.")

            return {
                "city": f"{city_name}, {country}",
                "temp": temp,
                "feels_like": feels_like,
                "humidity": humidity,
                "condition": condition
            }
        except KeyError as e:
            raise Exception(f"Failed to parse data. Missing field: {e}")

# ==========================================
# 2. GUI Dashboard (Tkinter)
# ==========================================
class WeatherDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Live Weather Dashboard")
        self.root.geometry("400x500")
        self.root.configure(bg="#2c3e50") # Dark theme background

        self.api = WeatherAPI(API_KEY)

        self.setup_ui()

    def setup_ui(self):
        """Creates the user interface."""
        # Title
        tk.Label(self.root, text="Live Weather Dashboard", font=("Helvetica", 18, "bold"), fg="white", bg="#2c3e50").pack(pady=20)

        # Location Input Frame
        frame_input = tk.Frame(self.root, bg="#2c3e50")
        frame_input.pack(pady=10)

        tk.Label(frame_input, text="Enter City:", font=("Helvetica", 12), fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=5)
        
        self.city_entry = tk.Entry(frame_input, font=("Helvetica", 12), width=20)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.bind("<Return>", lambda event: self.fetch_weather()) # Allow pressing Enter

        # Search Button
        tk.Button(self.root, text="Get Weather", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", command=self.fetch_weather).pack(pady=10)

        # Display Frame for Results
        self.display_frame = tk.Frame(self.root, bg="#34495e", bd=2, relief=tk.RIDGE)
        self.display_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Labels to hold the parsed data (Initially empty)
        self.lbl_city = tk.Label(self.display_frame, text="", font=("Helvetica", 16, "bold"), fg="#f1c40f", bg="#34495e")
        self.lbl_city.pack(pady=(15, 5))

        self.lbl_condition = tk.Label(self.display_frame, text="", font=("Helvetica", 14, "italic"), fg="#ecf0f1", bg="#34495e")
        self.lbl_condition.pack(pady=5)

        self.lbl_temp = tk.Label(self.display_frame, text="", font=("Helvetica", 36, "bold"), fg="white", bg="#34495e")
        self.lbl_temp.pack(pady=10)

        self.lbl_details = tk.Label(self.display_frame, text="", font=("Helvetica", 12), fg="#bdc3c7", bg="#34495e", justify="left")
        self.lbl_details.pack(pady=10)

    def fetch_weather(self):
        """Handles the user input and updates the GUI."""
        city = self.city_entry.get().strip()

        # User-friendly output: Input Validation
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        # Change button text to show loading
        self.lbl_city.config(text="Fetching data...")
        self.lbl_condition.config(text="")
        self.lbl_temp.config(text="")
        self.lbl_details.config(text="")
        self.root.update() # Force GUI to update immediately

        try:
            # API Request & JSON Data
            json_data = self.api.get_weather(city)
            
            # Parse Fields & Validate
            parsed_data = self.api.parse_weather_data(json_data)

            # Display Weather
            self.update_display(parsed_data)

        except Exception as e:
            # Exception Handling: Show error to user and reset display
            messagebox.showerror("Error", str(e))
            self.lbl_city.config(text="Error")
            self.lbl_condition.config(text="Could not fetch data.")
            self.lbl_temp.config(text="--°C")
            self.lbl_details.config(text="")

    def update_display(self, data):
        """Updates the GUI labels with the parsed weather data."""
        self.lbl_city.config(text=f"📍 {data['city']}")
        self.lbl_condition.config(text=f"{data['condition']}")
        self.lbl_temp.config(text=f"{data['temp']}°C")
        
        details_text = f"Feels like: {data['feels_like']}°C\nHumidity: {data['humidity']}%"
        self.lbl_details.config(text=details_text)

# ==========================================
# 3. Run Application
# ==========================================
if __name__ == "__main__":
    # Check if the user has replaced the API key
    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️ WARNING: You need to insert your OpenWeatherMap API key in the code!")
        
    root = tk.Tk()
    app = WeatherDashboardApp(root)
    root.mainloop()