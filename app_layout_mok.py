# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

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
            id="radioitems-input",
        ),
    ]
)

checklist = html.Div(
    [
        dbc.Label("Selecione as totalizações, índices ou Quantitativos"),
        dbc.Checklist(
            options=[
                {"label": "Quantidade de Unidades", "value": 1},
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
            value=[1],
            id="checklist-input",
        ),
    ]
)

app.layout = dbc.Container(
    [
        html.H1("Dash IPTU de São Paulo"),
        dbc.Form([radioitems]),
        dbc.Form([checklist]),
    ])



if __name__ == '__main__':
    app.run_server(debug=True)
    
