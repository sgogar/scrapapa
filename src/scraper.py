import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq as pdbq
from bs4 import BeautifulSoup
import requests
import json
import time

key_path = "./../alumnos-sandbox-50f796a33b0b.json"
project_id = "alumnos-sandbox"
table_id = 'precios_productos.grupo_1_papa'
credentials = service_account.Credentials.from_service_account_file(key_path)

urls_dia = ["https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=1",
            "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=2",
            "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=3",
            "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=4"]

urls_vea = ["https://www.vea.com.ar/papas?_q=papas&map=ft",
            "https://www.vea.com.ar/papas?_q=papas&map=ft&page=2"]

urls_disco = ["https://www.disco.com.ar/papas?_q=papas&map=ft",
              "https://www.disco.com.ar/papas?_q=papas&map=ft&page=2",
              "https://www.disco.com.ar/papas?_q=papas&map=ft&page=3"]

def get_matches(web,fuente):
    print(fuente)
    print(web)
    productos = []
    response = requests.get(web)
    time.sleep(3)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    items = json.loads(soup.find_all('script', type='application/ld+json')[1].text)['itemListElement']

    for item in items:
      nombre = item["item"]["name"]
      marca = item["item"]["brand"]["name"]
      precio = item["item"]["offers"]["offers"][0]["price"]
      sku = item["item"]["sku"]
      producto = {'nombre': nombre,'marca': marca,'precio': precio,'sku': sku}
      productos.append(producto)

    df_productos = pd.DataFrame(productos)
    df_productos['fuente'] = fuente
    return df_productos

def create_csv() -> None:
    #dia
    dia_productos = [get_matches(url,"dia") for url in urls_dia]
    #vea
    vea_productos = [get_matches(url,"vea") for url in urls_vea]
    #disco
    #disco_productos = [get_matches(url,"disco") for url in urls_disco]
    results = dia_productos + vea_productos #+ disco_productos
    df_productos = pd.concat(results, ignore_index=True)
    df_productos.to_csv("./../csvs/productos.csv", index=False)
    

def create_table_in_bq(df) -> None:
    pdbq.to_gbq(df, table_id, project_id=project_id, credentials=credentials, if_exists="append")

def get_all_bq() -> None:
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    sql_query = f"""
        SELECT *
        FROM `{project_id}.{table_id}`
        LIMIT 1000
        """

    query = client.query(sql_query)
    results = query.result()
    result_df = results.to_dataframe()
    print(result_df)

def print_get_all_bquery() -> None:
    gcp_project = "alumnos-sandbox"
    bq_dataset = "precios_productos"
    table_name = "precios_papa"

    client = bigquery.Client(project=gcp_project)
    dataset_ref = client.dataset(bq_dataset)

    sql_query = f"""
                    SELECT *
                    FROM `{bq_dataset}.{table_name}`
                    LIMIT 20
                 """

    query = client.query(sql_query)
    results = query.result()
    result_df = results.to_dataframe()
    print(result_df)

if __name__ == '__main__':
    #creo csv
    #create_csv()

    #leo csv
    #df_productos = pd.read_csv('./../csvs/productos.csv')

    #creo tabla en bq
    #create_table_in_bq(df_productos)

    #leo tabla de bq
    get_all_bq()
