## Creando el entorno de desarrollo 

Primero debemos crear el entorno para instalar todas las librerías que utilizaremos con Python, para ello tendremos que instalar “virtualenv” con pip de Python. 
https://virtualenv.pypa.io/en/latest/installation.html
Utilizando en el caso de Windows en el cmd utilizamos el comando 
“ pip install virtualenv ”
Una vez instalado podemos crear el entorno , abierto el cmd escribimos 
“ virtualenv [nombre] ”
Donde [nombre] es el nombre de nuestro entorno , luego para activar el entorno
“ .\ [nombre] \ Scripts \activate “
Entonces ya podemos instalar las librerías que usaremos.
En el mismo cmd una vez utilizado el entorno virtual instalamos
-	Pip install pandas
-	Pip install SQLAlchemy
-	Pip install Click
-	Pip install requests
-	Pip install csv
-	Pip install openpyxl
-	Pip install psycopg2

## Ejecutando el programa
Solo hay que ejecutar main.py 
