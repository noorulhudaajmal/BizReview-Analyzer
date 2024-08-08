import requests
import pandas as pd
from typing import Tuple
import folium
from template.html import POPUP
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from geopy.geocoders import Nominatim
import streamlit as st
from constants import query_map

# Initialize Nominatim geocoder
geolocator = Nominatim(user_agent="Biz-Reviews-Analyzer")


def fetch_pharmacy_details(api_key, result, location, i):
    place_id = result['place_id']

    # Place Details
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,geometry,international_phone_number,rating,user_ratings_total,reviews&key={api_key}"
    details_response = requests.get(details_url)
    details_data = details_response.json()

    # Extract pharmacy information
    pharmacy_info = {
        'address': result.get('formatted_address', ''),
        'averageRating': details_data['result'].get('rating', ''),
        'city': location,
        'contact': details_data['result'].get('international_phone_number', ''),
        'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'id': str(i+1),
        'latitude': result['geometry']['location'].get('lat', ''),
        'longitude': result['geometry']['location'].get('lng', ''),
        'name': result.get('name', ''),
        'totalReviews': details_data['result'].get('user_ratings_total', '')
    }
    # Extract the photo_reference and construct the photo URL
    photo_reference = result.get("photos", [{}])[0].get("photo_reference", "")
    if photo_reference:
        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=100&photoreference={photo_reference}&key={api_key}"
        pharmacy_info['photo_url'] = photo_url
    else:
        pharmacy_info['photo_url'] = None

    # Extract reviews (only up to 5 due to API limitation)
    reviews_list = []
    reviews = details_data['result'].get('reviews', [])
    for j, review in enumerate(reviews):
        # Convert epoch time to timezone-aware datetime string
        review_time = datetime.fromtimestamp(review.get('time', 0), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        review_info = {
            'datetime': review_time,
            'id': review.get('review_id', ''),
            'place_Name': result.get('name', ''),
            'rating': review.get('rating', ''),
            'reviewer': review.get('author_name', ''),
            'serial_Number': str(j+1),
            'text': review.get('text', '')
        }
        reviews_list.append(review_info)

    return pharmacy_info, reviews_list


def get_pharmacy_and_review_data(api_key, business_place, location, n=60):
    pharmacies_list = []
    all_reviews_list = []
    next_page_token = None


    while len(pharmacies_list) < n:
        # Place Search with pagination support
        search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={business_place}+in+{location}&key={api_key}"
        if next_page_token:
            search_url += f"&pagetoken={next_page_token}"

        search_response = requests.get(search_url)
        search_data = search_response.json()

        if 'results' not in search_data:
            break

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(fetch_pharmacy_details, api_key, result, location, len(pharmacies_list) + i)
                for i, result in enumerate(search_data['results'])
            ]

            for future in futures:
                pharmacy_info, reviews_list = future.result()
                pharmacies_list.append(pharmacy_info)
                all_reviews_list.extend(reviews_list)

                df_pharmacies_info = pd.DataFrame(pharmacies_list)
                df_review_list = pd.DataFrame(all_reviews_list)

                df_pharmacies_info, df_review_list = pre_process_data(df_pharmacies_info, df_review_list)
                yield df_pharmacies_info, df_review_list

        next_page_token = search_data.get('next_page_token', None)
        if not next_page_token:
            break

        # To prevent hitting API rate limits, you may need to introduce a delay
        import time
        time.sleep(2)  # Delay for 2 seconds before making the next request

        if len(pharmacies_list) >= n:
            break

    # Convert lists to DataFrames
    df_pharmacies = pd.DataFrame(pharmacies_list)
    df_reviews = pd.DataFrame(all_reviews_list)

    df_pharmacies, df_reviews = pre_process_data(df_pharmacies, df_reviews)

    return df_pharmacies, df_reviews


