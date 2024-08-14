import streamlit as st

def sidebar_business_place(query_map):
    return st.sidebar.selectbox(label="Business", options=list(query_map.keys()))

def sidebar_country(countries_list):
    return st.sidebar.selectbox(label="Location", options=countries_list)

def sidebar_city(cities_list):
    return st.sidebar.selectbox(label="City", options=sorted(cities_list))
