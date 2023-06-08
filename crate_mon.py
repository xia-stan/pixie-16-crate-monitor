import time

import plotly
import requests
from bs4 import BeautifulSoup
from dash import Dash, html, dcc, Output, Input

DATA = {"time": [], "values": {}}

# URL = "http://192.168.121.179/"
URL = "http://192.168.121.181/"
user = "private"
pwd = "private"

app = Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='graph0'),
    dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0)
])


@app.callback(Output('graph0', 'figure'),
              Input('interval', 'n_intervals'))
def update_graph(n):
    global DATA

    fig = plotly.tools.make_subplots(rows=1, cols=1)
    # fig['layout']['margin'] = {
    #     'l': 30, 'r': 10, 'b': 30, 't': 10
    # }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    soup = BeautifulSoup(requests.get(URL, auth=(user, pwd)).content, 'html.parser')
    DATA['time'].append(time.time())
    for tab in soup.findAll(id='tab'):
        section = tab.find('caption').text
        if section == "Output Voltages":
            headers = [header.text.lower() for header in tab.find_all('th')]
            results = [{headers[i]: cell.text for i, cell in enumerate(row.find_all('td'))}
                       for row in tab.find_all('tr')]
            for item in results:
                item['voltage'] = float(item['voltage'][:-1])
                item['current'] = float(item['current'][:-1])

                data = DATA['values'].get(item['channel'], None)
                if data is None:
                    DATA['values'][item['channel']] = [item['current']]
                else:
                    DATA['values'][item['channel']].append(item['current'])
    for k, v in DATA['values'].items():
        fig.append_trace({
            'x': DATA['time'],
            'y': v,
            'name': k,
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 1, 1)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
