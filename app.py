# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# from cgitb import enable
# from faulthandler import disable
import geopandas as gpd
import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import vaex

df_iptu_distritos = vaex.open('data/IPTU-Distritos1995-2022-agrupados-por-distrito.hdf5')
gdf_distritos = gpd.read_file('data/SIRGAS_GPKG_distrito.gpkg')
gdf_distritos['area'] = gdf_distritos.area
gdf_distritos.to_crs(epsg=4674, inplace=True)
# df_iptu_distritos = df_iptu_distritos.merge(gdf_distritos.loc[:, ['ds_codigo', 'ds_nome']].astype({'ds_codigo': 'int'}), left_on='distrito', right_on='ds_codigo')

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

server = app.server

my_output = html.Div()

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
                {"label": "TO médio", "value": "TO médio"},
                {"label": "CA médio em lotes condominiais", "value": "CA médio em lotes condominiais"},
                {"label": "TO médio em lotes condominiais", "value": "TO médio em lotes condominiais"},
                {"label": "CA médio em lotes não condominiais", "value": "CA médio em lotes não condominiais"},
                {"label": "TO médio em lotes não condominiais", "value": "TO médio em lotes não condominiais"},
                {"label": "Comprimento Médio da Testada", "value": "Comprimento Médio da Testada"},
                {"label": "Número médio de Pavimentos", "value": "Número médio de Pavimentos"},
                {"label": "Fator de obsolecência médio", "value": "Fator de obsolecência médio"}
            ],
            value='Área Total Construída',
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
                        # value=[2022,2022],
                        value=[2022],
                        marks={1995: '1995',2000: '2000', 2005: '2005', 2010: '2010', 2015: '2015', 2020: '2020'},
                        pushable=False),
    ],
    className="ano-exercicio",
)

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [html.H1("CEM - Centro de Estudo das Metrópoles"),
                html.H2("Dash IPTU de São Paulo (1995-2022) - V.0.0.1"),
                dcc.Markdown('''
                Prova de conceito em fase de pré-testes para validação do uso da série histórica dos dados de IPTU de São Paulo, com mais de 83 milhões de registros, com objetivo de visualização e exportação de dados agregados espacialmente para disseminação de seu uso para diversas disciplinas e finalidades.

                Código disponível em [https://github.com/cem-usp/dash-iptu] comentários, sugestões, inconsistências reportar preferencialmente por `issue` no GitHub ou por email para [feromes@usp.br](mailto:feromes@usp.br)
                '''),
                dbc.Form([range_slider])]
            )
        ),
        dbc.Row([
            dbc.Col(
                [dbc.Form([radioitems]),
                dbc.Form([checklist]),
                html.Br()]
            ),
            dbc.Col(
                dcc.Graph(id="graph"), width=8
            )]
        ),
        dbc.Row(
            dbc.Col(
                [html.H2('Download da série histórica para ...', id="table-title"),
                dash_table.DataTable(
                    id='table',
                    export_format="csv"
                )]
            )
        )
    ])

# @app.callback(
#     Output("my-output", "children"),
#     Input("checklist-input", "value")
# )
# def update(input_value):
#     return input_value


@app.callback(
    Output("graph", "figure"), 
    Input("checklist-input", "value"),
    Input("range-slider", "value"))
def update_map(atributo, ano):
    gdf_distritos_counted = gdf_distritos.astype({'ds_codigo': 'int'}).merge(df_iptu_distritos[df_iptu_distritos.ano == ano].to_pandas_df(), left_on='ds_codigo', right_on='distrito')
    fig = px.choropleth(gdf_distritos_counted,
                    geojson=gdf_distritos_counted.geometry,
                    projection="transverse mercator",
                    color=atributo,
                    locations=gdf_distritos_counted.index.to_list(),
                    hover_data=["ds_nome"],
                    custom_data=["ds_codigo"],
                    fitbounds='geojson',
                    title=f'{atributo} para o ano de {ano[-1]}')
                    #  color="ds_codigo")
                    #    projection="mercator")
    fig.update_geos(fitbounds="locations", visible=False)
    return fig

@app.callback(
    Output("table", "columns"),
    Output("table", "data"), 
    Input("checklist-input", "value"))
def gen_table(atributo):
    df = df_iptu_distritos.to_pandas_df().merge(gdf_distritos.loc[:, ['ds_codigo', 'ds_nome']].astype({'ds_codigo': 'int'}), left_on='distrito', right_on='ds_codigo')
    df_pivot = df.pivot(index=['distrito', 'ds_nome'], values=atributo, columns='ano')
    columns=[{"name": str(i), "id": str(i)} for i in df_pivot.reset_index().columns]
    data=df_pivot.reset_index().to_dict("records")
    return columns, data

@app.callback(
    Output("table-title", "children"),
    Input("checklist-input", "value"))
def change_title(atributo):
    return f'Download da série histórica para {atributo}'

if __name__ == '__main__':
    app.run_server(debug=True)
    
