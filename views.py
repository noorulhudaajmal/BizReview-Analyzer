import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from template.html import POPUP, review_card, card_view
from constants import icons_map
from utils import *


@st.cache_data
def map_view(business_place, location: str, API_KEY: str):
    """
    Creates a Folium map with markers for places based on the provided DataFrame.

    :param business_place: type of business
    :param API_KEY: Google Maps API key
    :param location: The user selected location
    :return: The Folium map with place markers.
    """

    # Initialize an empty DataFrame to hold the place data
    place_data = pd.DataFrame()

    # Placeholder for displaying the map
    # map_placeholder = st.empty()
    lat, lon = get_location_coordinates(location)
    # Initialize the map
    places_map = folium.Map(location=[lat, lon], zoom_start=10, control_scale=True, prefer_canvas=True)

    # Display the initial map
    map_placeholder = folium_static(places_map, width=1000, height=600)

    with st.spinner("Loading..."):
        for partial_place_data in get_places_data(API_KEY, business_place, location):
            # Append new data to the existing DataFrame
            place_data = pd.concat([place_data, partial_place_data], ignore_index=True)

            place_data.drop_duplicates(subset=['id'], inplace=True)

            # Update the map with the new place data
            for i, row in partial_place_data.iterrows():
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
                ).add_to(places_map)

            # Update the map display with the new markers
            map_placeholder.empty()  # Clear previous map
            map_placeholder = folium_static(places_map, width=1000, height=600)

    st.session_state['places_data'] = place_data


@st.cache_data
def list_view(business_place, location: str, API_KEY: str):
    """
    Function to create a view to list places for smooth user interaction
    Data view in list with place detail on left and its reviews on right.

    :param business_place: type of business
    :param API_KEY: Google Maps API key
    :param location: The user selected location
    :return: The Folium map with place markers.
    """

    place_data = st.session_state['places_data']
    reviews_data = pd.DataFrame()

    for _, place in place_data.iterrows():
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

        place_reviews = get_place_reviews(api_key=API_KEY, result=place)
        reviews_data = pd.concat([reviews_data, place_reviews])
        with upper_row[1]:
            # st.dataframe(place_reviews)
            # place Reviews Tab
            review_bar = st.expander(label=f"Reviews ({len(place_reviews)})")
            with review_bar:
                # Update the map with the new place data
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

    st.session_state['reviews_data'] = reviews_data


def review_analytics_page():
    """
    Function to show filter, display KPIs and analytics for a place
    Functionalities:
     - Filters for choosing place by name.
     - KPIs for Total Reviews, Avg. Rating, Review Frequency and Yearly Review Rate.
     - Wordcloud to analyze frequent occurring words in reviews.
     - Plotly bar chart for analyzing average reviews w.r.t Quarters for every year.
     - Plotly Scatter chart to analyze sentiment score over the time.
     - Plotly Pie Chart to get distribution of review per rating.
    :return: Streamlit frame/view
    """
    place_data = st.session_state['places_data']
    reviews_data = st.session_state['reviews_data']

    filter_kpi_row = st.columns((3, 1, 2, 2, 2, 2))
    place = filter_kpi_row[0].selectbox("Select place", options=reviews_data["place_Name"].unique())

    place_reviews = reviews_data[(reviews_data['place_Name'] == place)]
    place_id = place_reviews['place_id'].iloc[0]
    place_data = place_data[place_data['id']==int(place_id)]

    total_reviews, average_ratings, unique_reviewers, monthly_reviews_rate = calculate_kpis(place_data, place_reviews)

    filter_kpi_row[2].metric(label="Average Rating", value=f"{average_ratings:.1f}")
    filter_kpi_row[3].metric(label="Total Reviews", value=f"{total_reviews}")
    filter_kpi_row[4].metric(label="Unique Reviewers", value=f"{unique_reviewers}")
    filter_kpi_row[5].metric(label="Reviews Rate/month", value=f"{monthly_reviews_rate:.1f}")

    # calling function to display analytics charts based on selected place
    # display_reviews_analysis(filtered_data)


def calculate_kpis(place_data, place_reviews):
    """
    Function to calculate KPI values
    :param place_reviews: dataframe of reviews
    :param place_data: dataframe containing info of the place
    :return: Tuple(int, float, float, float)
    """

    total_reviews = place_data['totalReviews'].iloc[0]
    average_ratings = place_data['averageRating'].iloc[0]
    total_years = place_reviews['datetime'].dt.year.nunique()

    earliest_date = place_reviews['datetime'].min()
    latest_date = place_reviews['datetime'].max()
    total_months = (latest_date.year - earliest_date.year) * 12 + (latest_date.month - earliest_date.month)
    monthly_reviews_rate = (total_reviews / total_months)

    unique_reviewers = place_reviews["reviewer"].nunique()

    return total_reviews, average_ratings, unique_reviewers, monthly_reviews_rate

