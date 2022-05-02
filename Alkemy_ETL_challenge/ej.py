import psycopg2
import numpy as np
import psycopg2.extras as extras
import pandas as pd
from rutas import conn
  

def carga(conn, df, table):
    """cargar los datos
    
    Arg:
        -conn: conexion psycopg2.connect
        -df: dataframe de pandas
        -table: nombre de la tabla
    
    No retorna nada
    
    """

    tuples = [tuple(x) for x in df.to_numpy()]
  
    cols = ','.join(list(df.columns))
    # SQL query
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("El dataframe {table} fue insertado a la base de datos".format(table=table))
    cursor.close()
  


def crear_tablas():
    """Funcion para crear las tablas"""

    with conn.cursor() as cursor1:
        cursor1.execute(open(f"create_tables.sql", "r").read())
        conn.commit()

        print("Nombre de las tablas: ")
        print("- principal")
        print("- cine_tabla")


if __name__ == "__main__":
    carga()