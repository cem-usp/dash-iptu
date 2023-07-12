# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# from cgitb import enable
# from faulthandler import disable
from cgitb import enable
from email import header
from faulthandler import disable
from certifi import contents
import geopandas as gpd
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, dash_table, callback_context
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import vaex
import os

EXERCICIO = 2023

df_iptu_distrito = vaex.open(f'data/IPTU-1995-{EXERCICIO}-agrupados-por-distrito.hdf5')
df_iptu_subprefeitura = vaex.open(f'data/IPTU-1995-{EXERCICIO}-agrupados-por-subprefeitura.hdf5')
df_iptu_od = vaex.open(f'data/IPTU-1995-{EXERCICIO}-agrupados-por-od.hdf5')
df_iptu_censo = vaex.open(f'data/IPTU-1995-{EXERCICIO}-agrupados-por-censo.hdf5')
df_iptu_sq = vaex.open(f'data/IPTU-1995-{EXERCICIO}-agrupados-por-sq.hdf5')

gdf_distritos = gpd.read_file('data/SIRGAS_GPKG_distrito.gpkg')
# gdf_distritos['area'] = gdf_distritos.area
gdf_distritos_download = gdf_distritos.copy(deep=True)
gdf_distritos.geometry = gdf_distritos.simplify(tolerance=100)
gdf_distritos.to_crs(epsg=4674, inplace=True)

gdf_od = gpd.read_file('zip://data/SIRGAS_SHP_origemdestino_2017.zip!SIRGAS_SHP_origemdestino_2017', crs='EPSG:31983')
gdf_od = gdf_od[gdf_od.od_municip == '36']
gdf_od.set_crs(epsg=31983, inplace=True)
# gdf_od['area'] = gdf_od.area
gdf_od_download = gdf_od.copy(deep=True)
gdf_od.geometry = gdf_od.simplify(tolerance=10)
gdf_od.to_crs(epsg=4674, inplace=True)

gdf_subprefeitura = gpd.read_file('zip://data/SIRGAS_GPKG_subprefeitura.zip!SIRGAS_GPKG_subprefeitura.gpkg')
# gdf_subprefeitura['area'] = gdf_subprefeitura.area
gdf_subprefeitura_download = gdf_subprefeitura.copy(deep=True)
gdf_subprefeitura.geometry = gdf_subprefeitura.simplify(tolerance=100)
gdf_subprefeitura.to_crs(epsg=4674, inplace=True)

gdf_censo = gpd.read_file('data/areas-ponderacao-censo.gpkg', layer='areas-ponderacao-censo-2010')
# gdf_censo['area'] = gdf_censo.area
gdf_censo_download = gdf_censo.copy(deep=True)
gdf_censo.geometry = gdf_censo.simplify(tolerance=100)
gdf_censo.to_crs(epsg=4674, inplace=True)

gdf_quadras = gpd.read_file('data/quadras.gpkg')
gdf_quadras.to_crs(epsg=4674, inplace=True)

distritos_items = [{"label": d.ds_nome, "value": d.ds_codigo} for i, d in gdf_distritos.sort_values('ds_nome').iterrows()]

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
                {"label": "Zonas OD (2017)", "value": 'zonas-od', "disabled": False},
                {"label": "Macroáreas PDE(2014)", "value": 'macro-areas', "disabled": True},
                {"label": "Áreas de Ponderação do CENSO(2010)", "value": 'censo', "disabled": False},
            ],
            value='distritos',
            id="radioitems-input"
        ),
    ]
)

# atributos = [
#     "Quantidade de Unidades Condominiais",
#     "Tamanho Médio da Unidade Condominial",
#     "Tamanho médio dos Terrenos",
#     "Área Total dos terrenos-lotes",
#     "Área Total Ocupada",
#     "Área Total Construída",
#     "Valor Total dos Terrenos",
#     "Valor Total das Construções",
#     "CA médio",
#     "TO médio",
#     "CA médio em lotes condominiais",
#     "TO médio em lotes condominiais",
#     "CA médio em lotes não condominiais",
#     "TO médio em lotes não condominiais",
#     "Comprimento Médio da Testada",
#     "Número médio de Pavimentos",
#     "Fator de obsolecência médio",
#     "Percentual de Uso Residencial",
#     "Percentual de Uso Comercial",
#     "Percentual de Uso Serviços",
#     "Percentual de Uso Industrial",
#     "Percentual de Uso Outros"
# ]

