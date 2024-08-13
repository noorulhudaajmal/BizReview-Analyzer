import json

import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from wordcloud import WordCloud

from utils import insert_sentiment_scores
import numpy as np
import streamlit as st
import requests


COLORS = ["#0081a7", "#00afb9", "#f07167", "#e9c46a", "#264653",
          "#f4a261", "#e76f51", "#ef233c", "#fed9b7", "#f6bd60",
          "#84a59d", "#f95738", "#fdfcdc", ]


def update_layout(fig: go.Figure, x_label: str, y_label: str, title: str) -> go.Figure:
    """
    Updates the layout of a Plotly figure with specified labels and title.

    :param fig: plotly fig to be updated
    :param x_label: title for x-axis
    :param y_label: title for y-axis
    :param title: title for the plotly fig
    :return: The updated Plotly figure
    """
    fig = fig.update_layout(xaxis_title=x_label, yaxis_title=y_label,
                            title=title,
                            hovermode="x unified",
                            hoverlabel=dict(
                                bgcolor="white",
                                font_color="black",
                                font_size=16,
                                font_family="Rockwell"
                            )
                            )
    return fig


def reviews_wordcloud(df: pd.DataFrame) -> plt.figure:
    """
    Generate a word cloud to visualize frequent words in a DataFrame of reviews.

    :param df: The input DataFrame containing review data.
    :return: A matplotlib figure representing the word cloud
    """
    wordcloud = WordCloud(background_color='white', min_font_size=5)

    text = ' '.join(df['text'])
    if len(text) == 0:
        text = 'Null'

    wordcloud.generate(text)

    # Convert the word cloud to an image
    fig = plt.figure(facecolor=None)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=10)
    plt.title("Frequent Words in Reviews")

    return fig


def average_rating_overtime(df):
    """
    Function to plot Bar Chart to visualize average rating
    w.r.t Quarters for each year
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing average distribution overtime.
    """
    # Calculate the length of each review
    df['year'] = df['datetime'].dt.year
    df['quarter'] = df['datetime'].dt.quarter

    # Calculate average rating for each year and quarter
    avg_rating = df.groupby(['year', 'quarter'])['rating'].mean().reset_index()

    # Create a Plotly Go figure
    fig = go.Figure()

    # Add a bar trace for each quarter
    for quarter in range(1, 5):
        quarter_data = avg_rating[avg_rating['quarter'] == quarter]
        fig.add_trace(go.Bar(
            x=quarter_data['year'],
            y=quarter_data['rating'],
            name=f'Quarter {quarter}',
            marker=dict(color=COLORS[quarter])
        ))

    # Customize the layout
    fig.update_layout(barmode='group', legend=dict(title='Quarter'))

    fig = update_layout(fig, "Time", "Average Rating", "Average Rating overtime")
    return fig


def average_rating_wrt_month_year(df):
    """
    Function to plot Bar Chart to visualize average rating
    w.r.t Months for each year
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing average distribution overtime.
    """
    df['year'] = df['datetime'].dt.year
    df['month_num'] = df['datetime'].dt.month
    df['month_year'] = df['datetime'].dt.strftime("%b %Y")

    # Calculate average rating for each year and month
    avg_rating = df.groupby(['year', 'month_num', 'month_year'])['rating'].mean().reset_index()

    # Create a Plotly go figure
    fig = go.Figure()

    years = sorted(list(avg_rating['year'].unique()))
    # Add a bar trace for each month
    ind = 0
    for year in years:
        year_data = avg_rating[avg_rating['year'] == year]
        year_data.sort_values(by='month_num', inplace=True)
        fig.add_trace(go.Bar(
            x=year_data['month_year'],
            y=year_data['rating'],
            name=f'{year}',
            marker=dict(color=COLORS[ind])
        ))
        ind+=1

    # Customize the layout
    fig.update_layout(barmode='group', legend=dict(title='Year'))

    fig = update_layout(fig, "Time", "Average Rating", "Average Rating overtime w.r.t Month-Year")
    return fig


def rating_breakdown_pie(df: pd.DataFrame) -> go.Figure:
    """
    Generate a pie chart to visualize the breakdown of reviews by rating.
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing the breakdown of reviews by rating.
    """
    df = df.groupby("rating")["text"].count().reset_index()
    df["rating"] = df["rating"].astype(int)
    df["Rating-Formatted"] = df["rating"].map({
        5: "⭐ 5 😊", 4: "⭐ 4 🙂", 3: "⭐ 3 😕", 2: "⭐ 2 😒", 1: "⭐ 1 😑"
    })
    df.sort_values(by="rating", ascending=True, inplace=True)
    fig = go.Figure(
        go.Pie(
            labels=df["Rating-Formatted"],
            values=df["text"],
            hole=0.3,
            sort=False
        )
    )
    fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=15,
                      marker=dict(colors=COLORS))
    fig = update_layout(fig, "Rating", "Review Count", "Rating Distribution")

    return fig


