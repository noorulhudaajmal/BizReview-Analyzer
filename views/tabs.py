from views.views import map_view, review_analytics_page, list_view, market_analysis_page
from views.components import sidebar_business_place, sidebar_country, sidebar_city
from data_handling import get_stored_data, update_data_store
from utils import get_cities_names
import streamlit as st


def places_map_tab(query_map, geo_plug, API_KEY):
    business_place = sidebar_business_place(query_map)
    countries_list = geo_plug.all_CountryNames()
    country = sidebar_country(countries_list)
    cities_list = get_cities_names(country)
    city = sidebar_city(cities_list)

    map_view(business_place, country, city, API_KEY)
    update_data_store(city, country, business_place)


def list_view_tab(API_KEY):
    stored_data = get_stored_data()

    business_place = st.sidebar.selectbox(label="Business", options=list(stored_data['Business Point'].unique()))
    country = sidebar_country(stored_data[stored_data['Business Point']==business_place]['Country'].unique())
    city = sidebar_city(stored_data[(stored_data['Business Point'] == business_place) &
                                    (stored_data['Country'] == country)]['City'].unique())

    list_view(business_place, country, city, API_KEY)


def reviews_analytics_tab():
    stored_data = get_stored_data()
    stored_data = stored_data[stored_data['Reviews'] == 1]
    if len(stored_data) != 0:
        business_place = st.sidebar.selectbox(label="Business", options=list(stored_data['Business Point'].unique()))
        country = sidebar_country(stored_data[stored_data['Business Point']==business_place]['Country'].unique())
        city = sidebar_city(stored_data[(stored_data['Business Point'] == business_place) &
                                        (stored_data['Country'] == country)]['City'].unique())

        review_analytics_page(location=f'{city},+{country}', business_place=business_place)
    else:
        st.info("Go to previous tabs to load reviews first.")


def market_analysis_tab():
    stored_data = get_stored_data()
    if len(stored_data) != 0:
        business_place = st.sidebar.selectbox(label="Business", options=list(stored_data['Business Point'].unique()))
        country = sidebar_country(stored_data[stored_data['Business Point']==business_place]['Country'].unique())
        city = sidebar_city(stored_data[(stored_data['Business Point'] == business_place) &
                                        (stored_data['Country'] == country)]['City'].unique())

        market_analysis_page(location=f'{city},+{country}', business_place=business_place)
    else:
        st.info("Go to Home to load data first.")
