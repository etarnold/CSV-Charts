import os
import base64
import io
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


app = Dash(__name__)

# Styling and options for html elements
layout = html.Div([
    html.Div(id='metadata-container'),
    html.Div(id='graph-container'),
    html.H4('Select a file to display its graph', style={'margin-top': '20px', 'margin-bottom': '10px'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.Button('Browse Files', style={'font-size': '17px'})
        ]),
        multiple=False
    )
])


@app.callback(Output('metadata-container', 'children'), Input('upload-data', 'contents'),
              Input('upload-data', 'filename'))
def display_metadata(uploaded_file_contents, uploaded_file_name):
    if uploaded_file_contents is None:
        return ''

    content_type, content_string = uploaded_file_contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Find the line number where the header 'Timestamp' is present
    timestamp_line = None
    for i, line in enumerate(io.StringIO(decoded.decode('utf-8'))):
        if 'Timestamp' in line:
            timestamp_line = i
            break
    
    if timestamp_line is None:
        print("Error: 'Timestamp' header not found in the uploaded file")
        return ''
    
    # Read the CSV file starting from the row containing "Timestamp"
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), skiprows=timestamp_line)
    
    # Convert all columns to appropriate data types
    for col in df.columns:
        if col != 'Timestamp':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    metadata = []
    # Add the file name in bold to the metadata
    metadata.append(html.Strong(f'{uploaded_file_name}'))
    
    # Read the CSV file line by line until "Timestamp" is encountered
    for line in io.StringIO(decoded.decode('utf-8')):
        if 'Timestamp' in line:
            break
        if ',' in line:
            key, value = map(str.strip, line.split(',', 1))
            metadata.append(f"{key}: {value}")
        else:
            metadata.append(line.strip())

    metadata_html = [html.P(meta) for meta in metadata]
    return metadata_html



@app.callback(Output('graph-container', 'children'), Input('upload-data', 'contents'),
              Input('upload-data', 'filename'))
def update_graph(uploaded_file_contents, uploaded_file_name):
    if uploaded_file_contents is None:
        return ''

    content_type, content_string = uploaded_file_contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Find the line number where the header 'Timestamp' is present
    timestamp_line = None
    for i, line in enumerate(io.StringIO(decoded.decode('utf-8'))):
        if 'Timestamp' in line:
            timestamp_line = i
            break
    
    if timestamp_line is None:
        print("Error: 'Timestamp' header not found in the uploaded file")
        return ''

    # Read the CSV file starting from the row containing "Timestamp"
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), skiprows=timestamp_line)
    
    # Convert all columns to appropriate data types
    for col in df.columns:
        if col != 'Timestamp':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    y = df.columns[1:].tolist()

    fig = px.line(df, x='Timestamp', y=y)
    graph = dcc.Graph(id='graph', figure=fig)

    return graph


if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
