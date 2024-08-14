import streamlit as st
from css.streamlit_style_const import STYLE
from streamlit_option_menu import option_menu
from views.tabs import places_map_tab, list_view_tab, reviews_analytics_tab, market_analysis_tab
from template.constants import query_map
from utils import *
import pandas as pd

# Page Configuration
st.set_page_config(page_title="BizReview Analysis", page_icon="📊", layout="wide")

# Page Styling
try:
    with open("css/style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
    st.markdown(STYLE, unsafe_allow_html=True)
except FileNotFoundError:
    st.error("The CSS file was not found. Please ensure the file exists.")
except Exception as e:
    st.error(f"An error occurred while applying styles: {str(e)}")

# Global Variable
try:
    API_KEY = st.secrets["API_KEY"]
except KeyError:
    st.error("API Key is missing in the secrets configuration. Please add it to your secrets.")
except Exception as e:
    st.error(f"An error occurred while accessing the API key: {str(e)}")


def initialize_session_state():
    try:
        if 'data_store' not in st.session_state:
            st.session_state['data_store'] = pd.DataFrame(columns=['City', 'Country', 'Business Point', 'Reviews'])
    except Exception as e:
        st.error(f"An error occurred during session state initialization: {str(e)}")


def main():
    # Initialize session state
    initialize_session_state()

    # Menu
    menu = option_menu(menu_title=None, menu_icon=None, orientation="horizontal",
                       options=["Places Map", "List View", "Reviews Analytics", "Market Analysis"],
                       icons=['map', 'view-list', 'bar-chart', 'graph-up-arrow'])

    # Handling tabs
    try:
        if menu == "Places Map":
            places_map_tab(query_map, geo_plug, API_KEY)
        elif menu == "List View":
            list_view_tab(API_KEY)
        elif menu == "Reviews Analytics":
            reviews_analytics_tab()
        elif menu == "Market Analysis":
            market_analysis_tab()
    except Exception as e:
        st.error(f"An error occurred while rendering the selected tab: {str(e)}")


if __name__ == "__main__":
    main()