atributos = [
    'Quantidade de Unidades',
    'Quantidade de Unidades Condominiais',
    'Tamanho Médio da Unidade Condominial',
    'Tamanho médio dos Terrenos',
    'Área Total dos lotes',
    'Área Total Ocupada',
    'Área Total Construída',
    'Valor Total dos Terrenos',
    'Valor Total das Construções',
    'CA médio',
    'TO médio',
    'CA médio em lotes condominiais',
    'TO médio em lotes condominiais',
    'CA médio em lotes não condominiais',
    'TO médio em lotes não condominiais',
    'Comprimento Médio da Testada',
    'Número médio de Pavimentos',
    'Fator de obsolecência médio',
    'Residencial vertical Baixo (m2)',
    'Residencial vertical Médio (m2)',
    'Residencial vertical Alto (m2)',
    'Residencial horizontal Baixo (m2)',
    'Residencial horizontal Médio (m2)',
    'Residencial horizontal Alto (m2)',
    'Comercial vertical Baixo (m2)',
    'Comercial vertical Médio (m2)',
    'Comercial vertical Alto (m2)',
    'Comercial horizontal Baixo (m2)',
    'Comercial horizontal Alto (m2)',
    'Comercial horizontal Médio (m2)',
    'Terreno (m2)',
    'Outros Usos (m2)',
    'Residencial vertical Baixo (qt)',
    'Residencial vertical Médio (qt)',
    'Residencial vertical Alto (qt)',
    'Residencial horizontal Baixo (qt)',
    'Residencial horizontal Médio (qt)',
    'Residencial horizontal Alto (qt)',
    'Comercial vertical Baixo (qt)',
    'Comercial vertical Médio (qt)',
    'Comercial vertical Alto (qt)',
    'Comercial horizontal Baixo (qt)',
    'Comercial horizontal Alto (qt)',
    'Comercial horizontal Médio (qt)',
    'Terreno (qt)',
    'Outros Usos (qt)'
]

checklist = html.Div(
    [
        html.Hr(),
        dbc.Label("Selecione as totalizações, índices ou quantitativos"),
        dcc.Dropdown(atributos, 'Área Total Construída', id='dropdown-input', clearable=False),
    ]
)

range_slider = html.Div(
    [
        dbc.Label("82.322.059 registros calculados", id="registros-calculados"),
        dcc.RangeSlider(id="range-slider", 
                        min=1995, 
                        max=EXERCICIO, 
                        step=1, 
                        updatemode='drag',
                        # value=[EXERCICIO,EXERCICIO],
                        value=[1995,EXERCICIO],
                        marks={1995: '1995',2000: '2000', 2005: '2005', 2010: '2010', 2015: '2015', 2020: '2020'},
                        pushable=True),
    ],
    className="ano-exercicio",
)


bibtext = """@misc{Gomes_2022,
	doi = {10.55881/cem.db.dash01},
	url = {https://doi.org/10.55881/cem.db.dash01},
	year = 2022,
	month = {sep},
	publisher = {Centro de Estudos da Metropole},
	author = {Fernando Gomes, Mariana Abrantes Giannotti and Luciana Salvarani},
	title = {Painel Cadastral da Cidade de São Paulo}
}"""

