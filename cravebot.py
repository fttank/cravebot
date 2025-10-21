# ==============================================================================
# IMPORTS
# ==============================================================================
import streamlit as st
import requests
import random
from urllib.parse import quote

# ==============================================================================
# APP CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="CraveBot", page_icon="🤖", layout="wide")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def load_css(file_name):
    """Loads a local CSS file into the Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {file_name}")

def create_google_maps_link(name, address):
    """Generates a Google Maps search URL from a name and address."""
    query = quote(f"{name} {address}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"

def get_valid_image_url(item, api_key, craving):
    """
    Attempts to get a valid image URL. Tries Google Places first, then falls
    back to Unsplash to ensure an image is always found.
    """
    # Attempt to fetch image from Google Places API
    try:
        photo_ref = item["photos"][0]["photo_reference"]
        google_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_ref}&key={api_key}'
        
        # Actively check if the URL points to a valid image to avoid broken icons
        response = requests.head(google_url, allow_redirects=True, timeout=3)
        if 'image' in response.headers.get('Content-Type', ''):
            return google_url
    except (requests.RequestException, KeyError, IndexError, TypeError):
        # This handles cases where the photo key is missing, the request fails, etc.
        pass

    # Fallback to Unsplash if the Google image fails
    name = item.get("name", "food")
    unsplash_url = f"https://source.unsplash.com/800x600/?{quote(craving)},{quote(name)}"
    return unsplash_url

@st.cache_data(ttl=3600)
def search_places(_api_key, keyword, location):
    """
    Performs geocoding and then a nearby search using the Google Places API.
    Returns a list of restaurant results.
    """
    # 1. Geocode the location string to get latitude and longitude
    geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(location)}&key={_api_key}"
    try:
        resp = requests.get(geo_url).json()
        if resp.get("results"):
            loc = resp["results"][0]["geometry"]["location"]
            lat, lng = loc["lat"], loc["lng"]
        else:
            st.error("Could not find that location. Please try a different ZIP or neighborhood.")
            return []
    except requests.RequestException:
        st.error("Failed to connect to the Geocoding API.")
        return []

    # 2. Use coordinates to find nearby restaurants
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=3500&keyword={quote(keyword)}&type=restaurant&key={_api_key}"
    try:
        response = requests.get(url).json()
        return response.get("results", [])
    except requests.RequestException:
        st.error("Failed to connect to the Places API.")
        return []

def display_favorites():
    """Renders the sidebar component for the user's saved 'Crave List'."""
    with st.container():
        st.markdown('<div class="favorites-container">', unsafe_allow_html=True)
        st.markdown("<h3>❤️ Your Crave List</h3>", unsafe_allow_html=True)
        
        if not st.session_state.favorites:
            st.info("Your craved items will appear here!")
        else:
            for fav in st.session_state.favorites:
                name = fav.get('name', 'N/A')
                address = fav.get('vicinity', 'N/A')
                maps_link = create_google_maps_link(name, address)
                st.markdown(f'''
                <a href="{maps_link}" target="_blank" class="favorite-item">
                    <h4>{name}</h4>
                    <p>{address}</p>
                </a>
                ''', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        if st.button("Clear All", key="clear_favorites"):
            st.session_state.favorites = []
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# INITIALIZE APP STATE AND RENDER STATIC UI
# ==============================================================================

# Load custom CSS and initialize session state variables
load_css("style.css")
for key in ["results", "index", "favorites", "recommendation"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["results", "favorites"] else (0 if key == "index" else None)

# Render the main page title and header
st.markdown("<h1 class='main-title'>🤖 CraveBot</h1>", unsafe_allow_html=True)
st.subheader("Find your next bite — one swipe at a time!")

# Render the introductory info box
st.info("""
**Welcome to CraveBot!** 1.  Tell me what you're craving (like "tacos" or "sushi").
2.  Enter your ZIP code to find spots nearby.

**Pro-tip:** Don't know what you want? Just enter your **ZIP code** and hit "Find Food" for a random suggestion!
""")

# Render the search form
with st.form("search_form"):
    location_input = st.text_input("Enter your ZIP or neighborhood:", placeholder="e.g. 92104")
    craving_input = st.text_input("What are you craving? (Optional)", placeholder="e.g. sushi, tacos, pizza")
    search_button = st.form_submit_button("Find Food 🍴")

# ==============================================================================
# CORE APP LOGIC
# ==============================================================================

# This block runs only when the user submits the search form
if search_button and location_input:
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key: 
        st.error("Missing Google API key. Please add it to your .streamlit/secrets.toml file.")
    else:
        with st.spinner("Finding tasty spots..."):
            # Determine the search term, using the randomizer if needed
            search_term = craving_input.strip()
            if not search_term:
                choices = ["sushi", "burgers", "pasta", "thai", "mexican", "pizza", "ramen"]
                st.session_state.recommendation = random.choice(choices)
                search_term = st.session_state.recommendation
            else:
                st.session_state.recommendation = None
            
            # Fetch data from the API and reset the session state for a new search
            st.session_state.results = search_places(api_key, search_term, location_input)
            random.shuffle(st.session_state.results)
            st.session_state.index = 0
            st.session_state.favorites = []
            st.rerun()

# ==============================================================================
# DYNAMIC UI RENDERING (RESULTS & FAVORITES)
# ==============================================================================

# Set up the main two-column layout
main_col, sidebar_col = st.columns([2, 1])

# --- Main Column (Swipe Card) ---
with main_col:
    if st.session_state.results:
        # Display the randomizer recommendation if applicable
        if st.session_state.recommendation:
            st.success(f"CraveBot Recommends: **{st.session_state.recommendation.title()}!**")
        
        index, total = st.session_state.index, len(st.session_state.results)
        
        if index < total:
            # Display the current restaurant card
            item = st.session_state.results[index]
            api_key = st.secrets.get("GOOGLE_API_KEY")
            name = item.get("name", "N/A")
            rating = item.get("rating", "N/A")
            address = item.get("vicinity", "N/A")
            maps_link = create_google_maps_link(name, address)
            craving_for_image = st.session_state.recommendation or craving_input or 'food'
            
            image_url = get_valid_image_url(item, api_key, craving_for_image)

            st.markdown(f"""
                <div class="food-card">
                    <a href="{maps_link}" target="_blank"><img src="{image_url}" alt="{name}"></a>
                    <a href="{maps_link}" target="_blank"><h2>{name}</h2></a>
                    <p><b>⭐ {rating}</b> &nbsp;·&nbsp; {address}</p>
                </div>
            """, unsafe_allow_html=True)

            # Display the "Crave" and "Next" buttons
            b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([2, 1, 1, 1, 2])
            with b_col2:
                if st.button("❤️", help="Crave it!"):
                    st.session_state.favorites.append(item)
                    st.session_state.index += 1
                    st.rerun()
            with b_col4:
                if st.button("➡️", help="Next"):
                    st.session_state.index += 1
                    st.rerun()
        else:
            # Display a message when the user has swiped through all results
            st.success("🎉 You've swiped through all the results!")
            st.info("Check your Crave List on the right to see your picks.")
    else:
        # Display an initial message if no search has been performed yet
        st.info("Enter a location to start swiping for food!")

# --- Sidebar Column (Favorites List) ---
with sidebar_col:
    display_favorites()

# ==============================================================================
# END OF APP
# ==============================================================================