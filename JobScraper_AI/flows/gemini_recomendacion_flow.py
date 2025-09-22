import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import date
from google import genai
from telethon import TelegramClient
import asyncio
from prefect import task, flow
import pdfplumber

hoy_str = date.today().strftime("%Y%m%d")

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Acceder a las claves
usuario = os.getenv("usuario_postgres")
contraseña = os.getenv("contrasenia_postgres")
host = os.getenv("host_postgres")
puerto = os.getenv("puero_postgres")
base_datos = os.getenv("base_datos_postgres")
api_key = os.getenv("api_key_google_search")
api_id = os.getenv("api_id_telegram")
api_hash = os.getenv("api_hash_telegram")
id_grupo = os.getenv("id_grupo_telegram")

@task
def leer_tabla_postgresql():
    conn = psycopg2.connect(
        dbname=base_datos,
        user=usuario,
        password=contraseña,
        host=host,
        port=puerto
    )
    query = f"SELECT Puesto, Descripcion, Modalidad, URL FROM public.ofertas_laborales where fecha_subida={hoy_str}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@task
def texto_cv():
    pdf_path =  Path(__file__).resolve().parent.parent / 'Curriculum'

    archivos = [f.name for f in pdf_path.iterdir() if f.is_file()]
    nombre_pdf = archivos[0]

    with pdfplumber.open(f'{pdf_path}/{nombre_pdf}') as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    return texto


@task
def generar_recomendaciones(df: pd.DataFrame):
    cv = texto_cv()
    client = genai.Client(api_key=api_key)

    filas = df.to_dict(orient="records")
    texto_tabla = "\n".join([
        f"{f['puesto']} | {f['descripcion']} | {f['modalidad']} | {f['url']}"
        for f in filas
    ])

    prompt = f"""
    Tengo esta tabla de ofertas laborales:

    {texto_tabla}

    Recomendame los 3 trabajos más interesantes para alguien con perfil, usa mi curriculum para recomendarme trabajos:
     
    {cv}

    Priorizando modalidad remota y claridad en la descripción. Devuelve el resultado en formato: Puesto, Empresa (si se puede inferir), Modalidad, URL.
    Escribe el texto para enviarlo mensaje a mi mismo
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

@task
async def enviar_mensaje_grupo(texto: str):
    client = TelegramClient('mi_sesion', api_id, api_hash)
    await client.start()
    entidad = await client.get_entity(id_grupo)  # puede ser '@nombre_grupo' o ID
    await client.send_message(entidad, texto)
    await client.disconnect()



@flow(name="Recomendaciones Gemini + Telegram", retries=2, retry_delay_seconds=10, log_prints=True)
async def flow_recomendaciones_telegram():
    df = leer_tabla_postgresql()
    if df.empty:
        print(" No se encontraron ofertas para hoy.")
        return
    recomendaciones = generar_recomendaciones(df)
    await enviar_mensaje_grupo(recomendaciones)



if __name__ == "__main__":
    asyncio.run(flow_recomendaciones_telegram())
