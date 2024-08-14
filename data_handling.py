import pandas as pd
import streamlit as st

def update_data_store(city, country, business_place):
    new_row = pd.DataFrame([{"City": city,
                             "Country": country,
                             "Business Point": business_place,
                             "Reviews": 0}])
    st.session_state['data_store'] = pd.concat([st.session_state['data_store'], new_row], ignore_index=True)
    st.session_state['data_store'].drop_duplicates(inplace=True)

def get_stored_data():
    return st.session_state['data_store']
