import requests
import pandas as pd
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from geosky import geo_plug
import json
import time
# from textblob_de import TextBlobDE
# from textblob_fr import PatternAnalyzer
from textblob import TextBlob
import nltk

nltk.download('punkt')


def get_cities_names(location):
    states_data = json.loads(geo_plug.all_Country_StateNames())

    # Find states for the selected country
    states = []
    for entry in states_data:
        if location in entry:
            states = entry[location]
            break

    cities = set()
    # st.write(states_data)
    for state in states:
        cities_data = json.loads(geo_plug.all_State_CityNames(state))
        for entry in cities_data:
            if state in entry:
                cities.update(entry[state])
                break

    return cities


def fetch_place_details(api_key, result, location, i):
    place_id = result['place_id']

    # Place Details
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,geometry,international_phone_number,rating,user_ratings_total,reviews&key={api_key}"
    details_response = requests.get(details_url)
    details_data = details_response.json()

    # Extract place information
    place_info = {
        'address': result.get('formatted_address', ''),
        'averageRating': details_data['result'].get('rating', ''),
        'city': location,
        'contact': details_data['result'].get('international_phone_number', ''),
        'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'id': str(i+1),
        'latitude': result['geometry']['location'].get('lat', ''),
        'longitude': result['geometry']['location'].get('lng', ''),
        'name': result.get('name', ''),
        'totalReviews': details_data['result'].get('user_ratings_total', ''),
        'place_id': result.get('place_id', ''),
    }
    # Extract the photo_reference and construct the photo URL
    photo_reference = result.get("photos", [{}])[0].get("photo_reference", "")
    if photo_reference:
        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=100&photoreference={photo_reference}&key={api_key}"
        place_info['photo_url'] = photo_url
    else:
        place_info['photo_url'] = None

    return place_info


def get_places_data(api_key, business_place, location, n=20):
    places_list = []
    next_page_token = None

    while len(places_list) < n:
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
                executor.submit(fetch_place_details, api_key, result, location, len(places_list) + i)
                for i, result in enumerate(search_data['results'])
            ]

            for future in futures:
                place_info = future.result()
                places_list.append(place_info)

                df_places_info = pd.DataFrame(places_list)

                df_places_info = pre_process_listings_data(df_places_info)
                yield df_places_info

        next_page_token = search_data.get('next_page_token', None)
        if not next_page_token:
            break

        # To prevent hitting API rate limits
        time.sleep(2)  # Delay for 2 seconds before making the next request

        if len(places_list) >= n:
            break

    # Convert lists to DataFrames
    df_places = pd.DataFrame(places_list)

    df_places = pre_process_listings_data(df_places)

    return df_places


def get_place_reviews(api_key, result):
    place_id = result['place_id']

    # Place Details
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,geometry,international_phone_number,rating,user_ratings_total,reviews&key={api_key}"
    details_response = requests.get(details_url)
    details_data = details_response.json()

    # Extract reviews
    reviews_list = []
    reviews = details_data['result'].get('reviews', [])
    for j, review in enumerate(reviews):
        # epoch time to timezone-aware datetime string
        review_time = datetime.fromtimestamp(review.get('time', 0), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        review_info = {
            'place_id': result.get('id'),
            'datetime': review_time,
            'id': str(j+1),
            'place_Name': result.get('name', ''),
            'rating': review.get('rating', ''),
            'reviewer': review.get('author_name', ''),
            'serial_Number': str(j+1),
            'text': review.get('text', ''),
            'photo_url': review.get('profile_photo_url', None),
            'language': review.get('language', '')
        }
        reviews_list.append(review_info)

    if len(reviews) != 0:
        return pre_process_reviews(pd.DataFrame(reviews_list))
    else:
        return pd.DataFrame()


def pre_process_listings_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-processes place listings data.
    :param data: The input DataFrame containing place listings data.
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
    data["adjustedReview"] = data["totalReviews"].apply(adjusted_reviews)
    data["adjustedRating"] = data["averageRating"].apply(lambda x: int(x // 1))
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


def calculate_sentiment_score(row: pd.Series):
    """
    Function to calculate sentiment score of a review.
    of ratings to corresponding integer representation
    :param row: Series containing text and language of the review
    :return: None
   """
    text = row['text']
    lang = row['language']

    # worst-case: text has no words or language other than English
    if len(text) == 0 or lang not in ['en']:
        rating = row['rating']
        if rating == 5:
            return 1
        elif rating == 4:
            return 0.5
        elif rating == 3:
            return 0
        elif rating == 2:
            return -0.5
        elif rating == 1:
            return -1
    else:
        return TextBlob(text).sentiment.polarity
    # # calculating sentiment score based on language
    # if lang in ['en', 'de', 'fr']:
    #     if lang == 'en':
    #         return TextBlob(text).sentiment.polarity
    #     elif lang == 'de':
    #         return TextBlobDE(text).sentiment.polarity
    #     elif lang == 'fr':
    #         return TextBlob(text, analyzer=PatternAnalyzer()).sentiment[0]

    return None


def insert_sentiment_scores(df):
    """
    Function to insert sentiment score column
    to a dataframe containing review text.
    :param df: dataframe containing reviews data
    :return: dataframe with added column representing sentiment scores.
    """

    df['sentiment_score'] = df.apply(calculate_sentiment_score, axis=1)

    return df


def calculate_kpis(place_data, place_reviews):
    """
    Function to calculate KPI values
    :param place_reviews: dataframe of reviews
    :param place_data: dataframe containing info of the place
    :return: KPIs values
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
