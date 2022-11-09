from bs4 import BeautifulSoup
import requests
import json
from google.cloud import bigquery

def product_getter(urls):
  for url in urls:
    result = requests.get(url)
    content = result.text
    soup = BeautifulSoup(content, 'lxml')
    data = json.loads(soup.findAll('script', type='application/ld+json')[1].text)
    items = data['itemListElement']
    productos = []
  
    for item in items:
      producto = {}
      item_nombre = item["item"]["name"]
      item_marca = item["item"]["brand"]["name"]
      item_precio = item["item"]["offers"]["offers"][0]["price"]
      producto["name"] = item_nombre
      producto["marca"] = item_marca
      producto["precio"] = item_precio
      productos.append(producto)
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



if __name__ == '__main__':
  urls_dia = ["https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=1",
       "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=2",
       "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=3",
       "https://diaonline.supermercadosdia.com.ar/papas?_q=papas&map=ft&page=4"]

  print(product_getter(urls_dia))

  #urls_vea = ["https://www.vea.com.ar/papas?_q=papas&map=ft",
  #     "https://www.vea.com.ar/papas?_q=papas&map=ft&page=2"]

  #print(product_getter(urls_vea))

  #urls_disco = ["https://www.disco.com.ar/papas?_q=papas&map=ft",
  #            "https://www.disco.com.ar/papas?_q=papas&map=ft&page=2",
  #            "https://www.disco.com.ar/papas?_q=papas&map=ft&page=3"]

  #print(product_getter(urls_disco))
  
  productos = product_getter(urls_dia)
  
  # add_data_to_bigquery_and_print_df()
  create_table_in_bq(productos)