como_citar = html.Div(
    [
        dbc.Button("Como citar", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Como citar este Painel e seus dados")),
                dbc.ModalBody([
                    html.P("GOMES, Fernando; GIANNOTTI, Mariana Abrantes; SALVARANI, Luciana. Painel Cadastral da Cidade de São Paulo, desenvolvido pelo Centro de Estudos da Metrópole (CEM). Disponível em: <https://doi.org/10.55881/cem.db.dash01>.", id='citacao_abnt'),
                    
                    dcc.Clipboard(
                        target_id="citacao_abnt",
                        title="copy",
                        style={
                            # "display": "inline-block",
                            "fontSize": 20,
                            "verticalAlign": "top",
                        },
                    ),    

                    html.Code(bibtext, id='citacao_bibtex'),

                    dcc.Clipboard(
                        target_id="citacao_bibtex",
                        title="copy",
                        style={
                            # "display": "inline-block",
                            "fontSize": 20,
                            "verticalAlign": "top",
                        },
                    ),    


                ]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)


navbar = dbc.NavbarSimple(
    children=[
        html.Img(src=app.get_asset_url('cem-geoinfo-tudo-branco.png'), height="50px"),
        como_citar,
    ],
    brand=f"Painel Cadastral da Cidade de São Paulo (1995-{EXERCICIO}) - V.0.5.0",
    brand_href="#",
    color="#003366",
    dark=True
)

# menu_lateral = dbc.Col(
#     [dbc.Form([radioitems]),
#     dbc.Form([checklist]),
#     html.Br(),
#     dbc.Button('Download dos dados do mapa (.gpkg)', id='download-button', n_clicks=0),
#     html.Hr(),
#     html.P("Para agregações menores, selecione o distrito abaixo e escolha a opção"),
#     dbc.Select(
#         id='download_por_lotes',
#         options=distritos_items
#     ),
#     html.Br(),
#     dbc.DropdownMenu(
#         label="Download",
#         children=[
#             dbc.DropdownMenuItem(".. por Quadras", id='download-button-quadra', n_clicks=0),
#             dbc.DropdownMenuItem(".. por Lotes", id='download-button-lotes', n_clicks=0)
#         ],
#     ),
#     html.Br(),
#     dcc.Markdown(id='markdown-descricao-atributo')]
# )

accordion = dbc.Accordion(
[
    dbc.AccordionItem(
        [
            dbc.Form([radioitems]),
        ],
        title="Agregação Espacial",
    ),
    dbc.AccordionItem(
        [
            dbc.Form([checklist]),
        ],
        title="Atributo",
    ),
    dbc.AccordionItem(
        [
            html.Br(),
            dbc.Button('Download dos dados do mapa (.gpkg)', id='download-button', n_clicks=0),
            html.Hr(),
            html.P("Para agregações menores, selecione o distrito abaixo e escolha a opção"),
            dbc.Select(
                id='download_por_lotes',
                options=distritos_items
            ),
            html.Br(),
            dbc.DropdownMenu(
                label="Download",
                children=[
                    dbc.DropdownMenuItem(".. por Quadras", id='download-button-quadra', n_clicks=0),
                    dbc.DropdownMenuItem(".. por Lotes", id='download-button-lotes', n_clicks=0)
                ],
            ),
            html.Br(),
            html.A('Para o download de todos os distritos por lotes ou quadras utilize nosso repositório no GitHub', href='https://github.com/cem-usp/dash-iptu', target='_blank'),
            # dcc.Markdown('[Para o download de todos os distritos por lotes ou quadras utilize nosso repositório no GitHub](https://github.com/cem-usp/dash-iptu){:target="_blank"}'),
        ],
        title="Download dos dados",
    ),
    dbc.AccordionItem(
        [dcc.Markdown(id='markdown-descricao-atributo')],
        title="Informações",
    ),
],
)

menu_lateral = dbc.Col(
    [accordion, 


    ]
)

app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            dbc.Col(
                [html.Br(),
                dcc.Tabs(id='tab', value='atributo', children=[
                    dcc.Tab(label='Sobre o Painel Cadastral', value='sobre', id='tab-0', disabled=False),
                    dcc.Tab(label=f'Área Total Construída em {EXERCICIO}', value='atributo', id='tab-1'),
                    dcc.Tab(label=f'Diferença de 1995 à {EXERCICIO}', value='diferenca', id='tab-2'),
                    # dcc.Tab(label='Descrição do cálculo/processamento para Área Total Construída', value='descricao', id='tab-3', disabled=True),
                ]),
                dbc.Offcanvas(
                    dcc.Markdown('''
                        O Painel Cadastral da Cidade de São Paulo é uma ferramenta que permite acesso rápido às informações cadastrais dos imóveis da cidade, onde há incidência de Imposto Predial e Territorial Urbano – Emissão Geral (IPTU-EG). É um avanço para a democraticação e disseminação de acesso a tais dados, uma vez que as fontes originais disponíveis para download no site do GeoSampa possuem mais de 86 milhões de registros com dezenas de atributos e sem espacialização.

                        Portanto, essa ferramenta surge a partir do acordo de cooperação técnica entre o Centro de Estudos da Metrópole (CEM) e a Secretaria Municipal de Urbanismo e Licensiamento (SMUL), com a intenção de disseminar e facilitar o acesso a esse conjunto de dados muito importante para entender as dinâmicas de uso e ocupação na cidade de São Paulo.

                        Essa ferramenta foi elaborada somente a partir de dados abertos, disponíveis a qualquer pessoa e utilizando apenas bibliotecas e softwares livres. Como não poderia deixar de ser diferente, todo o processo de desenvolvimento e código está disponível para download, melhorias e contribuições ([https://github.com/cem-usp/dash-iptu]). Sobretudo, como é uma ferramenta em pleno desenvolvimento as interações são bem vindas, assim como comentários, sugestões, inconsistências que podem ser reportadas abrindo `issue` no (GitHub do Painel de Dados da Cidade)[https://github.com/cem-usp/dash-iptu]


                        '''),
                    id="offcanvas",
                    title="Sobre o Painel Cadastral de São Paulo",
                    is_open=False,
                    # placement='left'
                ),

                # dbc.Modal(
                #     [
                #         dbc.ModalHeader(dbc.ModalTitle("Scrolling modal")),
                #         dbc.ModalBody('''
                #         O Painel Cadastral da Cidade de São Paulo é uma ferramenta que permite acesso rápido às informações cadastrais dos imóveis da cidade, onde há incidência de IPTU. É um avanço para a democraticação e disseminação de acesso a tais dados, uma vez que as fontes originais disponíveis para download no site do GeoSampa possuem mais de 86 milhões de registros com dezenas de atributos e sem espacialização.

                #         Portanto, essa ferramenta surge a partir do acordo de cooperação técnica entre o Centro de Estudos da Metrópole (CEM) e a Secretaria Municipal de Urbanismo e Licensiamento (SMUL), com a intenção de disseminar e facilitar o acesso a esse conjunto de dados muito importante para entender as dinâmicas de uso e ocupação na cidade de São Paulo.

                #         Essa ferramenta foi elaborada somente a partir de dados abertos, disponíveis a qualquer pessoa e utilizando apenas bibliotecas e softwares livres. Como não poderia deixar de ser diferente, todo o processo de desenvolvimento e código está disponível para download, melhorias e contribuições ([https://github.com/cem-usp/dash-iptu]). Sobretudo, como é uma ferramenta em pleno desenvolvimento as interações são bem vindas, assim como comentários, sugestões, inconsistências que podem ser reportadas abrindo `issue` no (GitHub do Painel de Dados da Cidade)[https://github.com/cem-usp/dash-iptu]


                #         '''),
                #         dbc.ModalFooter(
                #             dbc.Button(
                #                 "Close",
                #                 id="offcanvas",
                #                 className="ms-auto",
                #                 n_clicks=0,
                #             )
                #         ),
                #     ],
                #     id="modal-scroll",
                #     is_open=False,
                # ),
                
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
                dcc.Loading(
                    id='downloading',
                    type='default',
                    fullscreen=True,
                    children=html.Div(id='downloading-output')
                ),
                dbc.Form([range_slider])
            ]),
        ]),
        dbc.Row([
            menu_lateral, 
            dbc.Col(
                [dcc.Graph(id="graph"),
                dcc.Download(id="download-gpkg"),
                dcc.Download(id="download-quadras"),
                dcc.Download(id="download-lotes")], width=8
            )]
        ),
        dbc.Row([
            # dbc.Col(),
            html.Hr(),
            dbc.Row([
                dcc.Markdown('Realização:'),
                dbc.Col(html.Img(src=app.get_asset_url('cem-alta.jpg'), height="100px"), width=4),
                dbc.Col(html.Img(src=app.get_asset_url('URBANISMO_E_LICENCIAMENTO_HORIZONTAL_FUNDO_CLARO.png'), height="85px"), width=4),
                dbc.Col(html.Div("Parceria firmada pelo acordo de cooperação técnica entre o Centro de Estudo da Matrópole (CEM) e a Secretaria Municipal de Urbanismo e Licensiamento (SMUL nº001/2022/SMUL)"))
            ]),
        ]),
        dbc.Row(children=[
            # dbc.Col(),
            html.Br(),
            dcc.Markdown('Apoio:'),
            dbc.Col(html.Img(src=app.get_asset_url('cebrap.jpg'), height="75px"), width=2),
            dbc.Col(html.Img(src=app.get_asset_url('logo-fapesp-2.png'), height="75px"), width=2),
            dbc.Col(html.Img(src=app.get_asset_url('cepid.jpg'), height="75px"), width=2),
            dbc.Col(html.Img(src=app.get_asset_url('usp.jpg'), height="75px"), width=2),
            dbc.Col(html.Img(src=app.get_asset_url('fflch.jpg'), height="50px"), width=2),],
            style={'padding-top': '30px'}
        )
    ])



