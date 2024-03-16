import pandas as pd
import sqlite3
import folium
from fonctions_dataset import *
import sys


"""
int GetFoliumMap(str)

crée la map intégrant le gvf et le cadastre dans le dossier templates

"""
def GetFoliumMap(city_name : str):
    from folium.plugins import marker_cluster
    #check si folder cadastres et dataset existe
    try :
        os.makedirs("dataset")
    except FileExistsError :
        pass
    try :
        os.makedirs("cadastres")
    except FileExistsError :
        pass

    Maj_DB()

    #recuperation des tables dans la db et les fusionnes
    db_conn = sqlite3.connect("dataset.sqlite")
    db_cursor = db_conn.cursor()
    sql_check_last_year = "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'ix%';"
    tables_db = db_cursor.execute(sql_check_last_year).fetchall()
    table_df = []

    for file in tables_db:
        try:
            sql_command_getville = "SELECT * FROM '"+file[0]+"' WHERE nom_commune = ?"

            df = pd.read_sql_query(sql_command_getville, db_conn, params=(city_name,))
            table_df.append(df)
        except KeyError as e:
            break
    df = table_df[0].copy()
    df = df._append(table_df[1:])

    # creation de la map
    map = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)

    # ajout du cadastre de la commune
    data_cadastre_parcelles = jsongz_to_geojson(df.iloc[1]['code_departement'], city_name)
    folium.GeoJson(data_cadastre_parcelles).add_to(map)

    # Groupe les données par latitude et longitude
    grouped = df.groupby(['latitude', 'longitude'])

    # transforme le tableau en tableau html pour une intégration plus simple et ajoute les markers
    cluster = marker_cluster.MarkerCluster()
    for (lat, lon), group in grouped:
        folium.Marker([lat, lon], popup=group[['valeur_fonciere', 'date_mutation', 'adresse_numero', 'surface_reelle_bati']].to_html()).add_to(cluster)

    cluster.add_to(map)

    map.save("templates/map.html")
    return 0


if __name__ == "__main__":
    a = sys.argv[1]
    GetFoliumMap(a)
