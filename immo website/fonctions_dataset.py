

import datetime
import requests
import gzip
import sqlite3
import json
import geopandas
import pandas as pd
import os
import tqdm
import glob



"""
int GetDataSet(void) :

cette fonction récupère automatiquement le dvf des 5 dernières années
et enregistres les fichiers csv dans le dossier dataset


"""
def GetDataSet() :
    try :
        print("récupération des Datasets : en cours\n")
        URL = "https://files.data.gouv.fr/geo-dvf/latest/csv/YEAR/full.csv.gz"
        year = datetime.datetime.today().year
        for i in tqdm.tqdm(range(year - 5, year, 1)) :
            url_year = URL.replace("YEAR",str(i))
            file = requests.get(url_year,allow_redirects=True)
            file = gzip.decompress(file.content)
            open("dataset/"+str(i)+"_dataset.csv",'w').write(file.decode("utf-8"))
        print("récupération des datasets : succès\n")
        return 0
    except Exception as e :
        print(e)
        return -1
 



"""
int Dataset_tosql(str) :

Prend en entrée le chemin + le nom du fichier a importer dans 
la db sqlite et supprime le csv après


"""

def Dataset_tosql(filename) :
    try :
        print("mise à jour de la DB sqlite...\n")
        db = sqlite3.connect("dataset.sqlite")
        df = pd.DataFrame(pd.read_csv(filename,encoding="ISO-8859-1", low_memory=False))
        df.to_sql(name=os.path.basename(filename) , con=db)
        os.remove(filename)
        db.close()
        print("mise à jour : succès\n")
        return 0
    except Exception as e :
        print(e)
        return -1




"""
2Dlist Maj_DB(void) :

fonction principal pour la maj de la DB,
compare l annee précédente car les datas sont mises à jour tout les 6 mois,
si absente de la DB fait une maj complète


"""
def Maj_DB() :
    db_conn = sqlite3.connect("dataset.sqlite")
    db_cursor = db_conn.cursor()
    sql_check_last_year = "SELECT name FROM sqlite_schema WHERE name NOT LIKE 'ix%';"
    tables_db = db_cursor.execute(sql_check_last_year).fetchall()

    bool_in_table = False
    for table in tables_db :
        if str(datetime.datetime.today().year-1) in table[0] :
            bool_in_table = True
    if not bool_in_table :
        if GetDataSet() == 0 :
            liste_csv = glob.glob("dataset/*.csv")
            for i in liste_csv :
                 if Dataset_tosql(i) == -1 :
                    print("échec import "+ str(i))
    return tables_db




"""
geopandas.Dataframe jsongz_to_geojson(str, str) :

récupération automatique du cadastre de la commune désignée grace au code insee (fichier insee non mis a jour car je n'en voit pas l'utilité)


"""
def jsongz_to_geojson(departement, ville):
    # Télécharger le fichier ZIP
    URL = f"https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/DEPARTEMENT/CODE_POSTAL/cadastre-CODE_POSTAL-parcelles.json.gz"



    #transformation code postal en code insee
    df_insee = pd.read_csv("insee_2022.csv")
    insee = df_insee[df_insee['NCCENR'] == ville]['COM']



    URL = URL.replace("DEPARTEMENT",str(int(departement)))
    URL = URL.replace("CODE_POSTAL",str(int(insee)))

    response = requests.get(URL, allow_redirects=True)
    response.raise_for_status()

    decompressed_data = gzip.decompress(response.content)
    data = json.loads(decompressed_data)
    filename = "cadastres/cadastre-CODE_POSTAL-parcelles.geojson".replace("CODE_POSTAL", str(int(insee)))
    with open(filename , 'w') as file:
        json.dump(data, file)
    
    gdf = geopandas.read_file(filename)
    gdf_projected = gdf.to_crs(epsg=2154)
    gdf_projected["area"] = gdf_projected.area

    #delete des fichiers geojson
    liste_geojson = glob.glob("cadastres/*.geojson")
    for i in liste_geojson :
        os.remove(i)

    
    return gdf_projected





