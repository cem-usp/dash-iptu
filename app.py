# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# from cgitb import enable
# from faulthandler import disable
from certifi import contents
import geopandas as gpd
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import vaex
import os

df_iptu_distrito = vaex.open('data/IPTU-1995-2022-agrupados-por-distrito.hdf5')
df_iptu_subprefeitura = vaex.open('data/IPTU-1995-2022-agrupados-por-subprefeitura.hdf5')
df_iptu_od = vaex.open('data/IPTU-1995-2022-agrupados-por-od.hdf5')
df_iptu_sq = vaex.open('data/IPTU-1995-2022-agrupados-por-sq.hdf5')

gdf_distritos = gpd.read_file('data/SIRGAS_GPKG_distrito.gpkg')
gdf_distritos['area'] = gdf_distritos.area
gdf_distritos.geometry = gdf_distritos.simplify(tolerance=100)
gdf_distritos.to_crs(epsg=4674, inplace=True)

gdf_od = gpd.read_file('zip://data/SIRGAS_SHP_origemdestino_2017.zip!SIRGAS_SHP_origemdestino_2017', crs='EPSG:31983')
gdf_od = gdf_od[gdf_od.od_municip == '36']
gdf_od.set_crs(epsg=31983, inplace=True)
gdf_od['area'] = gdf_od.area
gdf_od.geometry = gdf_od.simplify(tolerance=10)
gdf_od.to_crs(epsg=4674, inplace=True)

gdf_subprefeitura = gpd.read_file('zip://data/SIRGAS_GPKG_subprefeitura.zip!SIRGAS_GPKG_subprefeitura.gpkg')
gdf_subprefeitura['area'] = gdf_subprefeitura.area
gdf_subprefeitura.geometry = gdf_subprefeitura.simplify(tolerance=100)
gdf_subprefeitura.to_crs(epsg=4674, inplace=True)

# gdf_quadras = gpd.read_file('data/quadras.gpkg')
# gdf_quadras.to_crs(epsg=4674, inplace=True)

routes_pathname_prefix='/dash-iptu/'

# if 'DASH_ENV' in os.environ: 
#     if os.environ['DASH_ENV'] == 'production':
#         routes_pathname_prefix='/'

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    # as the proxy server will remove the prefix
    ## TODO IF PRODUCTION
    # routes_pathname_prefix='/',
    routes_pathname_prefix=routes_pathname_prefix,

    # the front-end will prefix this string to the requests
    # that are made to the proxy server
    requests_pathname_prefix='/dash-iptu/'
)

server = app.server

my_output = html.Div()

radioitems = html.Div(
    [
        dbc.Label("Selecione a agregação espacial"),
        dbc.RadioItems(
            options=[
                # {"label": "Subprefeituras", "value": 2, "disabled": False},
                # {"label": "Distritos", "value": 1},
                # {"label": "Zonas OD", "value": 3, "disabled": False},
                # {"label": "Macroáreas PDE", "value": 4, "disabled": True},
                # {"label": "Quadras", "value": 5, "disabled": True},
                {"label": "Subprefeituras", "value": 'subprefeituras', "disabled": False},
                {"label": "Distritos", "value": 'distritos'},
                {"label": "Zonas OD", "value": 'zonas-od', "disabled": False},
                {"label": "Macroáreas PDE", "value": 'macro-areas', "disabled": True},
                {"label": "Quadras", "value": 'quadras', "disabled": True},
                
            ],
            value='distritos',
            id="radioitems-input"
        ),
    ]
)

checklist = html.Div(
    [
        dbc.Label("Selecione as totalizações, índices ou Quantitativos"),
        dbc.RadioItems(
            options=[
                # {"label": "Quantidade de Unidades", "value": "Quantidade de Unidades", "disabled": False},
                {"label": "Quantidade de Unidades Condominiais", "value": "Quantidade de Unidades Condominiais"},
                {"label": "Tamanho Médio da Unidade Condominial", "value": "Tamanho Médio da Unidade Condominial"},
                {"label": "Tamanho médio dos Terrenos", "value": "Tamanho médio dos Terrenos"},
                {"label": "Área Total dos terrenos-lotes", "value": "Área Total dos terrenos-lotes", "disabled": False},
                {"label": "Área Total Ocupada", "value": "Área Total Ocupada", "disabled": False},
                {"label": "Área Total Construída", "value": "Área Total Construída"},
                {"label": "Valor Total dos Terrenos", "value": "Valor Total dos Terrenos", "disabled": False},
                {"label": "Valor Total das Construções", "value": "Valor Total das Construções", "disabled": False},
                {"label": "CA médio", "value": "CA médio"},
                {"label": "TO médio", "value": "TO médio"},
                {"label": "CA médio em lotes condominiais", "value": "CA médio em lotes condominiais"},
                {"label": "TO médio em lotes condominiais", "value": "TO médio em lotes condominiais"},
                {"label": "CA médio em lotes não condominiais", "value": "CA médio em lotes não condominiais"},
                {"label": "TO médio em lotes não condominiais", "value": "TO médio em lotes não condominiais"},
                {"label": "Comprimento Médio da Testada", "value": "Comprimento Médio da Testada"},
                {"label": "Número médio de Pavimentos", "value": "Número médio de Pavimentos"},
                {"label": "Fator de obsolecência médio", "value": "Fator de obsolecência médio"},
                {"label": "Percentual de Uso Residencial", "value": "Percentual de Uso Residencial"},
                {"label": "Percentual de Uso Comercial", "value": "Percentual de Uso Comercial"},
                {"label": "Percentual de Uso Serviços", "value": "Percentual de Uso Serviços"},
                {"label": "Percentual de Uso Industrial", "value": "Percentual de Uso Industrial"},
                {"label": "Percentual de Uso Outros", "value": "Percentual de Uso Outros"},
            ],
            value='Área Total Construída',
            id="checklist-input"
        ),
    ]
)

