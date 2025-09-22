from prefect import flow
import inspect
#Scraping
from flows.EducacionIT_flow import scraping_educacionit_flow
from flows.Linkedin_flow import linkedin_scarping_flow
from flows.Telegram_flow import scraping_telegram_flow
#Carga y analisis
from flows.SQL_SP_Empleos_flow import flujo_etl
from flows.gemini_recomendacion_flow import flow_recomendaciones_telegram




@flow(name="master_flow")
async def master_flow():
    for i, f in enumerate([scraping_educacionit_flow , linkedin_scarping_flow , scraping_telegram_flow , flujo_etl , flow_recomendaciones_telegram], start=1):
        try:
            if inspect.iscoroutinefunction(inspect.unwrap(f)):
                await f()
            else:
                f()

        except Exception as e:
            print(f" Error en flujo {i}: {e}")


if __name__ == '__main__':
    master_flow.serve(
        name="Master_Deploy_v1.0",
        cron="10 19 * * *",  # Ejecuta todos los días a las 18:00
    )
