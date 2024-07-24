import dash
from dash import dcc, html, Input, Output, State
import dash_uploader as du
import requests
print(__name__)
# Initialize Dash app
app = dash.Dash(__name__)
du.configure_upload(app, r"uploads")

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Chat with Your Documents"),
    du.Upload(id='upload-file', text='Upload Document', max_files=1),
    html.Div(id='file-upload-output'),
    dcc.Input(id='user-input', type='text', placeholder='Ask a question...', style={'width': '80%'}),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='response-output'),
])

# Callback to handle file upload
@app.callback(
    Output('file-upload-output', 'children'),
    Input('upload-file', 'isCompleted'),
    State('upload-file', 'fileNames')
)
def update_output(isCompleted, fileNames):
    if isCompleted and fileNames:
        file_path = f"uploads/{fileNames[0]}"
        response = requests.post("http://localhost:8000/upload", files={'file': open(file_path, 'rb')})
        text = response.json().get('text', '')
        return html.Div([
            html.H3("Extracted Text:"),
            html.P(text)
        ])
    return html.Div()

# Callback to handle user input and generate response
@app.callback(
    Output('response-output', 'children'),
    Input('submit-button', 'n_clicks'),
    State('user-input', 'value')
)
def update_response(n_clicks, value):
    if n_clicks > 0 and value:
        response = requests.post("http://localhost:8000/generate", json={'prompt': value})
        generated_text = response.json().get('generated_text', '')
        return html.Div([
            html.H3("Response:"),
            html.P(generated_text)
        ])
    return html.Div()
print('Function defs completed')
if __name__ == '__main__':
    app.run_server(debug=True)