def pre_process_data(data: pd.DataFrame, reviews: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Pre-processes data related to pharmacy listings and reviews.
    :param data: DataFrame containing information about pharmacy listings.
    :param reviews: DataFrame containing reviews data.
    :return: A tuple containing pre-processed DataFrames for listings and reviews.
    """
    data = pre_process_listings_data(data)
    reviews = pre_process_reviews(reviews)
    return data, reviews


def pre_process_listings_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-processes pharmacy listings data.
    :param data: The input DataFrame containing pharmacy listings data.
    :return: Processed DataFrame with adjusted column datatypes, filled NaN values,
    added markerColor based on totalReviews, adjustedReview, and adjustedRating columns.
    """
    # data = data.transpose()
    data.reset_index(inplace=True)
    data = adjust_column_datatypes(data)
    data.fillna(0, inplace=True)
    data["markerColor"] = data["totalReviews"].apply(
        lambda x: "green" if x >= 100 else ("orange" if x >= 50 else ("lightgray" if x >= 25 else "red")))
    data["totalReviews"] = data["totalReviews"].astype(int)
    # data["city"] = data["address"].apply(lambda x: x.split(', ')[-2].split(' ')[-1])
    data["adjustedReview"] = data["totalReviews"].apply(adjusted_reviews)
    data["adjustedRating"] = data["averageRating"].apply(lambda x: int(x // 1))
    # Sort the DataFrame based on 'ranking'
    data.sort_values(by='totalReviews', inplace=True)
    data.reset_index(drop=True, inplace=True)

    return data


def adjusted_reviews(review: int) -> str:
    """
    Categorizes the number of reviews into different groups based on provided values.

    :param review: The total number of reviews.
    :return: A string indicating the category of the number of reviews.
    """
    if review >= 200:
        return "More than 200"
    elif 100 < review <= 200:
        return "100-200"
    elif 50 < review <= 100:
        return "50 to 100"
    else:
        return "Up-to 50"


def adjust_column_datatypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adjusts the data types of specified columns in the DataFrame.
    The function performs the following transformations:
        - Converts numeric columns ('averageRating', 'latitude', 'longitude', 'totalReviews', 'id') to float,
          handling errors by coercing to NaN.
        - Converts the 'createdAt' column to datetime.
        - Extracts numeric characters from the 'contact' column, ensuring it contains only digits.

    :param df: The input DataFrame.
    :return: The DataFrame with adjusted column data types.
    """
    numeric_cols = ['averageRating', 'latitude', 'longitude', 'totalReviews', 'id']
    for column in numeric_cols:
        if column == 'averageRating':
            # Convert to numeric and set non-numeric to 0
            df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0).astype('float')
        else:
            # Convert other columns to numeric with downcast to float
            df[column] = pd.to_numeric(df[column], errors='coerce', downcast='float')

    df['createdAt'] = pd.to_datetime(df['createdAt'])
    df["contact"] = df["contact"].apply(lambda x: ''.join(filter(str.isdigit, str(x))))
    return df


def pre_process_reviews(data: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-processes the reviews data by performing the following steps:

        - Transposes the DataFrame.
        - Resets the index for consistency.
        - Adjusts column datatypes.
        - Fills missing values with 0.
        - Converts the 'datetime' column to a formatted 'date' column.
        - Sorts the DataFrame by the 'datetime' column in ascending order.

    :param data: The input DataFrame containing reviews data.
    :return: The pre-processed DataFrame with transformations.
    """
    # data = data.transpose()
    data.reset_index(inplace=True)
    data = adjust_column_datatypes_of_reviews(data)
    data.fillna(0, inplace=True)
    data["date"] = data["datetime"].dt.strftime("%d-%m-%Y")
    data.sort_values(by="datetime", ascending=True, inplace=True)
    return data


def adjust_column_datatypes_of_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adjusts the data types of columns in a DataFrame related to reviews.
    This function specifically handles the following columns:
        - 'datetime': Converts to datetime format.
        - 'text': Converts to string type.
        - 'rating': Converts to numeric type with float precision.

    :param df: The input DataFrame containing review data.
    :return: The DataFrame with adjusted data types.
    """
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["text"] = df["text"].astype(str)
    df["rating"] = pd.to_numeric(df["rating"], errors='coerce', downcast='float')
    return df




def get_location_coordinates(place: str):
    # Get the latitude and longitude of the country
    location = geolocator.geocode(place)
    latitude = location.latitude
    longitude = location.longitude

    return latitude, longitude