@app.callback(
    Output("graph", "figure"), 
    Output("loading-map", "children"),
    Output("registros-calculados", 'children'),
    Output("tab-1", "label"),
    Output("tab-2", "label"),
    # Output("tab-3", "label"),
    Output('markdown-descricao-atributo', 'children'),
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

    gdf_agregacao, hover_data, custom_data, min_max, gdf, gdf_diff, min_max_diff, gdf_total, gdf_diff_download = sel_agregacao(agregacao, ano, atributo)

    if tab == 'atributo':
        # print(gdf_agregacao.iloc[:, -1].sum())
        registros = f"{gdf_agregacao.iloc[:, -1].sum()} registros calculados"
        # registros = f"{gdf_agregacao.shape[0]} registros calculados"
        # Escalas de Cores disponíveis em: https://plotly.com/python/builtin-colorscales/
        color_continuous_scale='turbo'
        # color_continuous_midpoint = (min_max[1] - min_max[0])/2
        gdf_map = gdf_agregacao#.simplify(tolerance=100).set_crs(epsg=4674, allow_override=True)
        range_color=min_max
    else:
        registros = f"{gdf_agregacao.iloc[:, -1].sum()} registros calculados"
        color_continuous_scale='RdYlBu'
        color_continuous_midpoint = 0.0
        # color_continuous_midpoint = (min_max[1] - min_max[0])/2
        gdf_map = gdf_diff
        range_color=min_max_diff

    # gdf_map.geometry = gdf_distritos.simplify(tolerance=100)
    # gdf_map.to_crs(epsg=4674, inplace=True)

    ## BUG
    if atributo == 'Quantidade de Unidades' and tab == 'atributo':
        gdf_map = gdf_map.iloc[:, 0:3]
        
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

    r = open(f'descricao_atributos/{atributo}.md', 'r')

    return fig, loading, registros, tab1, tab2, r.read() 


def sel_agregacao(agregacao, ano, atributo, distrito=90):

    colums_str = dict()
    _ = [colums_str.update({c: str(c)}) for c in range(ano[0], ano[-1] + 1)]
    
    if agregacao == 'distritos':
        gdf = gdf_distritos.astype({'ds_codigo': 'int'})\
            .merge(df_iptu_distrito[(df_iptu_distrito.ano >= ano[0]) & (df_iptu_distrito.ano <= ano[-1])].to_pandas_df(), \
                left_on='ds_codigo', right_on='distrito')#\
                    # [["ds_codigo", "ds_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_agregacao = gdf.loc[gdf.ano == ano[-1], ["ds_codigo", "ds_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]

        gdf_download = gdf_distritos_download.astype({'ds_codigo': 'int'})\
            .merge(df_iptu_distrito[(df_iptu_distrito.ano >= ano[0]) & (df_iptu_distrito.ano <= ano[-1])].to_pandas_df(), \
                left_on='ds_codigo', right_on='distrito')#\
                    # [["ds_codigo", "ds_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]

        diff = gdf.pivot(index='ds_codigo', columns='ano', values=atributo)
        gdf_diff = gdf_distritos.astype({'ds_codigo': 'int'}).set_index('ds_codigo').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])

        diff_download = gdf_download.pivot(index='ds_codigo', columns='ano', values=atributo)
        gdf_diff_download = gdf_distritos_download.astype({'ds_codigo': 'int'}).set_index('ds_codigo').merge(diff_download, left_index=True, right_index=True, how='left')
        gdf_diff_download.loc[:, atributo] = (gdf_diff_download[ano[-1]] - gdf_diff_download[ano[0]])

        gdf_agregacao.set_index('ds_codigo', inplace=True)
        hover_data = ["ds_nome"]
        custom_data=["ds_codigo"]
        min_max = [df_iptu_distrito[atributo].min().item(), df_iptu_distrito[atributo].max().item()]
        # min_max_diff = [gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()]

    if agregacao == 'subprefeituras':
        gdf = gdf_subprefeitura.astype({'sp_codigo': 'int'})\
            .merge(df_iptu_subprefeitura[(df_iptu_subprefeitura.ano >= ano[0]) & (df_iptu_subprefeitura.ano <= ano[-1])].to_pandas_df(), \
                left_on='sp_codigo', right_on='subprefeitura')#\
                    # [["sp_codigo", "sp_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_download = gdf_subprefeitura_download.astype({'sp_codigo': 'int'})\
            .merge(df_iptu_subprefeitura[(df_iptu_subprefeitura.ano >= ano[0]) & (df_iptu_subprefeitura.ano <= ano[-1])].to_pandas_df(), \
                left_on='sp_codigo', right_on='subprefeitura')#\
                    # [["sp_codigo", "sp_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]

        gdf_agregacao = gdf.loc[gdf.ano == ano[-1], ["sp_codigo", "sp_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]

        diff = gdf.pivot(index='sp_codigo', columns='ano', values=atributo)
        gdf_diff = gdf_subprefeitura.astype({'sp_codigo': 'int'}).set_index('sp_codigo').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])

        diff_download = gdf_download.pivot(index='sp_codigo', columns='ano', values=atributo)
        gdf_diff_download = gdf_subprefeitura_download.astype({'sp_codigo': 'int'}).set_index('sp_codigo').merge(diff_download, left_index=True, right_index=True, how='left')
        gdf_diff_download.loc[:, atributo] = (gdf_diff_download[ano[-1]] - gdf_diff_download[ano[0]])
        
        gdf_agregacao.set_index('sp_codigo', inplace=True)
        hover_data = ["sp_nome"]
        custom_data=["sp_codigo"]
        min_max = [df_iptu_subprefeitura[atributo].min().item(), df_iptu_subprefeitura[atributo].max().item()]
        # min_max_diff = [gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()]

    if agregacao == 'zonas-od':
        gdf = gdf_od.astype({'od_id': 'int'})\
            .merge(df_iptu_od[(df_iptu_od.ano >= ano[0]) & (df_iptu_od.ano <= ano[-1])].to_pandas_df(), \
                left_on='od_id', right_on='od')#\
                    # [["od_id", "od_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_download = gdf_od_download.astype({'od_id': 'int'})\
            .merge(df_iptu_od[(df_iptu_od.ano >= ano[0]) & (df_iptu_od.ano <= ano[-1])].to_pandas_df(), \
                left_on='od_id', right_on='od')


        gdf_agregacao = gdf.loc[gdf.ano == ano[-1], ["od_id", "od_nome", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]

        diff = gdf.pivot(index='od_id', columns='ano', values=atributo)
        gdf_diff = gdf_od.astype({'od_id': 'int'}).set_index('od_id').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])


        diff_download = gdf_download.pivot(index='od_id', columns='ano', values=atributo)
        gdf_diff_download = gdf_od_download.astype({'od_id': 'int'}).set_index('od_id').merge(diff_download, left_index=True, right_index=True, how='left')
        gdf_diff_download.loc[:, atributo] = (gdf_diff_download[ano[-1]] - gdf_diff_download[ano[0]])

        gdf_agregacao.set_index('od_id', inplace=True)
        hover_data = ["od_nome"]
        custom_data=["od_id"]
        min_max = [df_iptu_od[atributo].min().item(), df_iptu_od[atributo].max().item()]
    
    if agregacao == 'censo':
        gdf = gdf_censo.astype({'COD_AED_S': 'int'})\
            .merge(df_iptu_censo[(df_iptu_censo.ano >= ano[0]) & (df_iptu_censo.ano <= ano[-1])].to_pandas_df(), \
                left_on='COD_AED_S', right_on='censo')#\
                    # [["COD_AED_S", "COD_AED", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]
        gdf_download = gdf_censo_download.astype({'COD_AED_S': 'int'})\
            .merge(df_iptu_censo[(df_iptu_censo.ano >= ano[0]) & (df_iptu_censo.ano <= ano[-1])].to_pandas_df(), \
                left_on='COD_AED_S', right_on='censo')

        gdf_agregacao = gdf.loc[gdf.ano == ano[-1], ["COD_AED_S", "COD_AED", atributo, 'geometry', 'ano', 'Quantidade de Unidades']]

        diff = gdf.pivot(index='COD_AED_S', columns='ano', values=atributo)
        gdf_diff = gdf_censo.astype({'COD_AED_S': 'int'}).set_index('COD_AED_S').merge(diff, left_index=True, right_index=True, how='left')
        gdf_diff.loc[:, atributo] = (gdf_diff[ano[-1]] - gdf_diff[ano[0]])

        diff_download = gdf_download.pivot(index='COD_AED_S', columns='ano', values=atributo)
        gdf_diff_download = gdf_censo_download.astype({'COD_AED_S': 'int'}).set_index('COD_AED_S').merge(diff_download, left_index=True, right_index=True, how='left')
        gdf_diff_download.loc[:, atributo] = (gdf_diff_download[ano[-1]] - gdf_diff_download[ano[0]])

        gdf_agregacao.set_index('COD_AED_S', inplace=True)
        hover_data = ["COD_AED"]
        custom_data=["COD_AED_S"]
        min_max = [df_iptu_censo[atributo].min().item(), df_iptu_censo[atributo].max().item()]

    max_value = abs(max([gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()], key=abs))
    min_max_diff = [-1 * max_value, max_value]
    gdf_total = gdf_download.loc[gdf.ano == ano[-1], :]
    gdf_diff_download.rename(columns=colums_str, inplace=True)
    gdf_diff.fillna(0.0, inplace=True)
    gdf_agregacao.fillna(0.0, inplace=True)
    gdf_total.fillna(0.0, inplace=True)
    gdf_diff_download.fillna(0.0, inplace=True)
    # min_max_diff = [gdf_diff[atributo].min().item(), gdf_diff[atributo].max().item()]

    return gdf_agregacao, hover_data, custom_data, min_max, gdf, gdf_diff, min_max_diff, gdf_total, gdf_diff_download

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
        # return dict(content=sel_agregacao(agregacao, ano, atributo)[7].to_json(), 
                    # filename=f"IPTU-SP-todos-atributos-{ano[-1]}-por-{agregacao}.geojson")
        return dcc.send_bytes(sel_agregacao(agregacao, ano, atributo)[7].to_file, f"IPTU-SP-todos-atributos-{ano[-1]}-por-{agregacao}.gpkg", driver='GPKG')

    else:
        # return dict(content=sel_agregacao(agregacao, ano, atributo)[5].to_json(), 
        #             filename=f"IPTU-SP-diferenca-de-{atributo.replace(' ','-')}-{ano[0]}-ate-{ano[-1]}-por-{agregacao}.geojson")
        return dcc.send_bytes(sel_agregacao(agregacao, ano, atributo)[8].to_file, f"IPTU-SP-diferenca-de-{atributo.replace(' ','-')}-{ano[0]}-ate-{ano[-1]}-por-{agregacao}.gpkg", driver='GPKG')
    
