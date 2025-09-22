from telethon import TelegramClient
from datetime import datetime, timezone, time
import time as tp
import re
from google import genai
import requests
from bs4 import BeautifulSoup
import ast
import pandas as pd
from prefect import task,flow
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Acceder a las claves
usuario = os.getenv("usuario_postgres")
contraseña = os.getenv("contrasenia_postgres")
host = os.getenv("host_postgres")
puerto = os.getenv("puero_postgres")
base_datos = os.getenv("base_datos_postgres")
api_id = os.getenv("api_id_telegram")
api_hash = os.getenv("api_hash_telegram")
api_key = os.getenv("api_key_google_search")



@task
async def mensajes_discord(api_id : int, api_hash : str, hoy_4am_utc : datetime) -> list[str]:
    l_messages = []

    async with TelegramClient('mi_sesion', api_id, api_hash) as client:
        channel = await client.get_entity('@LaburoArgento')

        async for message in client.iter_messages(channel, limit=15,reverse=False):
            if message.date > hoy_4am_utc:
                #print(message.text)
                l_messages.append(message.text)
    return l_messages

@task
def extraer_links(lista_mensajes: list) -> list[str]:
    # Patrón para detectar URLs comunes (http, https, www)
    texto = "\n".join(lista_mensajes)
    patron = r'https://[^\s]+'
    links = re.findall(patron, texto)
    return links


@task(cache_policy=None)
def gemini_analisis(string : str, client : genai.Client) -> str:
    query = "Encuentra el nombre del puesto, empresa y modalidad remota, hibrida o presencial, y colocalos en este formato ['puesto','empresa','modalidad'], del siguiente texto " + string
    response = client.models.generate_content(
    model="gemini-2.5-flash", contents=query
    )
    return response.text


@task
def get_link_preview(url : str) -> dict:
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    def get_meta(property_name):
        tag = soup.find('meta', property=property_name) or soup.find('meta', attrs={'name': property_name})
        return tag['content'] if tag and 'content' in tag.attrs else None

    preview = {
        'title': get_meta('og:title') or soup.title.string if soup.title else None,
        'description': get_meta('og:description') or get_meta('description'),
        'image': get_meta('og:image') or get_meta('twitter:image')
    }

    return preview

@task
def subir_df_postgresql(df):
    tabla_destino = "DATA_TELEGRAM"


    conn = psycopg2.connect(
        dbname = base_datos, user = usuario, password = contraseña,
        host= host , port = puerto
    )
    cursor = conn.cursor()

    # Convertir DataFrame a lista de tuplas
    tuplas = df.to_records(index=False).tolist()
    # Insertar con execute_values
    sql = f"INSERT INTO {tabla_destino} (Portal, Puesto, Empresa, Modalidad, Descripcion, URL) VALUES %s"
    print(sql)
    execute_values(cursor, sql, tuplas)

    conn.commit()
    cursor.close()
    conn.close()



@flow(name="Scraping Telegram", retries=2, retry_delay_seconds=10, log_prints=True)
async def scraping_telegram_flow():
    hoy_4am_utc = datetime.combine(datetime.today(), time(4, 0)).replace(tzinfo=timezone.utc)
    
    l_mensajes = await mensajes_discord(api_id , api_hash , hoy_4am_utc)
    links = extraer_links(l_mensajes)
    client = genai.Client(api_key = api_key)

    n = len(links)
    l_df = []
    for i in range(0, n):
        url = links[i]
        fila = {}
        try:
            metadata = get_link_preview(url)
            l_gemini = gemini_analisis(metadata['description'] , client)
            l_gemini = ast.literal_eval(l_gemini)
            fila['Portal'] = 'Telegram Grupo LaburoArgento'
            fila['Puesto'] = l_gemini[0]
            fila['Empresa'] = l_gemini[1]
            fila['Modalidad'] = l_gemini[2]
            fila['Descripcion'] = metadata['description']
            fila['URL'] = url
            l_df.append(fila)

        except:
            print('sin metadata/cloudflare  ', url)

    df = pd.DataFrame(l_df)
    if not df.empty:
        subir_df_postgresql(df)
        print(df)
    else:
        print('!!! No hay dataframe, seguramente no hay publicaciones de hoy !!!')

if __name__ == "__main__":
    import asyncio
    asyncio.run(scraping_telegram_flow())


