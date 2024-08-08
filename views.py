import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu
import requests
from css.streamlit_style_const import STYLE
from template.html import POPUP
from constants import icons_map
from utils import *


def map_view(business_place, location: str, API_KEY: str):
    """
    Creates a Folium map with markers for pharmacies based on the provided DataFrame.

    :param API_KEY: Google Maps API key
    :param location: The user selected location
    :param data: The DataFrame containing pharmacy data.
    :return: The Folium map with pharmacy markers.
    """

    # Initialize an empty DataFrame to hold the pharmacy data
    pharmacy_data = pd.DataFrame()

    # Placeholder for displaying the map
    # map_placeholder = st.empty()
    lat, lon = get_location_coordinates(location)
    # Initialize the map
    pharmacies_map = folium.Map(location=[lat, lon], zoom_start=7, control_scale=True, prefer_canvas=True)

    # Display the initial map
    map_placeholder = folium_static(pharmacies_map, width=1000, height=600)

    with st.spinner("Loading..."):
        for partial_pharmacy_data, _ in get_pharmacy_and_review_data(API_KEY, business_place, location):
            # Append new data to the existing DataFrame
            pharmacy_data = pd.concat([pharmacy_data, partial_pharmacy_data], ignore_index=True)

            # Update the map with the new pharmacy data
            for i, row in partial_pharmacy_data.iterrows():
                iframe = folium.IFrame(POPUP.format(
                    str(row['photo_url']),
                    str(row["name"]),
                    str(row["address"]),
                    str(row["averageRating"]),
                    str(row["totalReviews"]),
                    row["contact"]
                ), width=300, height=250)
                popup = folium.Popup(iframe, min_width=150, max_width=300)

                # Add each row to the existing map
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    tooltip=row["name"],
                    icon=folium.Icon(color=row['markerColor'], icon=icons_map.get(business_place), prefix='fa'),
                    popup=popup,
                ).add_to(pharmacies_map)

            # Update the map display with the new markers
            map_placeholder.empty()  # Clear previous map
            map_placeholder = folium_static(pharmacies_map, width=1000, height=600)

