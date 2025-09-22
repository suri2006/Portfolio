import requests
from datetime import date
import re
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from prefect  import task, flow
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

@task
def extraer_urls(xml_string):
    return re.findall(r"<url><loc>(.*?)</url>", xml_string)

@task
def limpiar_url(l_url_input, hoy_str):
    l_xml = l_url_input
    n = len (l_xml)
    l_url_limpia = []
    for i in range(0 , n):
        if hoy_str in l_xml[i]:
            index_borrar = l_xml[i].find('<')
            l_url_limpia.append( l_xml[i][:index_borrar] )
    return l_url_limpia

@task(cache_policy=None)
def obtener_html(driver , url , wait_time=5):
    driver.get(url)

    # Espera para cargar
    time.sleep(wait_time)

    # Extrae el HTML
    html = driver.page_source
    return html

@task
def datos_div_1 (html):
    soup = BeautifulSoup(html, "html.parser")
    titulo = soup.find_all("div",class_ = 'columnaEmpleosFiltros')



    # limpieza de tabulaciones, espacios y saltos de pagina
    texto_div_1 = titulo[0].text
    texto_div_1 = re.sub(r"[\n\r\t\s+]+", " ", texto_div_1)

    # extraccion por titulos
    l_titulos = ['Empresa','Industria','Descripcion','Ubicacion']
    dict_div_1 = {}
    n = len(l_titulos)
    for i in range(0 , n):
        i_inicial = texto_div_1.find(l_titulos[i])
        try:
            i_final = texto_div_1.find(l_titulos[i+1])
            text_aux = texto_div_1[i_inicial : i_final]
            i_aux = text_aux.find(':')
            text = text_aux[i_aux + 1:].strip()
            dict_div_1[l_titulos[i]] = text
        except:
            text_aux = texto_div_1[i_inicial:]
            i_aux = text_aux.find(':')
            text = text_aux[i_aux + 1:].strip()
            dict_div_1[l_titulos[i]] = text
    return dict_div_1

@task
def datos_div_2(html,dict_div_1):
    soup = BeautifulSoup(html, "html.parser")
    titulo = soup.find_all("div",class_ = 'detalleEmpleo')
    texto_div_2 = titulo[0].text

    #stg1 limpieza
    texto_div_2 = texto_div_2.replace('Postularse'," ")
    texto_div_2 = texto_div_2.replace('Agregar a mis postulaciones'," ")
    texto_div_2 = texto_div_2.replace(dict_div_1['Empresa']," ")

    l_texto_div_2 = texto_div_2.splitlines()
    l_texto_div_2 = [item for item in l_texto_div_2 if item.strip() != ""]
    #diccionario
    dict_div_2 = {}
    l_desc = []

    dict_div_2['Puesto'] =  l_texto_div_2[0]
    n = len(l_texto_div_2)

    #extraccion de modalidad y jornada
    for i in range(0 , n):
        leng = len(l_texto_div_2[i])
        if 'Modalidad' in l_texto_div_2[i] and leng <= 30:
            i_aux_m = l_texto_div_2[i].find(':')
            text = l_texto_div_2[i][i_aux_m + 1:].strip()
            dict_div_2['Modalidad'] =  text

        elif 'jornada' in l_texto_div_2[i] and leng <= 30:
            i_aux_j = l_texto_div_2[i].find(':')
            text = l_texto_div_2[i][i_aux_j + 1:].strip()
            dict_div_2['Jornada'] =  text

        elif leng > 100:
            l_desc.append(l_texto_div_2[i])

    v_desc = " ".join(l_desc)
    dict_div_2['Descripcion'] = v_desc
    return dict_div_2

@task
def subir_df_postgresql(df):
    tabla_destino = "DATA_EDUCACIONIT"


    conn = psycopg2.connect(
        dbname = base_datos, user = usuario, password = contraseña,
        host= host , port = puerto
    )
    cursor = conn.cursor()

    # Convertir DataFrame a lista de tuplas
    tuplas = df.to_records(index=False).tolist()
    # Insertar con execute_values
    sql = f"INSERT INTO {tabla_destino} (Portal, Empresa, Modalidad, Puesto, Descripcion, Jornada, URL) VALUES %s"
    print(sql)
    execute_values(cursor, sql, tuplas)

    conn.commit()
    cursor.close()
    conn.close()


@flow(name="Scraping EducacionIT", log_prints=True, retries=2, retry_delay_seconds=10)
def scraping_educacionit_flow():
    eduacionit_pag = 'https://empleos.educacionit.com/sitemap.xml'
    request = requests.get(eduacionit_pag).text
    hoy = date.today()
    hoy_str = hoy.strftime("%Y-%m-%d")

    l_xml = extraer_urls(request)
    l_url_hoy = limpiar_url(l_xml, hoy_str)

    if not l_url_hoy:
        print("No se encontraron URLs para hoy.")
        return
    
    driver = webdriver.Chrome()
    n = len(l_url_hoy)
    l_html = []
    for i in range(0, n):
        html = obtener_html(driver, l_url_hoy[i])
        l_html.append([html , l_url_hoy[i]])
        time.sleep(5)
    driver.quit()

    #Extraer datos de los html
    n = len(l_html)
    l_df = []
    for i in range(0 , n):
        fila = {}
        url = l_html[i][1]
        html = l_html[i][0]
        try:
            dict_div1 = datos_div_1(html)
        except:
            continue
        dict_div2 = datos_div_2(html,dict_div1)
        fila['Portal'] = 'Educacion IT'
        fila['Empresa'] = dict_div1['Empresa']
        fila['Modalidad'] = dict_div2['Modalidad']
        fila['Puesto'] = dict_div2['Puesto']
        fila['Descripcion'] = dict_div2['Descripcion']
        fila['Jornada'] = dict_div2['Jornada']
        fila['URL'] = url
        l_df.append(fila)

    
    df = pd.DataFrame(l_df)
    print(df)
    subir_df_postgresql(df)


if __name__ == "__main__":
    scraping_educacionit_flow()