import pymupdf  # PyMuPDF
import pandas as pd
import re

# TODOS LOS PARAMETROS xo,yo,x1,y1 se obtuvieron de la app de tabula, para separar las hojas de pdf en secciones


def tabla_datos_num(pdf_nombre, pag):
    """
    Extrae texto de la zona donde se encuentros los numeros y el campo de la region

    Parámetros:
    - pdf_nombre (str): nombre o ruta del archivo PDF
    - pag (int): número de página (0-indexed)

    Retorna:
    - Lista de elementos con [bbox, texto_linea]
    """
    # Abrir el documento y seleccionar la página
    doc = pymupdf.open(pdf_nombre)
    page = doc[pag]

    # Coordenadas del rectángulo de extracción
    x0 = 149.865625
    x1 = 588.678125
    y0 = 102.265625
    y1 = 776.103125
    rect = pymupdf.Rect(x0, y0, x1, y1)

    # Obtener el texto como diccionario
    data = page.get_text("dict", clip=rect)

    # Extraer líneas con su posición
    l_items = []

    for block in data['blocks']:
    #print('--')
        if block['type']  == 0: #solo texto
        #print(block['lines'])
            for lines in block['lines']:
                x0_n = lines['bbox'][0]
                y0_n = lines['bbox'][1]
                x1_n = lines['bbox'][2]
                y1_n = lines['bbox'][3]


                texto_linea = [span["text"] for span in lines["spans"]]
                bbox = [x0_n, y0_n, x1_n, y1_n]
                #print(bbox,y0_nn)
                l_items.append([bbox , texto_linea ])
    
    return l_items

#------- funciones para limpiar texto ------------------
def f_texto_min (lista):
    for texto in lista:
        if len(texto) <= 2:
            return True
        else:
            return False

def f_tiene_num(lista):
    for item in lista:
        flag = bool(re.search(r'\d', item))
        if flag:
            return True
    return False

def f_no_tiene_moneda(lista):
    for item in lista:
        if "$" not in item:
            return True
    return False

def f_en_region (lista):
    for item in lista:
        flag = bool( item in ['Buenos Aires', 'Cuyo', 'Litoral-Centro',  'NEA',  'NOA',  'Patagonia'])
        if flag:
            return True
    return False

#-------------------------------


def filtrar_items(l_items):
    """
    Filtra elementos de l_items según condiciones

    Parámetros:
    - l_items: lista de elementos, donde cada elemento es una lista [bbox, texto]

    Retorna:
    - l_items_1: lista filtrada que cumple con las condiciones
    """
    n = len(l_items)
    l_items_1 = []
    for i in range(0 , n):
        item = l_items[i][1]
        #print(item)
        if not (f_texto_min(item) or (f_tiene_num(item) and f_no_tiene_moneda(item) ) or ( not f_en_region(item) and not f_tiene_num(item)  ) ):
            l_items_1.append(l_items[i])
           
    return l_items_1


