import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu
import requests
from css.streamlit_style_const import STYLE
from template.html import POPUP
from utils import *
from views import map_view
from constants import query_map

# ------------------------------ Page Configuration------------------------------
st.set_page_config(page_title="BizReview Analysis", page_icon="📊", layout="wide")

# ----------------------------------- Page Styling ------------------------------

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown(STYLE, unsafe_allow_html=True)

API_KEY = st.secrets["API_KEY"]

# --------------------------------------------------------------------------------

business_place = st.sidebar.selectbox(label="Business", options=list(query_map.keys()))
location = st.sidebar.selectbox(label="Location", options=["Pakistan", "Switzerland", "India"])

# --------------------------------------------------------------------------------

def main():
    # ----- Menu -----
    menu = option_menu(menu_title=None, menu_icon=None, orientation="horizontal",
                       options=["Pharmacies Map", "List View", "Reviews Analytics", "Market Analysis"],
                       icons=['map', 'view-list', 'bar-chart', 'graph-up-arrow']
                       )

    # ----- Tab for Map View -----
    if menu == "Pharmacies Map":
        map_view(business_place, location, API_KEY)
    # ----- Tab for List View -----
    # elif menu == "List View":
    #     list_view()
    # # ----- Tab for Reviews Analysis -----
    # elif menu == "Reviews Analytics":
    #     review_analytics_page()
    #
    # # ----- Tab for Pharmaceutical Market Analysis -----
    # elif menu == "Market Analysis":
    #     market_analysis_page()


    # --------------------------------------------------------------------------------


if __name__ == "__main__":
    main()