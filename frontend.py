import dash
from dash import dcc, html, Input, Output, State, callback
import requests
import os
import base64

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Chat with Your Documents"),
    
    dcc.Upload(
        id='upload-file',
        children=html.Button('Upload Document'),
        multiple=False
    ),
    
    html.Div(id='file-upload-output'),
    
    dcc.Input(id='user-input', type='text', placeholder='Ask a question...', style={'width': '80%'}),
    html.Button('Submit', id='submit-button', n_clicks=0),
    
    html.Div(id='response-output'),
])

# Directory where files are saved
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Callback to handle file upload
@app.callback(
    Output('file-upload-output', 'children'),
    Input('upload-file', 'contents'),
    State('upload-file', 'filename')
)
def update_output(contents, filename):
    if contents:
        # Save the file to the 'uploads' directory
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as f:
            f.write(decoded)
        
        # Send only the filename to the backend
        response = requests.post("http://0.0.0.0:8000/upload", json={'filename': filename})
        
        # Extract text from the response
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
        response = requests.post("http://0.0.0.0:8000/generate", json={'prompt': value})
        generated_text = response.json().get('generated_text', '')
        return html.Div([
            html.H3("Response:"),
            html.P(generated_text)
        ])
    return html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)
