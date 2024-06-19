import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import openai
import json
import requests

# Data
file_path = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Data\\final_merged_output.xlsx'
df = pd.read_excel(file_path)

# Convert the 'Date_x' column to datetime format and rename it to 'Date'
df['Date'] = pd.to_datetime(df['Date_x'])
df['Year'] = df['Date'].dt.year

# Define positive and negative sentiments
positive_sentiments = ['Happiness', 'Love', 'Surprise']
negative_sentiments = ['Anger', 'Disgust', 'Fear', 'Sadness']

# Positive/Negative scores 
df['Positive'] = df[positive_sentiments].mean(axis=1)
df['Negative'] = df[negative_sentiments].mean(axis=1)

# Initialize the Dash app
app = Dash(__name__)

# Set your OpenAI API key
openai.api_key = 'key-tbd'

# Include 'All' option in dropdown options
source_type_options = [{'label': 'All', 'value': 'All'}] + [{'label': st, 'value': st} for st in df['Source Type'].unique()]
publisher_options = [{'label': 'All', 'value': 'All'}] + [{'label': publisher, 'value': publisher} for publisher in df['Publication Title'].unique()]

app.layout = html.Div([
    html.H1("Interactive Sentiment Analysis Visualization"),
    
    html.Div([
        html.Label("Source Type:"),
        dcc.Dropdown(
            id='source-type-dropdown',
            options=source_type_options,
            value='All',
            clearable=False
        ),
    ], style={'width': '22%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Publisher:"),
        dcc.Dropdown(
            id='publisher-dropdown',
            options=publisher_options,
            value='All',
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
    
    dcc.Graph(id='sentiment-line-graph'),

    html.Div([
        html.Label("Chat with the Dashboard:"),
        dcc.Input(id='chat-input', type='text', value='', placeholder='Type your message here...'),
        html.Button('Send', id='chat-submit-button', n_clicks=0, className='btn btn-primary'),
        html.Div(id='chat-output')
    ], style={'padding': '20px'})
], className='container')

@app.callback(
    Output('sentiment-line-graph', 'figure'),
    Input('source-type-dropdown', 'value'),
    Input('publisher-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_graph(selected_source, selected_publisher, selected_years):
    filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]
    
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['Source Type'] == selected_source]
    if selected_publisher != 'All':
        filtered_df = filtered_df[filtered_df['Publication Title'] == selected_publisher]

    numeric_columns = ['Positive', 'Negative']
    filtered_df_numeric = filtered_df[['Date'] + numeric_columns]

    if filtered_df_numeric.empty:
        return px.line(title="No data available for the selected filters.")

    filtered_df_numeric = filtered_df_numeric.set_index('Date')
    yearly_sentiments = filtered_df_numeric.resample('YE').mean().reset_index()

    fig = px.line(yearly_sentiments, x='Date', y=numeric_columns,
                  labels={'Date': 'Year', 'value': 'Sentiment Score', 'variable': 'Sentiment'},
                  title=f'Sentiment Trends for {selected_source} by {selected_publisher} from {selected_years[0]} to {selected_years[1]}')
    return fig

@app.callback(
    Output('source-type-dropdown', 'value'),
    Output('publisher-dropdown', 'value'),
    Output('year-slider', 'value'),
    Output('chat-output', 'children'),
    Input('chat-submit-button', 'n_clicks'),
    State('chat-input', 'value'),
    State('source-type-dropdown', 'value'),
    State('publisher-dropdown', 'value'),
    State('year-slider', 'value')
)
def update_filters(n_clicks, user_message, current_source, current_publisher, current_years):
    if n_clicks == 0:
        return current_source, current_publisher, current_years, ""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    
    chat_response = response.choices[0].message['content'].strip()

    # Here, you can parse `chat_response` to extract relevant filter values.
    # For simplicity, let's assume the response is a JSON with keys matching the filter ids.
    try:
        parsed_response = json.loads(chat_response)
        new_source = parsed_response.get('source_type', current_source)
        new_publisher = parsed_response.get('publisher', current_publisher)
        new_years = parsed_response.get('year_range', current_years)
    except json.JSONDecodeError:
        return current_source, current_publisher, current_years, "Error: Unable to interpret the response."

    return new_source, new_publisher, new_years, chat_response

if __name__ == '__main__':
    app.run_server(debug=True)