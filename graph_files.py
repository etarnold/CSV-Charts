import os
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

dir_path = './assets/' # path of csv files

# Lists files in dir_path
files = os.listdir(dir_path)
file_index = 1
file_paths = []
for file in files:
    file_path = os.path.join(dir_path, file)
    file_paths.append(file_path)
    file_index += 1

# Styling and options for html elements
layout = html.Div([
    html.H4('Select a file to display its graph'),
    html.Div(id='graph-container'),
    dcc.Dropdown(
        id='file-dropdown',
        style={'width': '500px'},
        options=[{'label': f'{i+1}: {files[i]}', 'value': i} for i in range(len(files))],
        value=None
    )
])

@app.callback(Output('graph-container', 'children'), Input('file-dropdown', 'value'))
def update_graph(selected_file_index):
    if selected_file_index is None:
        return ''
    
    # Create Panda DataFrame for building graph
    file_path = file_paths[selected_file_index]
    df = pd.read_csv(file_path)
    time_col_index = df.columns.str.lower().get_loc('time')
    y = df.columns[time_col_index+1:].tolist()
    
    # Draws lines for Dash graph
    fig = px.line(df, x=df.columns[time_col_index], y=y)
    graph = dcc.Graph(id='graph', figure=fig)
    
    return graph


if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
