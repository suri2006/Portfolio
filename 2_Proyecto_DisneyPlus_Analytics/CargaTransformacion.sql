CREATE DATABASE disneyT;
USE disneyT;
DROP TABLE dataset;

CREATE TABLE dataset(
show_id VARCHAR(20)
,ttype VARCHAR (50)
,title VARCHAR(150)
,director VARCHAR(150)
,cast VARCHAR(300)
,country VARCHAR(150)
,date_added VARCHAR(100)
,release_year VARCHAR(20)
,rating VARCHAR(50)
,duration VARCHAR(50)
,listed_in VARCHAR(200)
,ddescription VARCHAR(500)
);

#CARGA DE DATOS
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/disney_plus_titles.csv'
INTO TABLE dataset
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

#OBSERVAMOS LOS DATOS
SELECT * FROM dataset;


#---TABLA DIMENSION FECHA_DE_INGRESO ( PODEMOS AGREGAR MAS FILAS COMO CUATRIMESTRE O SEMESTRE QUEDA A CRITERIO)----

# (pd: iniciar el contador para crear el id de la tabla)
SET @contador=0;
CREATE TABLE tb_fecha_de_agregado AS
WITH CALENDARIO AS(SELECT show_id ,date_added,SUBSTRING_INDEX(date_added," ",1) AS MES
, SUBSTRING_INDEX(SUBSTRING_INDEX(date_added,",",1)," ",-1) AS DIA
, SUBSTRING_INDEX(date_added,", ",-1) AS ANIO FROM dataset
)
SELECT DISTINCT (SELECT @contador:=@contador+1) AS id_fecha_de_agregado,
date_added AS fecha_completa, CAL.dia, CAL.mes, SUBSTRING(CAL.MES, 1, 3) AS mes_corto
, CASE 
WHEN MES="January" THEN 1
WHEN MES="February" THEN 2
WHEN MES="March" THEN 3
WHEN MES="April" THEN 4
WHEN MES="May" THEN 5
WHEN MES="June" THEN 6
WHEN MES="July" THEN 7
WHEN MES="August" THEN 8
WHEN MES="September" THEN 9
WHEN MES="October" THEN 10
WHEN MES="November" THEN 11
WHEN MES="December" THEN 12
END num_mes, CAL.anio
FROM CALENDARIO AS CAL;

# este id contiene el valor nulo por eso lo borramos
DELETE FROM tb_fecha_de_agregado WHERE id_fecha_De_agregado=168;

#VISUALIZAMOS LA TABLA CREADA
SELECT * FROM tb_fecha_de_agregado;



#--- TABLA DIMENSION DIRECCION---
SET @contador=0;
CREATE TABLE tb_direccion AS 
SELECT DISTINCT (SELECT @contador:=@contador+1) AS id_direccion ,director,cast FROM dataset
WHERE (director <> "" OR cast <> "");

SELECT * FROM tb_direccion;

#---TABLA DIMENSION DESCRIPCION---
SET @contador=0;
CREATE TABLE tb_descripcion AS
SELECT DISTINCT (SELECT @contador:=@contador+1) AS id_descripcion,ddescription AS descripcion FROM dataset
WHERE ddescription <> "";

SELECT * FROM tb_descripcion;

#---TABLA PRINCIPAL DISNEY_PLUS---
CREATE TABLE tb_disney_principal AS
SELECT SUBSTRING_INDEX(A.show_id,"s",-1) AS id, A.ttype AS tipo,A.title AS titulo, B.id_direccion AS id_direccion,
A.country AS pais, C.id_fecha_de_agregado AS id_fecha_de_agregado,
A.release_year AS fecha_de_lanzamiento, A.rating AS edad_clasificacion,
A.duration AS duracion, A.listed_in AS genero,
D.id_descripcion AS id_descripcion
FROM dataset A
LEFT JOIN tb_direccion B ON (A.cast=B.cast AND A.director=B.director)
LEFT JOIN tb_fecha_de_agregado C ON A.date_added=C.fecha_completa
LEFT JOIN tb_descripcion D ON A.ddescription=D.descripcion;


#NOTAMOS QUE HAY ESPACIOS VACIOS Y LO REEMPLAZAMOS POR VALORES "null" para power bi
ALTER TABLE tb_disney_principal MODIFY id_direccion VARCHAR(20);
UPDATE tb_disney_principal
SET id_direccion=""
WHERE id_direccion IS NULL;

UPDATE tb_disney_principal
SET pais="" 
WHERE pais IS NULL;

ALTER TABLE tb_disney_principal MODIFY id_fecha_de_agregado VARCHAR(20);
UPDATE tb_disney_principal
SET id_fecha_de_agregado="" 
WHERE id_fecha_de_agregado IS NULL;

ALTER TABLE tb_disney_principal MODIFY fecha_de_lanzamiento VARCHAR(20);
UPDATE tb_disney_principal
SET fecha_de_lanzamiento="" 
WHERE fecha_de_lanzamiento IS NULL;

UPDATE tb_disney_principal
SET edad_clasificacion="" 
WHERE edad_clasificacion IS NULL;

UPDATE tb_disney_principal
SET duracion="" 
WHERE duracion IS NULL;

UPDATE tb_disney_principal
SET genero="" 
WHERE genero IS NULL;

ALTER TABLE tb_disney_principal MODIFY id_descripcion VARCHAR(20);
UPDATE tb_disney_principal
SET id_descripcion="" 
WHERE id_descripcion IS NULL;

UPDATE tb_direccion
SET director="" 
WHERE director IS NULL;

UPDATE tb_direccion
SET cast="" 
WHERE cast IS NULL;

SELECT * FROM tb_disney_principal;
SELECT * FROM tb_direccion;


#CREAMOS LAS VISTAS
CREATE VIEW v_disney_principal AS
SELECT * FROM tb_disney_principal;

CREATE VIEW v_disney_tb_descripcion AS
SELECT * FROM tb_descripcion;

CREATE VIEW v_disney_tb_direccion AS
SELECT * FROM tb_direccion;

CREATE VIEW v_disney_fecha_de_agregado AS
SELECT * FROM tb_fecha_de_agregado;

# vemos los views que creamos
SELECT * FROM v_disney_principal;
SELECT * FROM v_disney_tb_descripcion;
SELECT * FROM v_disney_tb_direccion;
SELECT * FROM v_disney_fecha_de_agregado;



 



