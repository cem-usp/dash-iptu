# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
# import pandas as pd
import geopandas as gpd

gdf_distritos = gpd.read_file('data/SIRGAS_GPKG_distrito.gpkg')
gdf_distritos['area'] = gdf_distritos.area
gdf_distritos.to_crs(epsg=4674, inplace=True)

# TODO
# Adicionar Vaex DF

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
                   color="area",
                   locations=gdf_distritos.index.to_list(),
                   hover_data=["ds_nome"],
                   custom_data=["ds_codigo"])
                  #  color="ds_codigo")
                #    projection="mercator")
    fig.update_geos(fitbounds="locations", visible=False)
    # fig.show()
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    
