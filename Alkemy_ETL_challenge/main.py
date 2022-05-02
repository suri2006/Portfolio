import pandas as pd
import requests 
import csv
import rutas
import os
from datetime import date
from rutas import conn
import psycopg2
import numpy as np
import psycopg2.extras as extras
from ej import carga,crear_tablas

#-------------Extraccion--------------

"""Descargamos los datos"""

salacine=requests.get(rutas.salacine_url)
museo=requests.get(rutas.museo_url)
bib=requests.get(rutas.bib_url)

"""Convertimos todo a csv"""
salacine_csv = csv.reader(
salacine.content.decode('utf-8').splitlines(), 
 delimiter=','
)

museo_csv = csv.reader(
museo.content.decode('utf-8').splitlines(),
 delimiter=','
)

bib_csv = csv.reader(
 bib.content.decode('utf-8').splitlines(),
 delimiter=','
 )

"""Convertimos en dataframes de pandas, para poder manejarlos mejor"""
df_cine = pd.DataFrame(salacine_csv)
df_museo = pd.DataFrame(museo_csv)
df_bib = pd.DataFrame(bib_csv)

"""Colocamos como nombre de columna la primera fila y borramos el duplicado"""
df_cine=df_cine.set_axis(df_cine.iloc[0], axis = 1)
df_cine=df_cine.drop(0 , axis = 0)

df_museo = df_museo.set_axis(df_museo.iloc[0], axis = 1)
df_museo = df_museo.drop(0 , axis = 0)

df_bib = df_bib.set_axis(df_bib.iloc[0], axis = 1)
df_bib = df_bib.drop(0 , axis = 0)

"""Listas para iterar y la fecha de hoy"""
categoria = ["cines" , "museos" , "bibliotecas_populares"]
datos=[df_cine , df_museo , df_bib]
today = date.today()

"""Creamos las carpetas y colocamos los archivos en los mismos"""
for i in range(0,3):
    os.makedirs(
        "data/{i}/{anio}-{mes}".format(
            i = categoria[i] , anio = today.strftime("%Y"), mes = today.strftime("%B")
            ),
         exist_ok=True
         )

    df_bib.to_excel(
        "data/{i}/{anio}-{mes}/{i}-{nombre}.xlsx".format(
        i = categoria[i] , anio = today.strftime("%Y"), mes = today.strftime("%B") , nombre = today.strftime("%d-%m-%Y")
        )
        )

#----------------Procesamiento------------------

""""
Este codigo lo realice para ver las columnas de mis datasets
Notamos que la tabla de MUSEO posee elementos que no tiene mayusculas y acentos

print(datos[0].columns.tolist())
print("********")
print(datos[1].columns.tolist())
print("********")
print(datos[2].columns.tolist())
"""

"""
Creamos las tablas segun el ejercicio
cod_localidad
o id_provincia
o id_departamento
o categoría
o provincia
o localidad
o nombre
o domicilio
o código postal
o número de teléfono
o mail
o web
Renombramos las columnas para que coincidan y creamos la tabla principal
"""

datos[0]=datos[0].rename(columns={"Categoría":"Categoria","Dirección":"Domicilio","Teléfono":"Telefono"})

datos[1]=datos[1].rename(columns={"categoria":"Categoria","provincia":"Provincia",
"localidad":"Localidad","nombre":"Nombre","direccion":"Domicilio","telefono":"Telefono"})

datos[2]=datos[2].rename(columns={"Categoría":"Categoria","Teléfono":"Telefono"})

df_principal=pd.concat(datos , join="inner" , ignore_index=True)

"""
Podemos ver que hay algunas columnas de mas con
print(df_principal.columns.to_list())
Entonces eliminamos las que sobran
"""
df_principal=df_principal.drop(columns=['Latitud', 'Longitud', 'TipoLatitudLongitud'])

""" 
Ahora creamos la otra
Procesar la información de cines para poder crear una tabla que contenga:
o Provincia
o Cantidad de pantallas
o Cantidad de butacas
o Cantidad de espacios INCAA
Podemos ver las columnas con
print(df_cine.columns.to_list())
"""
df_cine_principal=df_cine[["Provincia","Pantallas","Butacas","espacio_INCAA"]]
df_cine_principal=df_cine_principal.rename(columns={"Pantallas":"Cant_pantallas","Butacas":"Cant_butacas","espacio_INCAA":"Cant_espacio_incaa"})

"""Ingresamos los datos de la fecha en los dataframe"""
df_cine_principal["upload_date"]=today.strftime("%Y-%m-%d")
df_principal["upload_date"]=today.strftime("%Y-%m-%d")

#----------------Carga a base de datos------------------
crear_tablas()
carga(conn,df_principal,"principal")
carga(conn,df_cine_principal,"cine_tabla")


