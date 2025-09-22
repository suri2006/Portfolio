🧠 JobScraper AI – Scraping, Recomendaciones y Automatización con Prefect
JobScraper AI es un sistema automatizado que recopila ofertas laborales desde sitios web y grupos de Telegram, las almacena en una base de datos PostgreSQL, y genera recomendaciones personalizadas usando Gemini 2.5 Flash, tomando como referencia tu CV en PDF. Todo el flujo está orquestado con Prefect para garantizar persistencia, modularidad y escalabilidad. Para evitar problemas de bloqueo por scraping, la cantidad de pagina a scrapear es poco, maximo 5 pero si quieres puedes cambiar el codigo y modificarlo a tu gusto. Por dudas de componentes o instrucciones leer este README o Documentacion.pdf

🚀 Funcionalidades principales
- 🔍 Scraping de sitios web de empleo 
- 📲 Scraping de grupos de Telegram (Telethon)
- 🗃️ Almacenamiento en PostgreSQL local
- 📄 Lectura y análisis de CV en PDF
- 🤖 Recomendaciones laborales con Gemini 2.5 Flash
- 📤 Envío automático de recomendaciones a tu Telegram
- ⚙️ Orquestación completa con Prefect (flows + tasks)

🧱 Estructura del proyecto
- flows/
    - __init__.py
    - EducaionIT_flow.py: scraping de ofertas desde el sitio EducacionIT.
    - gemini_recomedacion.py: generación de recomendaciones laborales usando Gemini.
    - Linkedin_flow.py: scraping de publicaciones laborales en LinkedIn.
    - SQL_SP_Empleos_Flow.py: ejecución de stored procedures para cargar datos en PostgreSQL.
    - Telegram_flow.py: extracción de mensajes desde grupos de Telegram

- .env
Archivo con variables de entorno (credenciales, configuración)
- requirements.txt
Lista de librerías necesarias para ejecutar el proyecto.
- README.md
Documentación principal del proyecto.
- mi_sesion.session
Archivo generado automáticamente al iniciar sesión en Telegram con Telethon.
Se crea al ejecutar el script de autenticación. Ver Documentacion.pdf para más detalles.
- CREATE_TABLES.sql
Script SQL para crear las tablas necesarias en la base de datos PostgreSQL.
- SP_CARGA_TABLE_OFERTASLABORALES.sql
Stored procedure para insertar ofertas laborales en la base.
- main_deploy.py
Script principal que ejecuta y despliega el flujo completo usando Prefect
- Documentacion.pdf
Documentacion con detalles de las Api keys y cuidados con telegram.



"Tambien se creara una carpeta pero es la de nuestro entorno env, que lo mas recomendable es crearlo."


⚙️ Instalación
- Cloná el repositorio

- Creá un entorno virtual
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows

- Instalá las dependencias
pip install -r requirements.txt

- Tener instalado PostgreSQL y ejecutar los archivos .sql

- Configurá tu archivo .env
Copiá .env.example a .env y completá tus credenciales:
cp .env.example .env


🔐 Variables de entorno (.env)

Conexión a PostgreSQL
- usuario_postgres: Usuario de la base de datos
- contrasenia_postgres: Contraseña del usuario 
- host_postgres: Host de la base de datos (ej. localhost)
- puerto_postgres: Puerto de conexión (ej. 5432)
- base_datos_postgres: Nombre de la base de datos (ej. empleos_scrap_db)

Google Custom Search
- api_key_google_search: Clave de API para usar el motor de búsqueda personalizado de Google
- cse_id_google_search: ID del motor de búsqueda personalizado (CSE)

LinkedIn
- email_linkedin: Email de acceso a LinkedIn
- password_linkedin: Contraseña de LinkedIn

Telegram
- api_id_telegram: ID de API de Telegram
- api_hash_telegram: Hash secreto de la API
- id_grupo_telegram: ID o alias del grupo de nuestro grupo Telegram destino, donde se subiran nuestras recomendaciones (ej. @Ofertas_Empleos_1).Este grupo debe estar publico.


🧪 Ejecución

En main_deploy.py, en la seccion del "if" se puede modificar el "name" que sera el nombre del deploy  y "cron" que es la hora a la que se va a ejecutar y frecuencia. Para mas detalles de cron buscar documentacion o ver en https://es.wikipedia.org/wiki/Cron_(Unix)

if __name__ == '__main__':
    master_flow.serve(
        name="Master_Deploy_v1.0",
        cron="10 19 * * *", 
    )


Podés correr el flujo completo desde main_deploy.py o ejecutar cada flow.py de forma independiente
En la carpeta Curriculum dejamos nuestro CV en formato .pdf con el nombre que quieras, pero tiene que ser UNO solo.


También podés usar Prefect CLI para correr y monitorear:
prefect deployment run scrape_web
prefect deployment run recommend_jobs


📬 ¿Cómo funciona?
- Scraping: Se extraen ofertas laborales de sitios web y grupos de Telegram.
- Almacenamiento: Los datos se guardan en una base PostgreSQL local.
- Análisis de CV: Se lee tu CV en PDF y se extraen tus habilidades.
- Gemini: Se consulta Gemini 2.5 Flash para generar recomendaciones personalizadas en base a tu CV.
- Notificación: Las recomendaciones se envían automáticamente a tu grupo Telegram.