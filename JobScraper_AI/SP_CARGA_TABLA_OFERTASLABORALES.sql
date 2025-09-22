CREATE PROCEDURE STG_TABLA_EMPLEOS()
LANGUAGE plpgsql
AS $$

DECLARE
    v_fecha INTEGER;
BEGIN


CREATE TEMP TABLE temp_1 AS
	SELECT 	portal,
			puesto,
			modalidad,
			empresa,
			descripcion,
			jornada,
			URL,
			TO_CHAR(fecha_subida, 'YYYYMMDD')::INTEGER AS fecha_subida			
	FROM public.data_linkedin_jobs
	UNION
	SELECT	portal,
			puesto,
			modalidad,
			empresa,
			descripcion,
			'' jornada,
			url,
			TO_CHAR(fecha_subida, 'YYYYMMDD')::INTEGER AS fecha_subida		
	FROM public.data_telegram
	UNION
	SELECT	portal,
			puesto,
			modalidad,
			empresa,
			descripcion,
			'' jornada,
			url,
			TO_CHAR(fecha_subida, 'YYYYMMDD')::INTEGER AS fecha_subida
	FROM public.data_educacionit;
	


-- Primera fecha máxima
SELECT MAX(fecha_subida) INTO v_fecha FROM temp_1;

DELETE FROM public.ofertas_laborales WHERE fecha_subida = v_fecha;


INSERT INTO ofertas_laborales (
    portal,
    puesto,
    modalidad,
    empresa,
    descripcion,
    jornada,
    url,
    fecha_subida
)
SELECT DISTINCT
    portal,
    puesto,
    modalidad,
    empresa,
    descripcion,
    jornada,
    url,
    fecha_subida
FROM temp_1;



END;
$$;



