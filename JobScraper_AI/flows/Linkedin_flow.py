# para mas informacion consultar la documentacion de google: https://developers.google.com/custom-search/v1/overview?hl=es_419
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values
from prefect import task, flow
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
api_key = os.getenv("api_key_google_search")
cse_id = os.getenv("cse_id_google_search")
email = os.getenv("email_linkedin")
password = os.getenv("password_linkedin")




@task
def buscar_google(api_key : str, cse_id: str, query: str) -> list[str]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
    }

    response = requests.get(url, params=params)
    resultados = response.json()
    
    list_resultado = []

    # Mostrar los primeros resultados
    for item in resultados.get("items", []):
        json_resultado = {'Titulo':item["title"], 'URL_Linkedin':item["link"]}
        list_resultado.append(json_resultado)

    return list_resultado

@task
def iniciar_chrome_lnkd(email_input :str , password_input: str):
    driver = webdriver.Chrome()  # Asegurate de tener ChromeDriver instalado y en tu PATH
    driver.get("https://www.linkedin.com/login")

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    email = email_input
    password = password_input

    email_elem = driver.find_element(By.ID,"username")
    email_elem.send_keys(email)

    password_elem = driver.find_element(By.ID,"password")
    password_elem.send_keys(password)
    password_elem.submit()

    time.sleep(5)
    return driver

@task(cache_policy=None)
def f_scrap_lkdn(driver: webdriver , html_input : str):
    driver.get(html_input)
    time.sleep(5)
    html = driver.page_source
    time.sleep(2)
    return html

@task
def f_html_lkdn_parser(html_input:str):
    dict_lnkd = {}

    soup = BeautifulSoup(html_input, "html.parser")
    clasificaciones = soup.find_all("div",class_ = 'job-details-fit-level-preferences')
    clasificaciones = clasificaciones[0].text

    titulo = soup.find_all("div",class_ = 't-24 job-details-jobs-unified-top-card__job-title')
    titulo = titulo[0].text.strip()

    empresa = soup.find_all("div",class_ = 'job-details-jobs-unified-top-card__company-name')
    empresa = empresa[0].text.strip()

    descripcion = soup.find_all("div", id = 'job-details')
    descripcion = descripcion[0].text

    v_modalidad = ''
    l_modalidad = ['En remoto', 'Presencial', 'Hibrido']
    for item in l_modalidad:
        if item in clasificaciones:
            v_modalidad = item

    v_jornada = ''
    l_jornada = ['Jornada completa','Media jornada','Contrato por obra','Temporal','Voluntario']
    for item in l_jornada:
        if item in clasificaciones:
            v_jornada = item

    dict_lnkd['Portal'] = 'Linkedin Jobs'
    dict_lnkd['Puesto'] = titulo
    dict_lnkd['Modalidad'] = v_modalidad
    dict_lnkd['Empresa'] = empresa
    dict_lnkd['Descripcion'] = descripcion
    dict_lnkd['Jornada'] = v_jornada
    return dict_lnkd

@task
def subir_df_postgresql(df):
    tabla_destino = "DATA_LINKEDIN_JOBS"


    conn = psycopg2.connect(
        dbname = base_datos, user = usuario, password = contraseña,
        host= host , port = puerto
    )
    cursor = conn.cursor()

    # Convertir DataFrame a lista de tuplas
    tuplas = df.to_records(index=False).tolist()
    # Insertar con execute_values
    sql = f"INSERT INTO {tabla_destino} (Portal, Puesto, Modalidad, Empresa, Descripcion, Jornada, URL) VALUES %s"
    print(sql)
    execute_values(cursor, sql, tuplas)

    conn.commit()
    cursor.close()
    conn.close()



#----
@flow(name="Scraping Linkedin jobs", retries=2, retry_delay_seconds=10, log_prints=True)
def linkedin_scarping_flow ():

    ayer = datetime.now() - timedelta(days=1)

    fecha_ayer = ayer.strftime("%Y-%m-%d")
    # se puede cambiar la palabra "data", por fullstack, ciberseguridad, frontend, backend etc, segun se desee

    query = f'argentina data inurl:linkedin.com/jobs/view after:{fecha_ayer}'


    l_google_resultados = buscar_google(api_key, cse_id, query)


    driver = iniciar_chrome_lnkd(email, password)


    #tomaremos solo 5 links para scrapear, si quieres scrapear 10, solo comenta el el siguiente paso
    #pero es para evitar el bloqueo de la ip
    l_google_resultados = l_google_resultados[:5]
    n = len (l_google_resultados)
    l_df = []

    for i in range(0, n):
        html = l_google_resultados[i]['URL_Linkedin']
        html_pag = f_scrap_lkdn(driver , html)
        fila = f_html_lkdn_parser(html_pag)
        fila['URL'] = html
        l_df.append(fila)
    
    driver.quit()
    df = pd.DataFrame(l_df)
    print(df)
    subir_df_postgresql(df)


if __name__ == "__main__":
    linkedin_scarping_flow()
