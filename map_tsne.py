import io
import base64
import os
import re

from dash import Dash, dcc, html, Input, Output, no_update
from PIL import Image
import numpy as np
import plotly.graph_objs as go

# Define the directory path
directory = os.path.join(os.getcwd())

# Load data from each class into numpy arrays
class_0_data = np.loadtxt("tsne_class_0_data.txt")
class_1_data = np.loadtxt("tsne_class_1_data.txt")
class_2_data = np.loadtxt("tsne_class_2_data.txt")
class_3_data = np.loadtxt("tsne_class_3_data.txt")

# Combine data from all classes
X = np.concatenate((class_0_data, class_1_data, class_2_data, class_3_data))

# Define the labels for each class
class_0_labels = np.zeros(len(class_0_data))
class_1_labels = np.ones(len(class_1_data))
class_2_labels = np.full(len(class_2_data), 2)
class_3_labels = np.full(len(class_3_data), 3)

# Combine labels for all classes
y = np.concatenate((class_0_labels, class_1_labels, class_2_labels, class_3_labels))
# y = np.load('predictions.npy')

# Create a dictionary to map class labels to colors
color_dict = {
    0: 'rgb(4,110,152)',   # CNV     - BLUE
    1: 'rgb(187,208,50)',  # DME     - LIGHT GREEN
    2: 'rgb(231,55,41)',   # DRUSEN  - RED
    3: 'rgb(251,186,0)',   # NORMAL  - YELLOW
}

# Create a scatter plot with a different color for each class
fig = go.Figure(
    go.Scatter(
        x=X[:, 0],
        y=X[:, 1],
        mode='markers',
        marker=dict(
            color=[color_dict[label] for label in y],
            size=10,
            opacity=0.8
        )
    )
)



fig.update_traces(
    hoverinfo="none",
    hovertemplate=None,
    marker=dict(size=10)
)
fig.update_layout(
    xaxis=dict(range=[min(X[:, 0]) - 5, max(X[:, 0]) + 5]),
    yaxis=dict(range=[min(X[:, 1]) - 5, max(X[:, 1]) + 5]),
    height=1200,
    width=1200,
)


fig.write_html("image_map.html")

########################################################################################################################
# specify the directory where the PNG images are located
dir_path = os.path.join(os.getcwd())

# use glob to find all PNG files in the directory
files_0 = [os.path.join(directory, '0', f) for f in os.listdir(os.path.join(directory, '0')) if f.endswith('.png')]
files_1 = [os.path.join(directory, '1', f) for f in os.listdir(os.path.join(directory, '1')) if f.endswith('.png')]
files_2 = [os.path.join(directory, '2', f) for f in os.listdir(os.path.join(directory, '2')) if f.endswith('.png')]
files_3 = [os.path.join(directory, '3', f) for f in os.listdir(os.path.join(directory, '3')) if f.endswith('.png')]
files = np.concatenate((files_0, files_1, files_2, files_3))
########################################################################################################################
def extract_number_from_image_path(image_path):
    pattern = r'\b(\d)\b'
    match = re.search(pattern, image_path)
    if match:
        return match.group(1)
    else:
        return None

image_dict = {}
for i in range(1000):
    image_path = files[i]
    c = int(extract_number_from_image_path(image_path))
    im = Image.open(image_path)
    buffer = io.BytesIO()
    im.save(buffer, format="jpeg")
    encoded_image = base64.b64encode(buffer.getvalue()).decode()
    im_url = "data:image/jpeg;base64, " + encoded_image
    image_dict[i] = im_url

app = Dash(__name__)

app.layout = html.Div(
    className="container",
    children=[
        dcc.Graph(id="graph-2-dcc", figure=fig, clear_on_unhover=True),
        dcc.Tooltip(id="graph-tooltip-2", direction='bottom'),
    ],
)

@app.callback(
    Output("graph-tooltip-2", "show"),
    Output("graph-tooltip-2", "bbox"),
    Output("graph-tooltip-2", "children"),
    Output("graph-tooltip-2", "direction"),

    Input("graph-2-dcc", "hoverData"),
)

def display_hover(hoverData):
    if hoverData is None:
        return False, no_update, no_update, no_update

    hover_point = hoverData["points"][0]
    index = hover_point["pointIndex"]
    bbox = hover_point["bbox"]
    y = hover_point["y"]
    direction = "bottom" if y > 50 else "top"

    children = [
        html.Img(
            src=image_dict[index],
            style={"width": "150px"},
        ),
        html.P(f"Image {index} from base64 string"),
    ]

    return True, bbox, children, direction

if __name__ == "__main__":
    app.run_server(debug=True)
