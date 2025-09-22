CREATE TABLE IF NOT EXISTS DATA_EDUCACIONIT (
    id SERIAL PRIMARY KEY,
    Portal TEXT,
    Empresa TEXT,
	Modalidad TEXT,
	Puesto TEXT,
	Descripcion TEXT,
	Jornada TEXT,
	URL TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS DATA_TELEGRAM (
    id SERIAL PRIMARY KEY,
    Portal TEXT,
    Puesto TEXT,
	Empresa TEXT,
	Modalidad TEXT,
	Descripcion TEXT,
	URL TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS DATA_LINKEDIN_JOBS (
    id SERIAL PRIMARY KEY,
    Portal TEXT,
	Puesto TEXT,
    Modalidad TEXT,
	Empresa TEXT,
	Descripcion TEXT,
	Jornada TEXT,
	URL TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ofertas_laborales (
    portal TEXT,
    puesto TEXT,
    modalidad TEXT,
    empresa TEXT,
    descripcion TEXT,
    jornada TEXT,
    url TEXT,
    fecha_subida INTEGER
);


select * from DATA_EDUCACIONIT;
select * from DATA_TELEGRAM;
select * from DATA_LINKEDIN_JOBS;