def sentiment_score_overtime(df):
    """
    Function to plot a scatter chart to visualize sentiment score
    w.r.t time
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing sentiment score overtime.
    """
    df = insert_sentiment_scores(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["sentiment_score"],
            name="Sentiment Score",
            mode="markers",
            marker=dict(color="#84a59d", size=20),
        )
    )
    fig.add_hrect(y0=0.05, y1=1.05, line_width=0, fillcolor="#57cc99", opacity=0.2)
    fig.add_hrect(y0=-0.05, y1=-1.05, line_width=0, fillcolor="#ef233c", opacity=0.2)

    fig = update_layout(fig, "Time", "Sentiment Score", "Sentiment Score Analytics")

    return fig


def place_choropleth(df, country):
    """
    Function to plot a choropleth-like map based on average rating using latitude and longitude.
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure showing rating density per region.
    """
    url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    geo = requests.get(url).json()

    df["country"] = country

    # Calculate the average latitude and longitude for centering the map
    avg_lat = df['latitude'].mean()
    avg_lon = df['longitude'].mean()

    # Geographic Map
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=geo,
            locations=df["country"],
            featureidkey="properties.name",
            z=df["averageRating"],
            colorscale="sunsetdark",
            marker_opacity=0.8,
            marker_line_width=1,
        )
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=6,
        mapbox_center={"lat": avg_lat, "lon": avg_lon},
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title="Geographical Distribution of Ratings",
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
            font_family="Rockwell"
        )
    )

    return fig


def top_performing_places(df):
    """
    Function to plot a bar chart of top-performing places based on reviews, ratings, and reliability.
    :param df: The input DataFrame containing review data.
    :return: A Plotly Figure representing top places with their satisfaction and reliability scores.
    """
    # Drop rows with missing average ratings
    df = df.dropna(subset=["averageRating"])

    # Aggregate data by place name
    df = df.groupby("name").agg({
        "averageRating": "mean",
        "totalReviews": "sum"
    }).reset_index()

    # Filter places with total reviews above the average
    thresh = df["totalReviews"].quantile(0.50)
    df = df[df["totalReviews"] >= thresh]

    # Calculate Satisfaction Score
    df['Satisfaction Score'] = (df['averageRating'] * df['totalReviews']) / df['totalReviews'].sum()
    max_score = df['Satisfaction Score'].max()
    df['Relative Satisfaction Score'] = (df['Satisfaction Score'] / max_score) * 100

    # Calculate Reliability Score
    df['Reliability Score'] = df['averageRating'] * np.log1p(df['totalReviews'])

    # Sort places by Relative Satisfaction Score
    df.sort_values(by="Relative Satisfaction Score", ascending=False, inplace=True)

    # Select top 30 places
    top_places = df.head(30)

    # Create bar chart
    fig = go.Figure()

    # Add Relative Satisfaction Score bars
    fig.add_trace(
        go.Bar(
            x=top_places["name"],
            y=top_places["Relative Satisfaction Score"],
            marker=dict(color="#2a9d8f"),
            name="Satisfaction Score",
            text=top_places["Relative Satisfaction Score"].round(2).astype(str) + " %",
            hovertext=(
                    "Rating: " + top_places["averageRating"].astype(str) + " stars<br>" +
                    "Total Reviews: " + top_places["totalReviews"].astype(str) + "<br>" +
                    "Satisfaction Score: " + top_places["Satisfaction Score"].round(4).astype(str)
            ),
            hoverinfo="text"
        )
    )

    # Add Reliability Score bars
    fig.add_trace(
        go.Scatter(
            x=top_places["name"],
            y=top_places["Reliability Score"],
            marker=dict(color="#e9c46a"),
            name="Reliability Score",
            text=top_places["Reliability Score"].round(2).astype(str),
            hovertext=(
                    "Rating: " + top_places["averageRating"].astype(str) + " stars<br>" +
                    "Total Reviews: " + top_places["totalReviews"].astype(str) + "<br>" +
                    "Reliability Score: " + top_places["Reliability Score"].round(4).astype(str)
            ),
            hoverinfo="text",
        )
    )

    # Update layout
    fig.update_layout(
        height=500,
        xaxis_title="Score",
        yaxis_title="Place",
        hovermode ="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
            font_family="Rockwell"
        )
    )

    return fig