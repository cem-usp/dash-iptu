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
                {"label": "Subprefeituras", "value": 2, "disabled": True},
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
        dbc.RadioItems(
            options=[
                {"label": "Quantidade de Unidades", "value": "Quantidade de Unidades", "disabled": False},
                {"label": "Quantidade de Unidades Condominiais", "value": "Quantidade de Unidades Condominiais"},
                {"label": "Tamanho Médio da Unidade Condominial", "value": "Tamanho Médio da Unidade Condominial"},
                {"label": "Tamanho médio dos Terrenos", "value": "Tamanho médio dos Terrenos"},
                {"label": "Área Total dos terrenos/lotes", "value": "Área Total dos terrenos/lotes", "disabled": True},
                {"label": "Área Total Ocupada", "value": "Área Total Ocupada", "disabled": True},
                {"label": "Área Total Construída", "value": "Área Total Construída"},
                {"label": "Valor Total dos Terrenos", "value": "Valor Total dos Terrenos", "disabled": True},
                {"label": "Valor Total das Construções", "value": "Valor Total das Construções", "disabled": True},
                {"label": "CA médio", "value": "CA médio"},
                {"label": "TO médio", "value": "TO (Taxa de Ocupação)"},
                {"label": "CA médio em lotes condominiais", "value": "CA médio em lotes condominiais"},
                {"label": "TO médio em lotes condominiais", "value": "TO médio em lotes condominiais"},
                {"label": "CA médio em lotes não condominiais", "value": "CA médio em lotes não condominiais"},
                {"label": "TO médio em lotes não condominiais", "value": "TO médio em lotes não condominiais"},
                {"label": "Comprimento Médio da Testada", "value": "Comprimento Médio da Testada"},
                {"label": "Número médio de Pavimentos", "value": "Número médio de Pavimentos"},
                {"label": "Fator de obsolecência médio", "value": "Fator de obsolecência médio"}
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
        dbc.Form([range_slider]),
        dbc.Form([radioitems]),
        dbc.Form([checklist]),
        html.Br(),
        html.Div(id='my-output')
    ])

@app.callback(
    Output("my-output", "children"),
    Input("checklist-input", "value")
)
def update(input_value):
    return input_value

if __name__ == '__main__':
    app.run_server(debug=True)
    
