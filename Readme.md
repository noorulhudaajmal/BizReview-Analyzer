# BizReview Analyzer
BizReview Analysis is a Streamlit-based web application designed to provide insights into various business points by analyzing reviews. Users can visualize data on a map, list view, perform reviews analytics, and conduct market analysis based on location and business type.

## Pages
1. **Map View:** It visualizes business locations on an interactive map.
2. **List View:** Display a detailed list of business points along with reviews w.r.t location.
3. **Reviews Analytics:** Provide various analytics of customer reviews for selected business and location.
4. **Market Analysis:** Conduct market comparison analytics of various businesses at certain location.

## Installation
### Prerequisites
- Python 3.7 or higher
- A valid *Google Places API* Key for accessing places data

### Clone the Repository
```shell
git clone https://github.com/noorulhudaajmal/BizReview-Analyzer.git
cd BizReview-Analyzer-master
```

### Install Dependencies
```shell
pip install -r requirements.txt
```

### Set Up Secrets
- Add a secrets.toml file to .streamlit directory.
- In .streamlit/secrets.toml, add your Google API key:
```toml
API_KEY = "google_places_api_key"
```

### Run the Application
```shell
streamlit run app.py
```

## Usage
- **Select a Tab:** Use the horizontal menu to select the desired tab: Places Map, List View, Reviews Analytics, or Market Analysis.
- **Choose a Business and Location:** Depending on the tab, use the sidebar to select a business type and location (country and city).
- **View Insights:** Visualize the selected data on a map, list view, or analytics pages.

*For analytics of a location, the Map View and List View needs to be rendered first as data loading is done there*

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

---