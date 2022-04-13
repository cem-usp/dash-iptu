# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from cgitb import enable
from faulthandler import disable
from dash import Dash, html, dcc, Input, Output, dash_table
import dash
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(
    external_stylesheets=[dbc.themes.DARKLY]
)

radioitems = html.Div(
    [
        dbc.Label("Selecione a agregação espacial"),
        dbc.RadioItems(
            options=[
                {"label": "Distritos", "value": 1},
                {"label": "Subprefeituras", "value": 2},
                {"label": "Zonas OD", "value": 3, "disabled": True},
                {"label": "CODLOGs", "value": 4, "disabled": True},
            ],
            value=1,
            id="radioitems-input"
        ),
    ]
)

checklist = html.Div(
    [
        dbc.Label("Selecione as totalizações, índices ou Quantitativos"),
        dbc.Checklist(
            options=[
                {"label": "Quantidade de Unidades", "value": 1, "disabled": True},
                {"label": "Quantidade de Unidades Condominiais", "value": 2},
                {"label": "Tamanho Médio da Unidade Condominial"},
                {"label": "Total de área dos terrenos/lotes", "value": 3, "disabled": False},
                {"label": "Total de Área Ocupada"},
                {"label": "Total de Área Construída"},
                {"label": "Valor Total dos Terrenos"},
                {"label": "Valor Total das Construções"},
                {"label": "CA (Coeficiente de Aproveitamento"},
                {"label": "TO (Taxa de Ocupação)"},
                {"label": "Tamanho Médio da Testada"},
                {"label": "Número médio de Pavimentos"},
                {"label": "Fator de obsolecência médio"}
            ],
            value=[1, 2],
            id="checklist-input"
        ),
    ]
)

range_slider = html.Div(
    [
        dbc.Label("Exercício", html_for="range-slider"),
        dcc.RangeSlider(id="range-slider", 
                        min=1995, 
                        max=2022, 
                        step=1, 
                        value=[1995,2022],
                        marks={1995: '1995',2000: '2000', 2005: '2005', 2010: '2010', 2015: '2015', 2020: '2020'},
                        pushable=False),
    ],
    className="mb-3",
)

app.layout = dbc.Container(
    [
        html.H1("Dash IPTU de São Paulo"),
        dbc.Form([radioitems]),
        dbc.Form([checklist]),
        dbc.Form([range_slider]),
        html.Br(),
        html.Div(id='my-output')
    ])

@app.callback(
    Output("my-output", "children"),
    Input("range-slider", "value")
)
def update(input_value):
    return input_value

if __name__ == '__main__':
    app.run_server(debug=True)
    
