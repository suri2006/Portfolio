DROP TABLE IF EXISTS public.principal;
CREATE TABLE public.principal
(
    id serial NOT NULL,
    Cod_loc VARCHAR(200),
    IdProvincia VARCHAR(200),
    IdDepartamento VARCHAR(200),
    Categoria VARCHAR(200),
    Provincia VARCHAR(200),
    Localidad VARCHAR(200),
    nombre VARCHAR(200),
    Domicilio VARCHAR(200),
    CP VARCHAR(200),
    Telefono VARCHAR(200),
    Mail VARCHAR(200),
    Web VARCHAR(200),
    upload_date date,
    PRIMARY KEY (id)
);

DROP TABLE IF EXISTS public.cine_tabla;
CREATE TABLE public.cine_tabla
(
    id serial NOT NULL,
    Provincia VARCHAR(200),
    Cant_pantallas VARCHAR(200),
    Cant_butacas VARCHAR(200),
    Cant_espacio_incaa VARCHAR(200),
    upload_date date,
    PRIMARY KEY (id)
)