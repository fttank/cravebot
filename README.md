CraveBot 🤖
===========

CraveBot is a simple and modern, interactive web application designed to help users discover local restaurants in a fun, "swipe-right" interface. Built with Streamlit and powered by the Google Places API, it offers a dynamic way to find your next meal.

✨ Features
----------

*   **Interactive Swiping:** Like or pass on restaurants with a simple, engaging UI.
    
*   **Live Local Data:** Fetches real-time restaurant information using the Google Places API.
    
*   **"Crave List":** Save your favorite discoveries to a persistent list on the sidebar.
    
*   **Smart Randomizer:** Can't decide? Let CraveBot pick a random food category for you!
    
*   **Direct Google Maps Links:** Click on any restaurant to instantly open its location and details in Google Maps.
    
*   **Robust Image Fallbacks:** Ensures a great visual experience even when a restaurant is missing an official photo.
    
*   **Fully Responsive:** A beautiful, mobile-first design that works on any device.
    

🛠️ Tech Stack
--------------

*   **Framework:** Streamlit
    
*   **Language:** Python
    
*   **APIs:** Google Places API, Google Geocoding API
    
*   **Styling:** Custom CSS with a Material Design 3 inspired dark theme
    
*   **Libraries:** Requests
    

🚀 Getting Started
------------------

Follow these instructions to get a local copy up and running.

### Prerequisites

*   Python 3.8 or newer
    
*   A Google Cloud Platform account with the **Places API** and **Geocoding API** enabled.
    

### Installation

1.  git clone \[https://github.com/fttank/cravebot.git\](https://github.com/fttank/cravebot.git)cd cravebot
    
2.  \# For Windowspython -m venv venv.\\venv\\Scripts\\activate# For macOS/Linuxpython3 -m venv venvsource venv/bin/activate
    
3.  pip install -r requirements.txt
    
4.  **Set up your API Key:**
    
    *   Create a folder in the root of the project called .streamlit.
        
    *   Inside that folder, create a file named secrets.toml.
        
    *   GOOGLE\_API\_KEY = "your\_actual\_api\_key\_here"
        
5.  streamlit run app.py
    

The application should now be running in your browser!
