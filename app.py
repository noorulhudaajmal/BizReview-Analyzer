import streamlit as st
from css.streamlit_style_const import STYLE
from streamlit_option_menu import option_menu
from views.tabs import places_map_tab, list_view_tab, reviews_analytics_tab, market_analysis_tab
from template.constants import query_map
from utils import *


#  Page Configuration
st.set_page_config(page_title="BizReview Analysis", page_icon="📊", layout="wide")

# Page Styling
with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown(STYLE, unsafe_allow_html=True)

# Global Variable
API_KEY = st.secrets["API_KEY"]

def initialize_session_state():
    if 'data_store' not in st.session_state:
        st.session_state['data_store'] = pd.DataFrame(columns=['City', 'Country', 'Business Point', 'Reviews'])


def main():
    # Initialize session state
    initialize_session_state()

    # Menu
    menu = option_menu(menu_title=None, menu_icon=None, orientation="horizontal",
                       options=["Places Map", "List View", "Reviews Analytics", "Market Analysis"],
                       icons=['map', 'view-list', 'bar-chart', 'graph-up-arrow'])

    # Handle different tabs
    if menu == "Places Map":
        places_map_tab(query_map, geo_plug, API_KEY)
    elif menu == "List View":
        list_view_tab(API_KEY)
    elif menu == "Reviews Analytics":
        reviews_analytics_tab()
    elif menu == "Market Analysis":
        market_analysis_tab()


if __name__ == "__main__":
    main()