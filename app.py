import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Data
file_path = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Data\\final_merged_output.xlsx'
df = pd.read_excel(file_path)

# Convert the 'Date_x' column to datetime format
df['Date_x'] = pd.to_datetime(df['Date_x'])
df['Year'] = df['Date_x'].dt.year

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
            options=[{'label': 'All', 'value': 'All'}] + [{'label': st, 'value': st} for st in df['Source Type'].unique()],
            value='All',
            clearable=False
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Publisher:"),
        dcc.Dropdown(
            id='publisher-dropdown',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': publisher, 'value': publisher} for publisher in df['Publication Title'].unique()],
            value='All',
            clearable=False
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Emotions:"),
        dcc.Dropdown(
            id='emotions-dropdown',
            options=[
                {'label': 'Positive', 'value': 'Positive'},
                {'label': 'Negative', 'value': 'Negative'},
                {'label': 'Anger', 'value': 'Anger'},
                {'label': 'Disgust', 'value': 'Disgust'},
                {'label': 'Fear', 'value': 'Fear'},
                {'label': 'Sadness', 'value': 'Sadness'},
                {'label': 'Happiness', 'value': 'Happiness'},
                {'label': 'Love', 'value': 'Love'},
                {'label': 'Surprise', 'value': 'Surprise'},
                {'label': 'Neutral', 'value': 'Neutral'},
                {'label': 'Other', 'value': 'Other'}
            ],
            value=['Positive', 'Negative'],
            multi=True
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Aggregation Value:"),
        dcc.Dropdown(
            id='aggregation-dropdown',
            options=[
                {'label': 'Average Sentiment', 'value': 'mean'},
                {'label': 'Median Sentiment', 'value': 'median'},
                {'label': 'Max Sentiment', 'value': 'max'},
                {'label': 'Min Sentiment', 'value': 'min'}
            ],
            value='mean',
            clearable=False
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Year Range:"),
        dcc.RangeSlider(
            id='year-slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=[df['Year'].min(), df['Year'].max()],
            marks= {str(year): str(year) for year in range(df['Year'].min(), df['Year'].max() + 1) if year % 5 == 0},
            step=1
        ),
    ], style={'width': '90%', 'padding': '20px'}),
    
    dcc.Graph(id='sentiment-line-graph')
])

@app.callback(
    Output('sentiment-line-graph', 'figure'),
    Input('source-type-dropdown', 'value'),
    Input('publisher-dropdown', 'value'),
    Input('emotions-dropdown', 'value'),
    Input('aggregation-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_graph(selected_source, selected_publisher, selected_emotions, aggregation_value, selected_years):
    # Debugging: Print the selected filter values
    print(f"Selected Source Type: {selected_source}")
    print(f"Selected Publisher: {selected_publisher}")
    print(f"Selected Emotions: {selected_emotions}")
    print(f"Selected Aggregation Value: {aggregation_value}")
    print(f"Selected Year Range: {selected_years}")

    filtered_df = df.copy()
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['Source Type'] == selected_source]
    if selected_publisher != 'All':
        filtered_df = filtered_df[filtered_df['Publication Title'] == selected_publisher]
    filtered_df = filtered_df[(filtered_df['Year'] >= selected_years[0]) & (filtered_df['Year'] <= selected_years[1])]
    
    # Debugging: Print the shape of the filtered DataFrame
    print(f"Filtered DataFrame shape: {filtered_df.shape}")

    # Filter to include only numeric columns for resampling
    numeric_columns = selected_emotions
    filtered_df_numeric = filtered_df[['Date_x'] + numeric_columns]

    # Debugging: Check if filtered DataFrame is empty
    if filtered_df_numeric.empty:
        print("Filtered DataFrame is empty. No data available for the selected filters.")
        return px.line(title="No data available for the selected filters.")

    # Set the index to the 'Date_x' column
    filtered_df_numeric = filtered_df_numeric.set_index('Date_x')

    # Resample by year
    if aggregation_value == 'mean':
        yearly_sentiments = filtered_df_numeric.resample('Y').mean().reset_index()
    elif aggregation_value == 'median':
        yearly_sentiments = filtered_df_numeric.resample('Y').median().reset_index()
    elif aggregation_value == 'max':
        yearly_sentiments = filtered_df_numeric.resample('Y').max().reset_index()
    elif aggregation_value == 'min':
        yearly_sentiments = filtered_df_numeric.resample('Y').min().reset_index()

    # Debugging: Print the head of the yearly sentiments DataFrame
    print(f"Yearly Sentiments DataFrame head:\n{yearly_sentiments.head()}")

    fig = px.line(yearly_sentiments, x='Date_x', y=numeric_columns,
                  labels={'Date_x': 'Year', 'value': 'Sentiment Score', 'variable': 'Sentiment'},
                  title=f'Sentiment Trends for {selected_source} by {selected_publisher} from {selected_years[0]} to {selected_years[1]}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