# ordenamiento de burbuja, para ordenar segun la posicion y0 (ordenamiento vertical) [paso a insertar en un script limpio]
def f_bubble_sort(lista):
    """
    ordenamiento de burbuja, para ordenar segun la posicion y0
    
    Parámetros:
    - l_items: lista de elementos, donde cada elemento es una lista [bbox, texto]

    Retorna:
    - lista: lista ordenada segun y0 de menor a mayor
    """
    n = len(lista)
    for i in range(0,n):
        for j in range(0, n - i - 1):
            if lista[j][0][1] > lista[j + 1][0][1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista


def datos_a_fila(l_items):
    """
    Agrupa elementos de l_items en filas basadas en la cercanía vertical (coordenada Y).
    Si la diferencia entre Y de dos elementos consecutivos es menor o igual a 2, se consideran parte de la misma fila.

    Parámetros:
    - l_items: lista de elementos, donde cada uno tiene estructura [[x, y], [texto]]

    Retorna:
    - l_df_datos: lista de filas agrupadas, cada una con su Y de referencia y los textos asociados
    ejemplo:
    [[122.38488006591797], ['Buenos Aires', 'Cuyo', 'Litoral-Centro', 'NEA', 'NOA', 'Patagonia']]
    [[140.83270263671875], ['$2.678.940', '$2.277.099', '$2.411.046', '$2.411.046', '$2.143.152', '$3.214.728']]
    [[155.32876586914062], ['$3.110.184', '$2.643.656', '$2.799.166', '$2.799.166', '$2.488.147', '$3.732.221']]
    ...
    ...
    """
    n = len(l_items)
    l_fila = []
    l_df_datos = []

    for i in range(0,n):
        try:
            if abs(l_items[i][0][1] - l_items[i+1][0][1]) <= 2:
                l_fila.append(l_items[i][1][0])
            else:
                l_fila.append(l_items[i][1][0])
                l_df_yi = [l_items[i][0][1]]
                l_fila = [l_df_yi , l_fila]
                l_df_datos.append(l_fila)
                l_fila = []
        except:
            l_fila.append(l_items[n-1][1][0])

            l_df_yi = [l_items[i][0][1]]
            l_fila = [l_df_yi , l_fila]

            l_df_datos.append(l_fila)
    return l_df_datos


def datos_a_tabla (l_df_datos):
    """
    Separa l_df_datos en múltiples tablas usando como referencia los índices
    donde no hay números (entonces es encabezado).

    Parámetros:
    - l_df_datos: lista de filas, cada una con estructura [y, [texto1, texto2, ...]]

    Retorna:
    - l_df_datos_tables: lista de tablas separadas
    """
    n = len(l_df_datos)
    l_index_headers =[]

    for i in range(0 , n):
        if not f_tiene_num(l_df_datos[i][1]):
            l_index_headers.append(i)

    n = len(l_index_headers)
    l_df_datos_tables = []

    for i in range(0 , n):
        try:
            table = l_df_datos[ l_index_headers[i] : l_index_headers[i+1] ]
            l_df_datos_tables.append(table)
        except:
            table = l_df_datos[ l_index_headers[i] : ]
            l_df_datos_tables.append(table)  

    return l_df_datos_tables

def encabezados_datos(pdf_nombre, pag):
    """
    Extrae líneas de texto desde una zona específica de una página PDF,
    excluyendo aquellas que contienen la palabra 'zona' y las que no son numeros ni regiones.

    Parámetros:
    - pdf_nombre: nombre o ruta del archivo PDF
    - pag: número de página 

    Retorna:
    - l_item_h: lista de elementos con [bbox, texto_linea]
    """

    doc = pymupdf.open(pdf_nombre)
    page = doc[pag]


    x1=36.44375
    x2=159.1625
    y1=97.059375
    y2=772.384375

    rect = pymupdf.Rect(x1, y1, x2, y2)
    data = page.get_text("dict", clip=rect)

    l_item_h = []

    # Extraer líneas con su posición vertical
    for block in data['blocks']:
        #print('--')
        if block['type']  == 0: #solo texto
            #print(block['lines'])
            for lines in block['lines']:
                x0_n = lines['bbox'][0]
                y0_n = lines['bbox'][1]
                x1_n = lines['bbox'][2]
                y1_n = lines['bbox'][3]

                texto_linea = [span["text"] for span in lines["spans"]]
                #print(y0_n,texto_linea)
                bbox = [x0_n,y0_n,x1_n,y1_n]
                if not ('zona' in texto_linea[0]):
                    l_item_h.append([bbox , texto_linea ])
    return l_item_h

# Agregar ordenamiento de burbuja en caso de un solo script


def f_misma_fila (lista):
    """
    Une líneas de texto en 'lista' si sus coordenadas verticales están a menos de 15 unidades de distancia.
    Modifica el texto de la línea superior y elimina la inferior.

    Parámetros:
    - lista: lista de elementos con estructura [[x, y], [texto]]

    Retorna:
    - lista_copia: lista modificada con líneas combinadas
    """

    n = len(lista)
    lista_copia = lista.copy()
    lista_aux = []
    for i in range (0 , n-1):
        if abs(lista[i][0][1] - lista[i + 1][0][1]) <= 15 :
            lista_copia[i][1][0] = lista[i][1][0] + " " + lista[i + 1][1][0]
            lista_aux.append(lista[i + 1])
    
    n = len(lista_aux)
    for i in range(0 , n):
        v_borrar = lista_aux[i]
        lista_copia.remove(v_borrar)
    
    return lista_copia


def separacion_encabezado(l_df_datos_tables,l_item_h):
    """
    Extrae los encabezados que se encuentran dentro de las cotas verticales de cada tabla
    y extrae el de la posicion (1,1) si es que existe, que corresponde al puesto

    Parámetros:
    - l_item_h: lista de elementos con estructura [bbox, texto]
    - l_df_datos_tables: lista de tablas, cada una compuesta por filas con coordenadas

    Retorna:
    - l_sp: lista de encabezados por tabla
    - l_item_h_1: lista de elementos restantes fuera de las cotas
    """

    l_sp = []
    l_item_h_1 = l_item_h.copy()

    for i_t in range(0, len (l_df_datos_tables)):
        #print('-------TABLA-------')
        table = l_df_datos_tables[i_t]
        n = len(table)
        y_min = table[1][0][0]
        y_max = table[n-1][0][0]
        n_h = len(l_item_h)
        l_h_table = []
        #print(y_min,y_max)

        for i in range(0 , n_h):
            y_i = l_item_h[i][0][1]
            if y_i <= y_max and y_i >= y_min:
                item = l_item_h[i]
                l_h_table.append(item)
                l_item_h_1.remove(item)

        l_sp.append( l_h_table )
    
    return l_sp, l_item_h_1



def area_profesional(pdf_nombre, pag):
    """
    Extrae texto desde una zona específica de una página PDF y lo concatena en un solo string,
    excluyendo líneas que contienen la palabra 'zona'.

    Parámetros:
    - pdf_nombre: nombre o ruta del archivo PDF
    - pag: número de página 

    Retorna:
    - area_profesional: string con el texto concatenado de la zona seleccionada
    """

    x0 = 14.13125
    x1 = 342.125
    y0 = 13.015625
    y1 = 95.571875


    doc = pymupdf.open(pdf_nombre)
    page = doc[pag]
    rect = pymupdf.Rect(x0, y0, x1, y1)


    # Obtener el texto como diccionario
    data = page.get_text("dict", clip=rect)

    l_items = []

    for block in data['blocks']:
        #print('--')
        if block['type']  == 0: #solo texto
            #print(block['lines'])
            for lines in block['lines']:
                x0_n = lines['bbox'][0]
                y0_n = lines['bbox'][1]
                x1_n = lines['bbox'][2]
                y1_n = lines['bbox'][3]


                texto_linea = [span["text"] for span in lines["spans"]]
                bbox = [x0_n, y0_n, x1_n, y1_n]
                if not ('zona' in texto_linea[0]):
                    l_items.append([bbox , texto_linea ])

    area_profesional = ' '.join( [linea[1][0] for linea in l_items] )
    return area_profesional


def unir_todo(l_df_datos_tables ,l_sp , l_item_h_1, area_profesional):
    """
    Construye la lista final de tablas agregando encabezados y completando cada fila
    con datos de área profesional, puesto, sector y tipo de rango.

    Parámetros:
    - l_df_datos_tables: lista de tablas con datos
    - l_sp: lista de sectores por tabla
    - l_item_h_1: lista de puestos por tabla
    - area_profesional: string con el nombre del área profesional

    Retorna:
    - l_df_final: lista de tablas enriquecidas con encabezados y contexto
    """

    l_df_final = []
    n = len(l_df_datos_tables)
    for i_t in range(0 , n):
        n_i = len(l_df_datos_tables[i_t])
        n_sp = len(l_sp[i_t])
        l_aux = []

        #-------------- encabezados-------------
        l_df_datos_tables[i_t][0][1].insert(0,'Area_profesional')
        l_df_datos_tables[i_t][0][1].insert(1,'Puesto')
        l_df_datos_tables[i_t][0][1].insert(2,'Sector')
        l_df_datos_tables[i_t][0][1].insert(3,'Tipo_rango')
        #---------------------------------------
        l_aux.append(l_df_datos_tables[i_t][0][1])

        try:
            v_puesto = l_item_h_1[i_t][1][0]
            flag = True
        except:
            v_puesto = 'Vacio'
            flag = False


        if flag:
            for i_sp in range(0, n_sp):
                v_sp = l_sp[i_t][i_sp][1][0]
                #print( v_puesto, v_sp)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(0,area_profesional)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(1,v_puesto)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(2,v_sp)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(3,"Min")
                l_aux.append(l_df_datos_tables[i_t][2*i_sp + 1][1])

                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(0,area_profesional)
                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(1,v_puesto)
                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(2,v_sp)
                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(3,"Max")
                l_aux.append(l_df_datos_tables[i_t][2*i_sp + 2][1])
        else:
            for i_sp in range(0, n_sp):
                v_sp = l_sp[i_t][i_sp][1][0]
                #print( v_puesto, v_sp)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(0,area_profesional)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(1,v_sp)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(2,v_puesto)
                l_df_datos_tables[i_t][2*i_sp + 1][1].insert(3,"Min")
                l_aux.append(l_df_datos_tables[i_t][2*i_sp + 1][1])

                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(0,area_profesional)
                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(1,v_sp)
                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(2,v_puesto)
                l_df_datos_tables[i_t][2*i_sp + 2][1].insert(3,"Max")
                l_aux.append(l_df_datos_tables[i_t][2*i_sp + 2][1])

        l_df_final.append(l_aux)
        l_aux = []
    return l_df_final

def generar_df(l_df_final):
    """
    Convierte cada entrada de l_df_final en un DataFrame y genera su versión unpivot (formato largo).

    Parámetros:
    - l_df_final: lista de tablas, donde cada tabla es una lista con encabezado + filas

    Retorna:
    - df_tables: lista de DataFrames originales
    - df_tables_unpivot: lista de DataFrames transformados con pd.melt() para el unpivot
    """

    n_t = len(l_df_final)
    df_tables = [] 
    df_tables_unpivot = []

    for i in range(0 , n_t):
        df = pd.DataFrame(l_df_final[i][1:])
        df.columns = l_df_final[i][0]
        df_unpivot = pd.melt(df, id_vars = l_df_final[i][0][:4], 
                         value_vars = l_df_final[i][0][4:],
                         var_name="Zona", value_name="Valor")


        df_tables.append(df)
        df_tables_unpivot.append  (df_unpivot )

    return df_tables, df_tables_unpivot

def sin_tabla(pdf_nombre, pag):
    """
    Abre el archivo, extrae el contenido de la página 31,
    y verifica si hay menos de 10 bloques de texto. Es decir si existe tabla o no en la pagina

    Retorna 'True' si hay menos de 10 elementos, 'false' en caso contrario

     Parámetros:
    - pdf_nombre: nombre o ruta del archivo PDF
    - pag: número de página 

    Retorna:
    - Bool
    """

    doc = pymupdf.open(pdf_nombre)
    page = doc[pag]

    # Obtener el texto como diccionario
    data = page.get_text("dict")

    l_items = []

    for block in data['blocks']:
        #print('--')
        if block['type']  == 0: #solo texto
            #print(block['lines'])
            for lines in block['lines']:
                x0_n = lines['bbox'][0]
                y0_n = lines['bbox'][1]
                x1_n = lines['bbox'][2]
                y1_n = lines['bbox'][3]


                texto_linea = [span["text"] for span in lines["spans"]]
                bbox = [x0_n, y0_n, x1_n, y1_n]
                l_items.append([bbox, texto_linea])

    if len(l_items) < 10:
        return True
    else:
        return False