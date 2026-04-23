import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import cv2
import base64

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard Interativo - Visão Computacional"),
    dcc.Slider(
        id='threshold',
        min=0,
        max=255,
        step=10,
        value=127
    ),
    html.Img(id='image-output')
]
)

def process_image(thresh):
    img = cv2.imread("imagem.jpg", 0)
    _, th = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
    _, buffer = cv2.imencode('.png', th)
    return base64.b64encode(buffer).decode()

@app.callback(
    Output('image-output', 'src'),
    Input('threshold', 'value')
)

def update_image(thresh):
    img_base64 = process_image(thresh)
    return f'data:image/png;base64,{img_base64}'

if __name__ == '__main__':
    app.run_server(debug=True)