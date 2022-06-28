# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# from cgitb import enable
# from faulthandler import disable
from cgitb import enable
from faulthandler import disable
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
df_iptu_censo = vaex.open('data/IPTU-1995-2022-agrupados-por-censo.hdf5')
# df_iptu_sq = vaex.open('data/IPTU-1995-2022-agrupados-por-sq.hdf5')

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

gdf_censo = gpd.read_file('data/areas-ponderacao-censo.gpkg', layer='areas-ponderacao-censo-2010')
gdf_censo['area'] = gdf_censo.area
gdf_censo.geometry = gdf_censo.simplify(tolerance=100)
gdf_censo.to_crs(epsg=4674, inplace=True)

# gdf_quadras = gpd.read_file('data/quadras.gpkg')
# gdf_quadras.to_crs(epsg=4674, inplace=True)

# routes_pathname_prefix='/dash-iptu/'

# if 'DASH_ENV' in os.environ: 
#     if os.environ['DASH_ENV'] == 'production':
#         routes_pathname_prefix='/'

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    # as the proxy server will remove the prefix
    ## TODO IF PRODUCTION
    # routes_pathname_prefix='/',
    # routes_pathname_prefix=routes_pathname_prefix,

    # the front-end will prefix this string to the requests
    # that are made to the proxy server
    # requests_pathname_prefix='/dash-iptu/'
)

server = app.server

my_output = html.Div()

radioitems = html.Div(
    [
        dbc.Label("Selecione a agregação espacial"),
        dbc.RadioItems(
            options=[
                {"label": "Subprefeituras", "value": 'subprefeituras', "disabled": False},
                {"label": "Distritos", "value": 'distritos'},
                {"label": "Zonas OD", "value": 'zonas-od', "disabled": False},
                {"label": "Macroáreas PDE(2014)", "value": 'macro-areas', "disabled": True},
                {"label": "Áreas de Ponderação do CENSO(2010)", "value": 'censo', "disabled": False},
                {"label": "Quadras/Lotes Fiscais", "value": 'quadras', "disabled": True},
            ],
            value='distritos',
            id="radioitems-input"
        ),
    ]
)

atributos = [
    "Quantidade de Unidades Condominiais",
    "Tamanho Médio da Unidade Condominial",
    "Tamanho médio dos Terrenos",
    "Área Total dos terrenos-lotes",
    "Área Total Ocupada",
    "Área Total Construída",
    "Valor Total dos Terrenos",
    "Valor Total das Construções",
    "CA médio",
    "TO médio",
    "CA médio em lotes condominiais",
    "TO médio em lotes condominiais",
    "CA médio em lotes não condominiais",
    "TO médio em lotes não condominiais",
    "Comprimento Médio da Testada",
    "Número médio de Pavimentos",
    "Fator de obsolecência médio",
    "Percentual de Uso Residencial",
    "Percentual de Uso Comercial",
    "Percentual de Uso Serviços",
    "Percentual de Uso Industrial",
    "Percentual de Uso Outros"
]

checklist = html.Div(
    [
        dbc.Label("Selecione as totalizações, índices ou Quantitativos"),
        dcc.Dropdown(atributos, "Área Total Construída", id='dropdown-input', clearable=False),
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

como_citar = html.Div(
    [
        dbc.Button(
            "Como Citar",
            id="positioned-toast-toggle",
            color="primary",
            n_clicks=0,
        ),
        dbc.Toast(
            "Aqui em breve informações de como citar este trabalho",
            id="positioned-toast",
            header="Como citar o Dash do IPTU",
            is_open=False,
            dismissable=True,
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),
    ]
)

navbar = dbc.NavbarSimple(
    children=[
        como_citar,
    ],
    brand="CEM - Centro de Estudo das Metrópoles - Dash IPTU de São Paulo (1995-2022) - V.0.4.3",
    brand_href="#",
    color="#003366",
    dark=True
)

app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            dbc.Col(
                [html.Br(),
                dcc.Tabs(id='tab', value='atributo', children=[
                    dcc.Tab(label='Sobre o Dash do IPTU', value='sobre', id='tab-0', disabled=False),
                    dcc.Tab(label='Área Total Construída em 2022', value='atributo', id='tab-1'),
                    dcc.Tab(label='Diferença de 1995 à 2022', value='diferenca', id='tab-2'),
                    dcc.Tab(label='Descrição do cálculo/processamento para Área Total Construída', value='descricao', id='tab-3', disabled=True),
                ]),
                dbc.Offcanvas(
                    dcc.Markdown('''
                        Prova de conceito em fase de pré-testes para validação do uso da série histórica dos dados de IPTU de São Paulo, com mais de 83 milhões de registros, com objetivo de visualização e exportação de dados agregados espacialmente para disseminação de seu uso para diversas disciplinas e finalidades.

                        Código disponível em [https://dashiptu.centrodametropole.fflch.usp.br/] comentários, sugestões, inconsistências reportar preferencialmente por `issue` no GitHub ou por email para [feromes@usp.br](mailto:feromes@usp.br)
                        '''),
                    id="offcanvas",
                    title="Sobre o Dash do IPTU de São Paulo",
                    is_open=False,
                    placement='bottom'
                ),
          ])
        ),
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id='loading-map',
                    type='default',
                    # fullscreen=True,
                    children=html.Div(id='loading-output')
                ),
                dbc.Form([range_slider])
            ]),
        ]),
        dbc.Row([
            dbc.Col(
                [dbc.Form([radioitems]),
                dbc.Form([checklist]),
                html.Br(),
                dbc.Button('Download', id='download-button', n_clicks=0),
                html.Br()]
            ),
            dbc.Col(
                [dcc.Graph(id="graph"),
                dcc.Download(id="download-gpkg")], width=8
            )]
        ),
    ])



