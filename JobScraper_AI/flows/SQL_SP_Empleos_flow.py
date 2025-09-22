
import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path
from prefect import task, flow

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Acceder a las claves
usuario = os.getenv("usuario_postgres")
contraseña = os.getenv("contrasenia_postgres")
host = os.getenv("host_postgres")
puerto = os.getenv("puero_postgres")
base_datos = os.getenv("base_datos_postgres")

@task
def call_stored_procedure():
    try:
        conn = psycopg2.connect(
            dbname = base_datos, user = usuario, password = contraseña,
            host= host , port = puerto
        )
        cursor = conn.cursor()
        sql = "CALL public.STG_TABLA_EMPLEOS();"
        cursor.execute(sql)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'Error al ejecutar procedimiento: {str(e)}')


@flow(name="POSTGRESQL - SP_CARGA_TABLA")
def flujo_etl():
    call_stored_procedure()

if __name__ == "__main__":
    flujo_etl()
