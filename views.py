import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu
import requests
from css.streamlit_style_const import STYLE
from template.html import POPUP, review_card, card_view
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
    pharmacy_data, reviews_data = pd.DataFrame(), pd.DataFrame()

    # Placeholder for displaying the map
    # map_placeholder = st.empty()
    lat, lon = get_location_coordinates(location)
    # Initialize the map
    pharmacies_map = folium.Map(location=[lat, lon], zoom_start=10, control_scale=True, prefer_canvas=True)

    # Display the initial map
    map_placeholder = folium_static(pharmacies_map, width=1000, height=600)

    with st.spinner("Loading..."):
        for partial_pharmacy_data, partial_reviews_data in get_pharmacy_and_review_data(API_KEY, business_place, location):
            # Append new data to the existing DataFrame
            pharmacy_data = pd.concat([pharmacy_data, partial_pharmacy_data], ignore_index=True)
            reviews_data = pd.concat([reviews_data, partial_reviews_data], ignore_index=True)

            pharmacy_data.drop_duplicates(subset=['id'], inplace=True)
            reviews_data.drop_duplicates(inplace=True)

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

    st.session_state['places_data'] = pharmacy_data
    st.session_state['reviews_data'] = reviews_data



def list_view(business_place, location: str, API_KEY: str):
    """
    Function to create a view to list Pharmacies for smooth user interaction
    Data view in list with pharmacy detail on left and its reviews on right.
    """

    pharmacy_data = st.session_state['places_data']
    reviews_data = st.session_state['reviews_data']

    # st.dataframe(pharmacy_data)

    for _, place in pharmacy_data.iterrows():
        upper_row = st.columns(2)
        with upper_row[0]:
            row = st.columns((2, 8))
            # card view
            # image on left
            row[0].image(place['photo_url'])
            # info on right
            row[1].markdown(card_view(place["name"], place["address"],
                                      f"{place['averageRating']:.1f}", place["totalReviews"],
                                      place["contact"]),
                            unsafe_allow_html=True)

        place_reviews = reviews_data[reviews_data['place_id']==str(int(place['id']))]
        with upper_row[1]:
            # st.dataframe(place_reviews)
            # Pharmacy Reviews Tab
            review_bar = st.expander(label=f"Reviews ({len(place_reviews)})")
            with review_bar:
                # Update the map with the new pharmacy data
                for _, review in place_reviews.iterrows():
                    row_ = st.columns((1, 6))
                    # reviewer image on left
                    row_[0].image(review['photo_url'])
                    # review detail on right
                    row_[1].markdown(review_card(review['reviewer'], review['date'],
                                                 review['rating']),
                                     unsafe_allow_html=True)
                    # review text on bottom
                    if review["text"] != "nan":
                        st.write(f"{review['text']}")
                    st.write("---")

        st.write("---")

