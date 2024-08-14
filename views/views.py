import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
from plots import average_rating_overtime, rating_breakdown_pie, sentiment_score_overtime, reviews_wordcloud, \
    average_rating_wrt_month_year, top_performing_places, folium_marker_map, spatial_dist_of_business_points
from template.html import POPUP, review_card, card_view
from template.constants import icons_map
from utils import get_places_data, get_place_reviews, calculate_kpis


@st.cache_data
def map_view(business_place, country: str, city: str, API_KEY: str):
    """
    Creates a Folium map with markers for places based on the provided DataFrame.

    :param city: name of city
    :param country: name of country
    :param business_place: type of business
    :param API_KEY: Google Maps API key
    :return: The Folium map with place markers.
    """

    location = f"{city},+{country}"

    # Initialize an empty DataFrame to hold the place data
    place_data = pd.DataFrame()

    # Placeholder for displaying the map
    # map_placeholder = st.empty()
    # Initialize the map
    places_map = folium.Map(location=[0, 0], zoom_start=10, control_scale=True, prefer_canvas=True)

    # Display the initial map
    map_placeholder = folium_static(places_map, width=1000, height=600)

    with st.spinner("Loading..."):
        for partial_place_data in get_places_data(API_KEY, business_place, location=location):
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

            places_map.fit_bounds(places_map.get_bounds())

            # Update the map display with the new markers
            map_placeholder.empty()  # Clear previous map
            map_placeholder = folium_static(places_map, width=1200, height=600)

    st.session_state[f'{location}-{business_place}-data'] = place_data




@st.cache_data
def list_view(business_place, country, city, API_KEY: str):
    """
    Function to create a view to list places.
    Data view in list with place detail on left and its reviews on right.

    :param city: name of city
    :param country: name of country
    :param business_place: type of business
    :param API_KEY: Google Maps API key
    :return: streamlit view
    """
    location=f'{city},+{country}'
    place_data = st.session_state[f'{location}-{business_place}-data']
    reviews_data = pd.DataFrame()

    for _, place in place_data.iterrows():
        upper_row = st.columns(2)
        with upper_row[0]:
            st.markdown(card_view(place["name"], place["address"], place['photo_url'],
                                      f"{place['averageRating']:.1f}", place["totalReviews"],
                                      place["contact"]),
                            unsafe_allow_html=True)

        place_reviews = get_place_reviews(api_key=API_KEY, result=place)
        reviews_data = pd.concat([reviews_data, place_reviews])
        with upper_row[1]:
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

    st.session_state['data_store'].loc[
        (st.session_state['data_store']["City"] == city) &
        (st.session_state['data_store']["Country"] == country) &
        (st.session_state['data_store']["Business Point"] == business_place),
        "Reviews"
    ] = 1

    st.session_state[f'{location}-{business_place}-reviews'] = reviews_data


def review_analytics_page(location, business_place):
    """
    Function to show review analytics for a place

    :param location: name of city and country
    :param business_place: type of business

    :return: Streamlit frame/view
    """
    place_data = st.session_state[f'{location}-{business_place}-data']
    reviews_data = st.session_state[f'{location}-{business_place}-reviews']

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

    charts_row_1 = st.columns((4, 3))
    # Reviews Distribution w.r.t Quarter-Year
    charts_row_1[0].plotly_chart(average_rating_overtime(reviews_data), use_container_width=True)
    # Rating distribution pie
    charts_row_1[1].plotly_chart(rating_breakdown_pie(reviews_data), use_container_width=True)

    charts_row_2 = st.columns((3, 4))
    # sentiment score over the time
    charts_row_2[0].plotly_chart(sentiment_score_overtime(reviews_data), use_container_width=True)
    # rating over the time
    charts_row_2[1].plotly_chart(average_rating_wrt_month_year(reviews_data), use_container_width=True)
    # Wordcloud of review text
    st.pyplot(reviews_wordcloud(reviews_data), clear_figure=True, use_container_width=True)


@st.cache_resource
def market_analysis_page(location, business_place):
    """
    Function to create view for the 'Market Analysis' tab
    :return: Analytics charts
    """
    place_data = st.session_state[f'{location}-{business_place}-data']

    cols = st.columns(2)
    with cols[0]:
        st.write("#### Geographical Distribution of Ratings")
        folium_marker_map(place_data)
    with cols[1]:
        st.write("#### Geographical Clusters of Business Points")
        spatial_dist_of_business_points(place_data)

    st.plotly_chart(top_performing_places(place_data), use_container_width=True)




