from bs4 import BeautifulSoup
import requests
import json
from google.cloud import bigquery
import pandas as pd
import pandas_gbq as pdbq

def product_getter_dia(urls,fuente):
  productos = []
  for url in urls:
    result = requests.get(url)
    content = result.text
    soup = BeautifulSoup(content, 'lxml')
    data = json.loads(soup.findAll('script', type='application/ld+json')[1].text)
    items = data['itemListElement']
    
  
    for item in items:
      producto = {}
      item_nombre = item["item"]["name"]
      item_marca = item["item"]["brand"]["name"]
      item_precio = item["item"]["offers"]["offers"][0]["price"]
      item_sku = item["item"]["sku"]
      producto["nombre"] = item_nombre
      producto["marca"] = item_marca
      producto["precio"] = item_precio
      producto["sku"] = item_sku
      producto["fuente"] = fuente
  return productos

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
  urls_dia = ["https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=1",
       "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=2",
       "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=3",
       "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=4"]

  #urls_vea = ["https://www.vea.com.ar/papas?_q=papas&map=ft",
  #     "https://www.vea.com.ar/papas?_q=papas&map=ft&page=2"]

  #urls_disco = ["https://www.disco.com.ar/papas?_q=papas&map=ft",
  #            "https://www.disco.com.ar/papas?_q=papas&map=ft&page=2",
  #            "https://www.disco.com.ar/papas?_q=papas&map=ft&page=3"]

  #json_dia = product_getter_dia(urls_dia,"dia")
  #create_dia_table_in_bq(json_dia)
  #json_vea = product_getter(urls_vea)
  #json_vea = product_getter(urls_disco)
  
  #productos = product_getter(urls_dia)
  
  # add_data_to_bigquery_and_print_df()
  #create_table_in_bq(productos)

  #create_table_in_bq(json_dia)
  #print(json_dia)
  print_get_all_bquery()