@app.callback(
    Output("graph", "figure"), 
    Output("loading-map", "children"),
    Output("registros-calculados", 'children'),
    Output("tab-1", "label"),
    Output("tab-2", "label"),
    Output("tab-3", "label"),
    Input("dropdown-input", "value"),
    Input("range-slider", "value"),
    Input("radioitems-input", "value"),
    Input("tab", "value"),
    State('graph', 'figure'))
def update_map(atributo, ano, agregacao, tab, mapa_atual):

    if mapa_atual:
        zoom = mapa_atual['layout']['mapbox']['zoom']
        center = mapa_atual['layout']['mapbox']['center']
    else:
        zoom, center = 9, {'lat':-23.62095411, 'lon':-46.61666592}

    gdf_agregacao, hover_data, custom_data, min_max, gdf, gdf_diff, min_max_diff = sel_agregacao(agregacao, ano, atributo)

    if tab == 'atributo':
        registros = f"{format(gdf_agregacao['Quantidade de Unidades'].sum(), ',d').replace(',', '.')} registros calculados"
        # Escalas de Cores disponíveis em: https://plotly.com/python/builtin-colorscales/
        color_continuous_scale='turbo'
        # color_continuous_midpoint = (min_max[1] - min_max[0])/2
        gdf_map = gdf_agregacao
        range_color=min_max
    else:
        registros = f"{format(gdf['Quantidade de Unidades'].sum(), ',d').replace(',', '.')} registros calculados"
        color_continuous_scale='RdYlBu'
        print(min_max_diff)
        color_continuous_midpoint = 0.0
        # color_continuous_midpoint = (min_max[1] - min_max[0])/2
        gdf_map = gdf_diff
        range_color=min_max_diff

    fig = px.choropleth_mapbox(gdf_map,
                    geojson=gdf_map.geometry,
                    color_continuous_scale=color_continuous_scale,
                    # color_continuous_midpoint=color_continuous_midpoint,
                    zoom=zoom,
                    center=center,
                    # animation_frame='ano',
                    #  projection="transverse mercator",
                    color=atributo,
                    range_color=range_color,
                    locations=gdf_map.index.to_list(),
                    mapbox_style="white-bg",
                    hover_data=hover_data,
                    # custom_data=custom_data,
                    height=600,
                    width=800)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                    title={'text': 'Seila'})

    loading = None
    
    tab1 = f"{atributo} em {ano[-1]}"
    tab2 = f"Diferença em {atributo} de {ano[0]} à {ano[-1]}"
    tab3 = f"Descrição do cálculo/processamento para {atributo}"

    # print(min_max_diff)

    return fig, loading, registros, tab1, tab2, tab3 