## Download dados agregados por quadra
@app.callback(
    Output("download-quadras", "data"),
    Output("downloading", "children"),
    Input("download-button-quadra", "n_clicks"),
    Input("download-button-lotes", "n_clicks"),
    State("dropdown-input", "value"),
    State("range-slider", "value"),
    State("radioitems-input", "value"),
    State("tab", "value"),
    State("download_por_lotes", "value"),
    prevent_initial_call=True,
)
def func(quadra, lotes, atributo, ano, agregacao, tab, download_por_lotes):
    # print(quadra, lotes)
    # print(callback_context.triggered)
    distrito = gdf_distritos[gdf_distritos.ds_codigo == download_por_lotes].iloc[0]
    quadras = gdf_quadras[gdf_quadras.ds_codigo == download_por_lotes]

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'download-button-quadra' in changed_id:    
        if tab != "diferenca":
            quadras = quadras.set_index('sq').join(df_iptu_sq[df_iptu_sq.ano == int(ano[-1])].to_pandas_df().set_index('sq'))
            # quadras.set_crs(epsg=31983, inplace=True)

            # return dict(content=quadras.to_json(), 
            #         filename=f"IPTU-SP-todos-atributos-{ano[-1]}-por-quadras-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.geojson"), None
            return dcc.send_bytes(quadras.to_file, f"IPTU-SP-todos-atributos-{ano[-1]}-por-quadras-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.gpkg", driver='GPKG'), None
        else:
            quadras = quadras.set_index('sq').join(df_iptu_sq[(df_iptu_sq.ano >= ano[0]) & (df_iptu_sq.ano <= ano[-1])][['sq', 'ano', atributo]].to_pandas_df().pivot(index='sq', columns='ano', values=atributo))
            # quadras.set_crs(epsg=31983, inplace=True)

            # return dict(content=quadras.to_json(), 
            #             filename=f"IPTU-SP-diferenca-de-{atributo.replace(' ','-')}-{ano[0]}-ate-{ano[-1]}-por-quadras-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.geojson"), None
            return dcc.send_bytes(quadras.to_file, f"IPTU-SP-diferenca-de-{atributo.replace(' ','-')}-{ano[0]}-ate-{ano[-1]}-por-quadras-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.gpkg", driver='GPKG'), None
        
    if 'download-button-lotes' in changed_id:

        agg_atributos = {
                'Quantidade de Unidades':'sum',
                'Quantidade de Unidades Condominiais':'sum',
                'Tamanho Médio da Unidade Condominial':'mean',
                'Tamanho médio dos Terrenos':'mean',
                'Área Total dos lotes':'sum',
                'Área Total Ocupada':'sum',
                'Área Total Construída':'sum',
                'Valor Total dos Terrenos':'sum',
                'Valor Total das Construções':'sum',
                'CA médio':'mean',
                'TO médio':'mean',
                'CA médio em lotes condominiais':'mean',
                'TO médio em lotes condominiais':'mean',
                'CA médio em lotes não condominiais':'mean',
                'TO médio em lotes não condominiais':'mean',
                'Comprimento Médio da Testada':'mean',
                'Número médio de Pavimentos':'mean',
                'Fator de obsolecência médio':'mean',
                'Residencial vertical Baixo (m2)':'sum',
                'Residencial vertical Médio (m2)':'sum',
                'Residencial vertical Alto (m2)':'sum',
                'Residencial horizontal Baixo (m2)':'sum',
                'Residencial horizontal Médio (m2)':'sum',
                'Residencial horizontal Alto (m2)':'sum',
                'Comercial vertical Baixo (m2)':'sum',
                'Comercial vertical Médio (m2)':'sum',
                'Comercial vertical Alto (m2)':'sum',
                'Comercial horizontal Baixo (m2)':'sum',
                'Comercial horizontal Alto (m2)':'sum',
                'Comercial horizontal Médio (m2)':'sum',
                'Terreno (m2)':'sum',
                'Outros Usos (m2)':'sum',
                'Residencial vertical Baixo (qt)':'sum',
                'Residencial vertical Médio (qt)':'sum',
                'Residencial vertical Alto (qt)':'sum',
                'Residencial horizontal Baixo (qt)':'sum',
                'Residencial horizontal Médio (qt)':'sum',
                'Residencial horizontal Alto (qt)':'sum',
                'Comercial vertical Baixo (qt)':'sum',
                'Comercial vertical Médio (qt)':'sum',
                'Comercial vertical Alto (qt)':'sum',
                'Comercial horizontal Baixo (qt)':'sum',
                'Comercial horizontal Alto (qt)':'sum',
                'Comercial horizontal Médio (qt)':'sum',
                'Terreno (qt)':'sum',
                'Outros Usos (qt)':'sum'
        }

        # print('lotes')
        
        # Abrindo Arquivo de lotes
        path = f'lotes_agregados_por_ano/{ano[-1]}/SIRGAS_SHP_LOTES_{distrito.ds_codigo.rjust(2, "0")}_{distrito.ds_nome.replace(" ", "_")}_IPTU_{ano[-1]}.gpkg'
        gdf_lote = gpd.read_file(path).drop_duplicates(subset=['sqlc']).set_index('sqlc')
        gdf_lote.to_crs(epsg=4674, inplace=True)
        gdf_lote = gdf_lote[gdf_lote.is_valid]

        # Abrindo arquivo com os dados agregados de IPTU por lote (SQLC)
        df_iptu = vaex.open(f'data/por_distritos/IPTU-1995-{EXERCICIO}-agrupados-por-sqlc-{distrito.ds_codigo}-{distrito.ds_nome.replace(" ", "-").lower()}.hdf5').to_pandas_df().set_index('sqlc')

        if tab != "diferenca":
            df_iptu = df_iptu[df_iptu.ano == ano[-1]]#[[atributo]]
            lotes_existentes = gdf_lote.join(df_iptu, how='inner')
            lotes_sg = df_iptu.join(gdf_lote, how='left').sq.isna()
            df_lotes_sg = df_iptu[lotes_sg].reset_index()
            df_lotes_sg.sqlc = df_lotes_sg.sqlc.str[:6] + '000000'
            df_lotes_sg_group = df_lotes_sg.groupby('sqlc').agg(agg_atributos)
            lotes_agregados = gdf_lote.join(df_lotes_sg_group, how='inner')
            lotes = pd.concat([lotes_existentes, lotes_agregados])

            # return dict(content=lotes.to_json(), 
            #         filename=f"IPTU-SP-todos-atributos-por-lotes-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.geojson"), None
            return dcc.send_bytes(lotes.to_file, f"IPTU-SP-todos-atributos-por-lotes-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.gpkg", driver='GPKG'), None
        else:
            df_iptu = df_iptu[(df_iptu.ano >= ano[0]) & (df_iptu.ano <= ano[-1])][['ano', atributo]].reset_index().pivot(index='sqlc', columns='ano', values=atributo)
            lotes_existentes = gdf_lote.join(df_iptu, how='inner')
            lotes_sg = df_iptu.join(gdf_lote, how='left').sq.isna()
            df_lotes_sg = df_iptu[lotes_sg].reset_index()
            df_lotes_sg.sqlc = df_lotes_sg.sqlc.str[:6] + '000000'
            df_lotes_sg_group = df_lotes_sg.groupby('sqlc').agg(agg_atributos[atributo])
            # Agora com as geometrias
            lotes_agregados = gdf_lote.join(df_lotes_sg_group, how='inner')
            lotes = pd.concat([lotes_existentes, lotes_agregados])

            # return dict(content=lotes.to_json(), 
            #         filename=f"IPTU-SP-diferenca-de-{atributo.replace(' ','-')}-{ano[-1]}-por-lotes-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.geojson"), None
            return dcc.send_bytes(lotes.to_file, f"IPTU-SP-diferenca-de-{atributo.replace(' ','-')}-{ano[-1]}-por-lotes-{download_por_lotes}-{distrito.ds_nome.lower().replace(' ', '-')}.gpkg", driver='GPKG'), None            

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
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# @app.callback(
#     Output("positioned-toast", "is_open"),
#     [Input("positioned-toast-toggle", "n_clicks")],
# )
# def open_toast(n):
#     if n:
#         return True
#     return False

if __name__ == '__main__':
    # app.run_server(debug=True)
    # app.run_server(debug=True, host='0.0.0.0', ssl_context='adhoc')
    app.run_server(debug=True, host='0.0.0.0')
    