range_slider = html.Div(
    [
        dbc.Label("82.322.059 registros calculados", id="registros-calculados"),
        dcc.RangeSlider(id="range-slider", 
                        min=1995, 
                        max=2022, 
                        step=1, 
                        updatemode='drag',
                        # value=[2022,2022],
                        value=[1995,2022],
                        marks={1995: '1995',2000: '2000', 2005: '2005', 2010: '2010', 2015: '2015', 2020: '2020'},
                        pushable=True),
    ],
    className="ano-exercicio",
)

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [html.H1("CEM - Centro de Estudo das Metrópoles"),
                html.H2("Dash IPTU de São Paulo (1995-2022) - V.0.0.3"),
                dcc.Markdown('''
                Prova de conceito em fase de pré-testes para validação do uso da série histórica dos dados de IPTU de São Paulo, com mais de 83 milhões de registros, com objetivo de visualização e exportação de dados agregados espacialmente para disseminação de seu uso para diversas disciplinas e finalidades.

                Código disponível em [https://github.com/cem-usp/dash-iptu] comentários, sugestões, inconsistências reportar preferencialmente por `issue` no GitHub ou por email para [feromes@usp.br](mailto:feromes@usp.br)
                '''),
                dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
                    dcc.Tab(label='Área Total Construída em 2022', value='tab-1', id='tab-1'),
                    dcc.Tab(label='Variação de 1995 à 2022', value='tab-2', id='tab-2'),
                    dcc.Tab(label='Descrição do cálculo/processamento para Área Total Construída', value='tab-3', id='tab-3'),
                ]),
                dcc.Loading(
                    id='loading-map',
                    type='default',
                    # fullscreen=True,
                    children=html.Div(id='loading-output')
                ),
                dbc.Form([range_slider])
          ]
            )
        ),
        dbc.Row([
            dbc.Col(
                [dbc.Form([radioitems]),
                dbc.Form([checklist]),
                html.Br()]
            ),
            dbc.Col(
                [dcc.Graph(id="graph"),
                dbc.Button('Download', id='download-button', n_clicks=0),
                dcc.Download(id="download-gpkg")], width=8
            )]
        ),
        # dbc.Row(
        #     dbc.Col(
        #         [html.H2('Download da série histórica para ...', id="table-title"),
        #         dash_table.DataTable(
        #             id='table',
        #             export_format="csv"
        #         )]
        #     )
        # )
    ])

# @app.callback(
#     Output("my-output", "children"),
#     Input("checklist-input", "value")
# )
# def update(input_value):
#     return input_value


@app.callback(
    Output("graph", "figure"), 
    Output("loading-map", "children"),
    Output("registros-calculados", 'children'),
    Output("tab-1", "label"),
    Output("tab-2", "label"),
    Output("tab-3", "label"),
    Input("checklist-input", "value"),
    Input("range-slider", "value"),
    Input("radioitems-input", "value"),
    State('graph', 'figure'))
def update_map(atributo, ano, agregacao, mapa_atual):

    if mapa_atual:
        zoom = mapa_atual['layout']['mapbox']['zoom']
        center = mapa_atual['layout']['mapbox']['center']
    else:
        zoom, center = 9, {'lat':-23.62095411, 'lon':-46.61666592}

    # if agregacao == 1:
    #     gdf_agregacao = gdf_distritos.astype({'ds_codigo': 'int'}).merge(df_iptu_distrito[df_iptu_distrito.ano == ano].to_pandas_df(), left_on='ds_codigo', right_on='distrito')
    #     hover_data = ["ds_nome"]
    #     custom_data=["ds_codigo"]

    # if agregacao == 2:
    #     gdf_agregacao = gdf_subprefeitura.astype({'sp_codigo': 'int'}).merge(df_iptu_subprefeitura[df_iptu_subprefeitura.ano == ano].to_pandas_df(), left_on='sp_codigo', right_on='subprefeitura')
    #     hover_data = ["sp_nome"]
    #     custom_data=["sp_codigo"]

    # if agregacao == 3:
    #     gdf_agregacao = gdf_od.astype({'od_id': 'int'}).merge(df_iptu_od[df_iptu_od.ano == ano].to_pandas_df(), left_on='od_id', right_on='od')        
    #     hover_data = ["od_nome"]
    #     custom_data=["od_id"]

    gdf_agregacao, hover_data, custom_data, min_max = sel_agregacao(agregacao, ano[-1], atributo)

    fig = px.choropleth_mapbox(gdf_agregacao,
                    geojson=gdf_agregacao.geometry,
                    zoom=zoom,
                    center=center,
                    animation_frame='ano',
                    #  projection="transverse mercator",
                    color=atributo,
                    range_color=min_max,
                    locations=gdf_agregacao.index.to_list(),
                    mapbox_style="white-bg",
                    hover_data=hover_data,
                    custom_data=custom_data,
                    height=600,
                    width=800)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                    title={'text': 'Seila'})

    loading = None

    registros = f"{format(gdf_agregacao['Quantidade de Unidades'].sum(), ',d').replace(',', '.')} registros calculados"
    tab1 = f"{atributo} em {ano[-1]}"
    tab2 = f"Variação em {atributo} de {ano[0]} à {ano[-1]}"
    tab3 = f"Descrição do cálculo/processamento para {atributo}"

    return fig, loading, registros, tab1, tab2, tab3 

