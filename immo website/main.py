import pandas as pd
import sqlite3
import folium
from fonctions_dataset import *

if __name__ == "__main__":

    #check si folder cadastres et dataset existe
    # a faire
    

    Maj_DB()

    str_ville = input("entrer le nom de la ville :")

    #recuperation des tables dans la db et les fusionnes
    db_conn = sqlite3.connect("dataset.sqlite")
    db_cursor = db_conn.cursor()
    sql_check_last_year = "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'ix%';"
    tables_db = db_cursor.execute(sql_check_last_year).fetchall()
    table_df = []

    for file in tables_db :
        try :
            sql_command_getville = "SELECT * FROM '"+file[0]+"' WHERE nom_commune = ?"

            df = pd.read_sql_query(sql_command_getville, db_conn, params=(str_ville,))
            table_df.append(df)
        except KeyError as e:
            break
    df = table_df[0].copy()
    df = df._append(table_df[1:])

    #creation de la map
    map = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)

    #ajout du cadastre de la commune
    data_cadastre_parcelles = jsongz_to_geojson(df.iloc[1]['code_departement'], str_ville)
    folium.GeoJson(data_cadastre_parcelles).add_to(map)


    # Groupe les données par latitude et longitude
    grouped = df.groupby(['latitude', 'longitude'])

    #transforme le tableau en tableau html pour une intégration plus simple et ajoute les markers
    for (lat, lon), group in grouped:
        folium.Marker([lat, lon],popup=group[['valeur_fonciere','date_mutation','adresse_numero','surface_reelle_bati']].to_html()).add_to(map)

    map.save("map.html")
