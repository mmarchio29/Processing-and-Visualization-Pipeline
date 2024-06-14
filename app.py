import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Data
file_path = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\Capitalism.xlsx'
df = pd.read_excel(file_path)

# Convert the 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
df['Year'] = df['Date'].dt.year

# Define positive and negative sentiments
positive_sentiments = ['Happiness', 'Love', 'Surprise']
negative_sentiments = ['Anger', 'Disgust', 'Fear', 'Sadness']

# Positive/Negative scores 
df['Positive'] = df[positive_sentiments].mean(axis=1)
df['Negative'] = df[negative_sentiments].mean(axis=1)

# Initialize the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Sentiment Analysis Visualization"),
    
    html.Div([
        html.Label("Source Type:"),
        dcc.Dropdown(
            id='source-type-dropdown',
            options=[{'label': st, 'value': st} for st in df['Source Type'].unique()],
            value=df['Source Type'].unique()[0],
            clearable=False
        ),
    ], style={'width': '22%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("City:"),
        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in df['City'].unique()],
            value=df['City'].unique()[0],
            clearable=False
        ),
    ], style={'width': '22%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Publisher:"),
        dcc.Dropdown(
            id='publisher-dropdown',
            options=[{'label': publisher, 'value': publisher} for publisher in df['Publication'].unique()],
            value=df['Publication'].unique()[0],
            clearable=False
        ),
    ], style={'width': '22%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Year Range:"),
        dcc.RangeSlider(
            id='year-slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=[df['Year'].min(), df['Year'].max()],
            marks={str(year): str(year) for year in range(df['Year'].min(), df['Year'].max() + 1, 2)},
            step=1
        ),
    ], style={'width': '90%', 'padding': '20px'}),
    
    dcc.Graph(id='sentiment-line-graph')
])

@app.callback(
    Output('sentiment-line-graph', 'figure'),
    Input('source-type-dropdown', 'value'),
    Input('city-dropdown', 'value'),
    Input('publisher-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_graph(selected_source, selected_city, selected_publisher, selected_years):
    # Debugging: Print the selected filter values
    print(f"Selected Source Type: {selected_source}")
    print(f"Selected City: {selected_city}")
    print(f"Selected Publisher: {selected_publisher}")
    print(f"Selected Year Range: {selected_years}")

    filtered_df = df[(df['Source Type'] == selected_source) & 
                     (df['City'] == selected_city) & 
                     (df['Publication'] == selected_publisher) & 
                     (df['Year'] >= selected_years[0]) & 
                     (df['Year'] <= selected_years[1])]
    
    # Debugging: Print the shape of the filtered DataFrame
    print(f"Filtered DataFrame shape: {filtered_df.shape}")

    # Filter to include only numeric columns for resampling
    numeric_columns = ['Positive', 'Negative']
    filtered_df_numeric = filtered_df[['Date'] + numeric_columns]

    # Debugging: Check if filtered DataFrame is empty
    if filtered_df_numeric.empty:
        print("Filtered DataFrame is empty. No data available for the selected filters.")
        return px.line(title="No data available for the selected filters.")

    # Set the index to the 'Date' column
    filtered_df_numeric = filtered_df_numeric.set_index('Date')

    # Resample by year
    yearly_sentiments = filtered_df_numeric.resample('Y').mean().reset_index()

    # Debugging: Print the head of the yearly sentiments DataFrame
    print(f"Yearly Sentiments DataFrame head:\n{yearly_sentiments.head()}")

    fig = px.line(yearly_sentiments, x='Date', y=numeric_columns,
                  labels={'Date': 'Year', 'value': 'Sentiment Score', 'variable': 'Sentiment'},
                  title=f'Sentiment Trends for {selected_source} in {selected_city} by {selected_publisher} from {selected_years[0]} to {selected_years[1]}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
