# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
# import pandas as pd
import geopandas as gpd
import vaex

df_iptu = vaex.open('data/IPTU_2022/IPTU_2022.hdf5')

gdf_distritos = gpd.read_file('data/SIRGAS_GPKG_distrito.gpkg')
gdf_quadras = gpd.read_file('zip://data/SIRGAS_SHP_quadraMDSF.zip!SIRGAS_SHP_quadraMDSF/SIRGAS_SHP_quadraMDSF.shp')
gdf_quadras = gdf_quadras.set_crs(epsg=31983)
gdf_quadras = gdf_quadras[gdf_quadras.qd_tipo == 'F']
gdf_quadras = gdf_quadras.dissolve(['qd_setor', 'qd_fiscal']).reset_index()
gdf_quadras_distritos = gdf_quadras.sjoin(gdf_distritos, how='left', predicate='intersects')
df_quadras_distritos = gdf_quadras_distritos.loc[:, ['qd_setor', 'qd_fiscal', 'ds_codigo', 'ds_nome', 'ds_cd_sub', 'ds_subpref']]
df_quadras_distritos.loc[:, ['sq']] = df_quadras_distritos.qd_setor + df_quadras_distritos.qd_fiscal
df_quadras_distritos.drop_duplicates(keep='first', inplace=True, ignore_index=True)
df_quadras_distritos = vaex.from_pandas(df_quadras_distritos)

df_iptu.setor = df_iptu['NUMERO DO CONTRIBUINTE'].str.slice(0,3)
df_iptu.quadra = df_iptu['NUMERO DO CONTRIBUINTE'].str.slice(3,6)
df_iptu.fillna(value='00-0', column_names=['NUMERO DO CONDOMINIO'], inplace=True)
df_iptu.fillna(value=1., column_names=['FRACAO IDEAL'], inplace=True)
df_iptu.fillna(value=0., column_names=['AREA CONSTRUIDA', 'AREA OCUPADA', 'AREA DO TERRENO'], inplace=True)
df_iptu.sqlc = df_iptu.func.where(df_iptu['NUMERO DO CONDOMINIO'] == '00-0',
                                df_iptu['NUMERO DO CONTRIBUINTE'].str.slice(0, 10) + '00',
                                df_iptu['NUMERO DO CONTRIBUINTE'].str.slice(0, 6) + '0000' + df_iptu['NUMERO DO CONDOMINIO'].str.slice(0, 2))
df_iptu['sq'] = df_iptu.setor + df_iptu.quadra
df_iptu['sqlc'] = df_iptu.sqlc

df_iptu = df_iptu.join(df_quadras_distritos, on='sq', how='left',  
            allow_duplication=True, inplace=True)

df_sqlc_ac = df_iptu.groupby('sqlc' , agg={'area_contruida_total': vaex.agg.sum('AREA CONSTRUIDA')})
df_iptu = df_iptu.join(df_sqlc_ac, on='sqlc')

gdf_distritos['area'] = gdf_distritos.area
gdf_distritos.to_crs(epsg=4674, inplace=True)

df_iptu.fillna(value='0', column_names=['ds_codigo'], inplace=True)
df_iptu['distrito'] = df_iptu['ds_codigo'].astype('int')
df_iptu.categorize('distrito', inplace=True)

df_iptu_ac_total = df_iptu.groupby(df_iptu.distrito, agg={'Área Construída Total': vaex.agg.sum('area_contruida_total')})

gdf_distritos = gdf_distritos.astype({'ds_codigo': 'int'}).merge(df_iptu_ac_total.to_pandas_df(), left_on='ds_codigo', right_on='distrito')
dist_columns = ['ds_codigo', 'ds_nome', 'Área Construída Total']

app = Dash(__name__)

app.layout = html.Div([
    html.H4('IPTU 2022 - Estatísticas por distrito'),
    html.P("Selecione um atributo"),
    dcc.RadioItems(
        id='atributo', 
        options=["Área Construída", "Valor Venal", "CA", "TO"],
        value="Área Construída",
        inline=True
    ),
    dcc.Graph(id="graph"),

    dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in gdf_distritos[dist_columns].columns],
        data=gdf_distritos[dist_columns].to_dict("records"),
        export_format="csv"
    )

])

# TODO
# Adicionar tabela com opção de exportação
# https://stackoverflow.com/questions/61203436/export-plotly-dash-datatable-output-to-a-csv-by-clicking-download-link

@app.callback(
    Output("graph", "figure"), 
    Input("atributo", "value"))
def display_choropleth(atributo):
    fig = px.choropleth(gdf_distritos,
                   geojson=gdf_distritos.geometry,
                   projection="transverse mercator",
                   color="Área Construída Total",
                   locations=gdf_distritos.index.to_list(),
                   hover_data=["ds_nome", "Área Construída Total"],
                   custom_data=["ds_codigo"])
                  #  color="ds_codigo")
                #    projection="mercator")
    fig.update_geos(fitbounds="locations", visible=False)
    # fig.show()
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    
