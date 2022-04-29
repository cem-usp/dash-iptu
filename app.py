# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# from cgitb import enable
# from faulthandler import disable
import geopandas as gpd
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import vaex

df_iptu_distrito = vaex.open('data/IPTU-1995-2022-agrupados-por-distrito.hdf5')
df_iptu_subprefeitura = vaex.open('data/IPTU-1995-2022-agrupados-por-subprefeitura.hdf5')
df_iptu_od = vaex.open('data/IPTU-1995-2022-agrupados-por-od.hdf5')

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

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.config.update({
    # as the proxy server will remove the prefix
    'routes_pathname_prefix': '/', 

    # the front-end will prefix this string to the requests
    # that are made to the proxy server
    'requests_pathname_prefix': '/dash-iptu/'
})

server = app.server

my_output = html.Div()

radioitems = html.Div(
    [
        dbc.Label("Selecione a agregação espacial"),
        dbc.RadioItems(
            options=[
                {"label": "Subprefeituras", "value": 2, "disabled": False},
                {"label": "Distritos", "value": 1},
                {"label": "Zonas OD", "value": 3, "disabled": False},
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

    gdf_agregacao, hover_data, custom_data = sel_agregacao(agregacao, ano)

    fig = px.choropleth_mapbox(gdf_agregacao,
                    geojson=gdf_agregacao.geometry,
                    zoom=zoom,
                    center=center,
                    #  projection="transverse mercator",
                    color=atributo,
                    locations=gdf_agregacao.index.to_list(),
                    mapbox_style="white-bg",
                    hover_data=hover_data,
                    custom_data=custom_data,
                    height=600,
                    width=800)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                    title={'text': 'Seila'})

    return fig

@app.callback(
    Output("table", "columns"),
    Output("table", "data"), 
    Input("checklist-input", "value"))
def gen_table(atributo):
    df = df_iptu_distrito.to_pandas_df().merge(gdf_distritos.loc[:, ['ds_codigo', 'ds_nome']].astype({'ds_codigo': 'int'}), left_on='distrito', right_on='ds_codigo')
    df_pivot = df.pivot(index=['distrito', 'ds_nome'], values=atributo, columns='ano')
    columns=[{"name": str(i), "id": str(i)} for i in df_pivot.reset_index().columns]
    data=df_pivot.reset_index().to_dict("records")
    return columns, data

@app.callback(
    Output("table-title", "children"),
    Input("checklist-input", "value"))
def change_title(atributo):
    return f'Download da série histórica para {atributo} por Distrito'

def sel_agregacao(agregacao, ano):

    if agregacao == 1:
        gdf_agregacao = gdf_distritos.astype({'ds_codigo': 'int'}).merge(df_iptu_distrito[df_iptu_distrito.ano == ano].to_pandas_df(), left_on='ds_codigo', right_on='distrito')
        hover_data = ["ds_nome"]
        custom_data=["ds_codigo"]

    if agregacao == 2:
        gdf_agregacao = gdf_subprefeitura.astype({'sp_codigo': 'int'}).merge(df_iptu_subprefeitura[df_iptu_subprefeitura.ano == ano].to_pandas_df(), left_on='sp_codigo', right_on='subprefeitura')
        hover_data = ["sp_nome"]
        custom_data=["sp_codigo"]

    if agregacao == 3:
        gdf_agregacao = gdf_od.astype({'od_id': 'int'}).merge(df_iptu_od[df_iptu_od.ano == ano].to_pandas_df(), left_on='od_id', right_on='od')        
        hover_data = ["od_nome"]
        custom_data=["od_id"]

    return gdf_agregacao, hover_data, custom_data

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, host='0.0.0.0')
    
