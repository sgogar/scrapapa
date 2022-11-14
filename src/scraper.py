import pandas as pd
from google.cloud import bigquery
import pandas_gbq as pdbq
from bs4 import BeautifulSoup
import requests
import json

urls_dia = ["https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=1",
            "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=2",
            "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=3",
            "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=4"]

urls_vea = ["https://www.vea.com.ar/papas?_q=papas&map=ft",
            "https://www.vea.com.ar/papas?_q=papas&map=ft&page=2"]

urls_disco = ["https://www.disco.com.ar/papas?_q=papas&map=ft",
              "https://www.disco.com.ar/papas?_q=papas&map=ft&page=2",
              "https://www.disco.com.ar/papas?_q=papas&map=ft&page=3"]

def get_matches(url,fuente):
    print(fuente)
    web = url
    productos = []
    response = requests.get(web)
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

def create_table_in_bq(productos) -> None:
    gcp_project = "alumnos-sandbox"
    table_id = "productos_papa.new_table"

    for producto in productos:
      df = pd.DataFrame(
            {
                "nombre": producto['name'],
                "marca": producto['marca'],
                "precio": producto['precio']
            }
        )
    pdbq.to_gbq(df, table_id, project_id=gcp_project, if_exists="append")

def create_dia_table_in_bq(df) -> None:
    gcp_project = "alumnos-sandbox"
    #bq_dataset = "precios_productos"
    table_name = "precios_productos.precios_papa"
    df = pd.DataFrame.from_dict(df)
    pdbq.to_gbq(df, table_name, project_id=gcp_project, if_exists="append")

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
  #dia
  dia_productos = [get_matches(url,"dia") for url in urls_dia]
  #vea
  #vea_productos = [get_matches(url,"vea") for url in urls_vea]
  #disco
  #disco_productos = [get_matches(url,"disco") for url in urls_disco]
  #results
  results = dia_productos #+ disco_productos + vea_productos

  df_productos = pd.concat(results, ignore_index=True)
  df_productos.to_csv("./csvs/productos.csv", index=False)
  df = pd.read_csv('./csvs/productos.csv')
  print(df.sample(5))