def sel_agregacao(agregacao, ano, atributo):

    if agregacao == 'distritos':
        gdf = gdf_distritos.astype({'ds_codigo': 'int'})\
            .merge(df_iptu_distrito[(df_iptu_distrito.ano >= ano[0]) & (df_iptu_distrito.ano <= ano[-1])].to_pandas_df(), \
                left_on='ds_codigo', right_on='distrito')\
                    [["ds_codigo", "ds_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_agregacao = gdf.loc[gdf.ano == ano[-1]]
        diff = gdf.pivot(index='ds_codigo', columns='ano', values=atributo)
        gdf_diff = gdf_distritos.astype({'ds_codigo': 'int'}).set_index('ds_codigo').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])
        gdf_agregacao.set_index('ds_codigo', inplace=True)
        hover_data = ["ds_nome"]
        custom_data=["ds_codigo"]
        min_max = [df_iptu_distrito[atributo].min().item(), df_iptu_distrito[atributo].max().item()]
        # min_max_diff = [gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()]

    if agregacao == 'subprefeituras':
        gdf = gdf_subprefeitura.astype({'sp_codigo': 'int'})\
            .merge(df_iptu_subprefeitura[(df_iptu_subprefeitura.ano >= ano[0]) & (df_iptu_subprefeitura.ano <= ano[-1])].to_pandas_df(), \
                left_on='sp_codigo', right_on='subprefeitura')\
                    [["sp_codigo", "sp_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_agregacao = gdf.loc[gdf.ano == ano[-1]]
        diff = gdf.pivot(index='sp_codigo', columns='ano', values=atributo)
        gdf_diff = gdf_subprefeitura.astype({'sp_codigo': 'int'}).set_index('sp_codigo').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])
        gdf_agregacao.set_index('sp_codigo', inplace=True)
        hover_data = ["sp_nome"]
        custom_data=["sp_codigo"]
        min_max = [df_iptu_subprefeitura[atributo].min().item(), df_iptu_subprefeitura[atributo].max().item()]
        # min_max_diff = [gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()]

    if agregacao == 'zonas-od':
        gdf = gdf_od.astype({'od_id': 'int'})\
            .merge(df_iptu_od[(df_iptu_od.ano >= ano[0]) & (df_iptu_od.ano <= ano[-1])].to_pandas_df(), \
                left_on='od_id', right_on='od')\
                    [["od_id", "od_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_agregacao = gdf.loc[gdf.ano == ano[-1]]
        diff = gdf.pivot(index='od_id', columns='ano', values=atributo)
        gdf_diff = gdf_od.astype({'od_id': 'int'}).set_index('od_id').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])
        gdf_agregacao.set_index('od_id', inplace=True)
        hover_data = ["od_nome"]
        custom_data=["od_id"]
        min_max = [df_iptu_od[atributo].min().item(), df_iptu_od[atributo].max().item()]
    
    if agregacao == 'censo':
        gdf = gdf_censo.astype({'COD_AED_S': 'int'})\
            .merge(df_iptu_censo[(df_iptu_censo.ano >= ano[0]) & (df_iptu_censo.ano <= ano[-1])].to_pandas_df(), \
                left_on='COD_AED_S', right_on='censo')\
                    [["COD_AED_S", "COD_AED", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_agregacao = gdf.loc[gdf.ano == ano[-1]]
        diff = gdf.pivot(index='COD_AED_S', columns='ano', values=atributo)
        gdf_diff = gdf_censo.astype({'COD_AED_S': 'int'}).set_index('COD_AED_S').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])
        gdf_agregacao.set_index('COD_AED_S', inplace=True)
        hover_data = ["COD_AED"]
        custom_data=["COD_AED_S"]
        min_max = [df_iptu_censo[atributo].min().item(), df_iptu_censo[atributo].max().item()]

    max_value = abs(max([gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()], key=abs))
    min_max_diff = [-1 * max_value, max_value]
    # min_max_diff = [gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()]

    return gdf_agregacao, hover_data, custom_data, min_max, gdf, gdf_diff, min_max_diff

@app.callback(
    Output("download-gpkg", "data"),
    Input("download-button", "n_clicks"),
    State("dropdown-input", "value"),
    State("range-slider", "value"),
    State("radioitems-input", "value"),
    State("tab", "value"),
    prevent_initial_call=True,
)
def func(n_clicks, atributo, ano, agregacao, tab):
    if tab != "diferenca":
        return dict(content=sel_agregacao(agregacao, ano, atributo)[0].to_json(), 
                    filename=f"IPTU-SP-{atributo.replace(' ','-')}-{ano[-1]}-por-{agregacao}.geojson")
    else:
        return dict(content=sel_agregacao(agregacao, ano, atributo)[5].to_json(), 
                    filename=f"IPTU-SP-diferenca-de-{atributo.replace(' ','-')}-{ano[0]}-ate-{ano[-1]}-por-{agregacao}.geojson")

@app.callback(
    Output("offcanvas", "is_open"),
    Output("tab", "value"),
    Input("tab", "value"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1 == 'sobre':
        return not is_open, "atributo"
    return is_open, n1



@app.callback(
    Output("positioned-toast", "is_open"),
    [Input("positioned-toast-toggle", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False

if __name__ == '__main__':
    # app.run_server(debug=True)
    # app.run_server(debug=True, host='0.0.0.0', ssl_context='adhoc')
    app.run_server(debug=True, host='0.0.0.0')
    
