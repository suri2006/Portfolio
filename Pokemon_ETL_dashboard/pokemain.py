import requests
import json
from pprint import pprint
import pandas as pd
from sqlalchemy import create_engine

#Obtenemos el json (con limit vamos a tomar dicha cantidad  de datos de pokemons y con offset es el lugar desde que se toman los datos)
url="https://pokeapi.co/api/v2/pokemon/?offset=0&limit=300"
request_poke=requests.get(url)
request_poke_json=json.loads(request_poke.text)
#pprint(request_poke_json["results"][0]["url"])
#pprint(request_poke_json)

#Creamos una lista para guardar diccionarios de pokemons
pokemon_list=[]
stats_list=[]
imag_list=[]
contador=0


#Guardamos los datos
for i in request_poke_json["results"]:
    url_pokemon = i["url"]
    request_poke2 = requests.get(url_pokemon)
    request_poke2_json = json.loads(request_poke2.text)

    #El peso se encuentra en hectogramos se divide por 10 para pasar a kg
    #La altura se encuentra en decimetros se divide por 10 para pasar a metros
    nombre = request_poke2_json["name"]
    url_imagen = request_poke2_json["sprites"]["other"]["official-artwork"]["front_default"]
    peso = request_poke2_json["weight"]/10
    altura = request_poke2_json["height"]/10

    #Para obtener descripcion, habitat , legendario o mitico
    url_descripcion=request_poke2_json["species"]["url"]
    request_descripcion=requests.get(url_descripcion)
    request_descripcion_json=json.loads(request_descripcion.text)
    habitat=request_descripcion_json["habitat"]["name"]
    es_legendario=request_descripcion_json["is_legendary"]
    es_mitico=request_descripcion_json["is_mythical"]
    generacion=request_descripcion_json["generation"]["name"]

    #Obtener una descripcion en ingles de las muchas descripciones que hay
    for i in request_descripcion_json["flavor_text_entries"]:
        if i["language"]["name"]=="en":
            descripcion=str(i["flavor_text"]).replace("\n"," ")
            break

    #Test para mitico y legendario
    test = lambda a : "Yes" if a==True else "No"

    tipo_pokemon=""
    for i in request_poke2_json["types"]:
        tamaño=len(request_poke2_json["types"])
        if i != request_poke2_json["types"][tamaño-1]:
            tipo_pokemon+=i["type"]["name"]+","
        else:
            tipo_pokemon+=i["type"]["name"]

    habilidades=""
    for i in request_poke2_json["abilities"]:
        tamaño=len(request_poke2_json["abilities"])
        if i != request_poke2_json["abilities"][tamaño-1]:
            habilidades+=i["ability"]["name"]+","
        else:
            habilidades+=i["ability"]["name"] 

    movimientos=""
    for i in request_poke2_json["moves"]:
        tamaño=len(request_poke2_json["moves"])
        if i != request_poke2_json["moves"][tamaño-1]:
            movimientos+=i["move"]["name"]+","
        else:
            movimientos+=i["move"]["name"]
    contador+=1

    diccionario={"Id":contador,"Nombre":nombre,"Tipo_pokemon":tipo_pokemon,
    "Imagen_id":f"i{contador}","Peso(kg)":peso,"Habilidades":habilidades,
    "Movimientos_Compatibles":movimientos,"Stats_id":f"s{contador}",
    "Altura(m)":altura,"Habitat":habitat,"Es_legendario":test(es_legendario),
    "Es_mitico":test(es_mitico),"Generacion":str(generacion),"Descripcion":descripcion,}

    pokemon_list.append(diccionario)
    
    stats_dic={"Stats_id":f"s{contador}"}
    for j in request_poke2_json["stats"]:
        stats_dic[j['stat']['name']] = j['base_stat']

    stats_list.append(stats_dic)
    stats_dic={}

    imag_list.append({"Image_id":f"i{contador}","Url":url_imagen})



#------ Convirtiendo en dataframes--------
df_principal = pd.DataFrame(pokemon_list)
#Colocando mayusculas
df_principal["Tipo_pokemon"] = df_principal["Tipo_pokemon"].str.capitalize() 
df_principal["Nombre"] = df_principal["Nombre"].str.capitalize() 
df_principal["Habilidades"] = df_principal["Habilidades"].str.capitalize() 
df_principal["Movimientos_Compatibles"] = df_principal["Movimientos_Compatibles"].str.capitalize() 

df_stats=pd.DataFrame(stats_list)
df_imag=pd.DataFrame(imag_list)


#------------Exportando a una base de datos en mysql----------
#Configurando la conexion de nuestra base de datos mysql
usuario="root"
contraseña="1234"
host="localhost"
port="3306"
database="pokedb"
conexion=create_engine(f'mysql+pymysql://{usuario}:{contraseña}@{host}:{port}/{database}')

#Enviando a mysql
df_principal.to_sql(con=conexion,name="principal",if_exists="append",index=False)
df_imag.to_sql(con=conexion,name="dim_imag",if_exists="append",index=False)
df_stats.to_sql(con=conexion,name="dim_stats",if_exists="append",index=False)



#-----------CODIGO USADO PARA VER LA INFORMACIÓN (PARA EXPERIMENTAR)--------------
"""

url_pokemon=request_poke_json["results"][2]["url"]
request_poke2=requests.get(url_pokemon)
request_poke2_json=json.loads(request_poke2.text)
print(request_poke2_json["name"])

new_url=request_poke2_json["species"]["url"]
#new_url=f"https://pokeapi.co/api/v2/pokedex/{idd}"

request_poke2=requests.get(new_url)
request_poke2_json=json.loads(request_poke2.text)
#pprint(request_poke2_json.keys())
#pprint(request_poke2_json["flavor_text_entries"][0].keys())
#print(request_poke2_json["flavor_text_entries"][0])

for i in request_poke2_json["flavor_text_entries"]:
    if i["language"]["name"]=="en":
        print(i["flavor_text"])
        break

"""





#pprint(request_poke2_json.keys())
#LISTO DESCRIPCION print(str(request_poke2_json["flavor_text_entries"][0]["flavor_text"]).replace("\n"," "))







#dict_keys(['abilities', 'base_experience', 'forms', 'game_indices', 'height', 'held_items', 'id', 'is_default',
#'location_area_encounters', 'moves', 'name', 'order', 'past_types', 'species', 'sprites', 'stats', 'types', 'weight'])

#LISTO NOMBRE
#print(request_poke2_json["name"])


# LISTO imagenes 
#pprint(request_poke2_json["sprites"]["other"]["official-artwork"]["front_default"])

#LISTO FOR PARA EL TIPO DE POKEMON
#print(request_poke2_json["types"])
#for i in request_poke2_json["types"]:
#    print(i["type"]["name"])

#LISTO HABILDADES
#print(request_poke2_json["abilities"])
#for i in request_poke2_json["abilities"]:
#    print(i["ability"]["name"])

#LISTO MOVIMIENTOS QUE PUEDE HACER
#pprint(request_poke2_json["moves"][0]["move"]["name"])
#for i in request_poke2_json["moves"]:
#    print(i["move"]["name"])

#LISTO LOCACION DE ENCUENTROS
#pprint(request_poke2_json['stats'])
#for i in request_poke2_json['stats']:
#    print(f"base {i['base_stat']}\n{i['stat']['name']}\n\n\n")

##ALTURA EN DECIMETROS HAY QUE PASARLO A METROS dividiento por 10 al igual que weight en hectogramos pasarlo a kg
#pprint(request_poke2_json["height"]/10)