# @app.callback(
#     Output("table", "columns"),
#     Output("table", "data"), 
#     Input("checklist-input", "value"))
# def gen_table(atributo):
#     df = df_iptu_distrito.to_pandas_df().merge(gdf_distritos.loc[:, ['ds_codigo', 'ds_nome']].astype({'ds_codigo': 'int'}), left_on='distrito', right_on='ds_codigo')
#     df_pivot = df.pivot(index=['distrito', 'ds_nome'], values=atributo, columns='ano')
#     columns=[{"name": str(i), "id": str(i)} for i in df_pivot.reset_index().columns]
#     data=df_pivot.reset_index().to_dict("records")
#     return columns, data

# @app.callback(
#     Output("table-title", "children"),
#     Input("checklist-input", "value"))
# def change_title(atributo):
#     return f'Download da série histórica para {atributo} por Distrito'

def sel_agregacao(agregacao, ano, atributo):

    if agregacao == 'distritos':
        gdf_agregacao = gdf_distritos.astype({'ds_codigo': 'int'}).merge(df_iptu_distrito[df_iptu_distrito.ano == ano].to_pandas_df(), left_on='ds_codigo', right_on='distrito')[["ds_codigo", "ds_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        hover_data = ["ds_nome"]
        custom_data=["ds_codigo"]
        min_max = [df_iptu_distrito[atributo].min().item(), df_iptu_distrito[atributo].max().item()]

    if agregacao == 'subprefeituras':
        gdf_agregacao = gdf_subprefeitura.astype({'sp_codigo': 'int'}).merge(df_iptu_subprefeitura[df_iptu_subprefeitura.ano == ano].to_pandas_df(), left_on='sp_codigo', right_on='subprefeitura')[["sp_codigo", "sp_nome", atributo, 'geometry', 'ano',  'Quantidade de Unidades']]
        hover_data = ["sp_nome"]
        custom_data=["sp_codigo"]
        min_max = [df_iptu_subprefeitura[atributo].min().item(), df_iptu_subprefeitura[atributo].max().item()]

    if agregacao == 'zonas-od':
        gdf_agregacao = gdf_od.astype({'od_id': 'int'}).merge(df_iptu_od[df_iptu_od.ano == ano].to_pandas_df(), left_on='od_id', right_on='od')[["od_id", "od_nome", atributo, 'geometry', 'ano',  'Quantidade de Unidades']]        
        hover_data = ["od_nome"]
        custom_data=["od_id"]
        min_max = [df_iptu_od[atributo].min().item(), df_iptu_od[atributo].max().item()]


    # if agregacao == 'quadras':
    #     gdf_agregacao = gdf_quadras.merge(df_iptu_sq[df_iptu_sq.ano == ano].to_pandas_df(), left_on='sq', right_on='sq')        
    #     hover_data = ["sq"]
    #     custom_data=["sq"]
    #     min_max = [df_iptu_sq[atributo].min().item(), df_iptu_sq[atributo].max().item()]

    return gdf_agregacao, hover_data, custom_data, min_max

@app.callback(
    Output("download-gpkg", "data"),
    Input("download-button", "n_clicks"),
    State("checklist-input", "value"),
    State("range-slider", "value"),
    State("radioitems-input", "value"),
    prevent_initial_call=True,
)
def func(n_clicks, atributo, ano, agregacao):
    # return dict(content="Hello world!", filename="hello.txt")
    return dict(content=sel_agregacao(agregacao, ano[-1], atributo)[0].to_json(), 
                filename=f"IPTU-SP-{atributo.replace(' ','-')}-{ano[-1]}-{agregacao}.geojson")


if __name__ == '__main__':
    # app.run_server(debug=True)
    # app.run_server(debug=True, host='0.0.0.0', ssl_context='adhoc')
    app.run_server(debug=True, host='0.0.0.0')
    
