USE empresa;

#Activaremos el parametro para crear funciones
SET GLOBAL log_bin_trust_function_creators = 1;

#SCRIPTS DE LAS 4 FUNCIONES

/*CREATE DEFINER=`root`@`localhost` FUNCTION `num_aleatorio`(vmax int,vmin int) RETURNS int
BEGIN
DECLARE vresultado INT;
SELECT FLOOR((RAND() * (vmax-vmin))+vmin) INTO vresultado;
RETURN vresultado;
END

CREATE DEFINER=`root`@`localhost` FUNCTION `f_vendedor_aleatorio`() RETURNS varchar(50) CHARSET utf8mb4
BEGIN
#Hay que tener en cuenta que el tipo de variable y cantidad de caracteres
#de la tabla a la que se hace referencia, en este caso vresultado toma un DNI de tb_vendedor
DECLARE vresultado VARCHAR(50);
DECLARE valeatorio INT;
DECLARE vmax INT;
SELECT COUNT(*) INTO vmax FROM tb_vendedor;
#como la funcion num_aleatorio crea un valor entre 1 y el vmax, si le resto -1
# entonces ahora varia entre 0 y vmax-1, para con el limit poder tomar
SET valeatorio=num_aleatorio(0,vmax);
SELECT MATRICULA INTO vresultado FROM tb_vendedor LIMIT valeatorio,1;
RETURN vresultado;
END

CREATE DEFINER=`root`@`localhost` FUNCTION `f_producto_aleatorio`() RETURNS varchar(10) CHARSET utf8mb4
BEGIN
#Hay que tener en cuenta que el tipo de variable y cantidad de caracteres
#de la tabla a la que se hace referencia, en este caso vresultado toma un DNI de tb_productos
DECLARE vresultado VARCHAR(10);
DECLARE valeatorio INT;
DECLARE vmax INT;
SELECT COUNT(*) INTO vmax FROM tb_productos;
#como la funcion num_aleatorio crea un valor entre 1 y el vmax, si le resto -1
# entonces ahora varia entre 0 y vmax-1, para con el limit poder tomar
SET valeatorio=num_aleatorio(0,vmax);
SELECT CODIGO INTO vresultado FROM tb_productos LIMIT valeatorio,1;
RETURN vresultado;
END

CREATE DEFINER=`root`@`localhost` FUNCTION `f_cliente_aleatorio`() RETURNS varchar(11) CHARSET utf8mb4
BEGIN
#Hay que tener en cuenta que el tipo de variable y cantidad de caracteres
#de la tabla a la que se hace referencia, en este caso vresultado toma un DNI de tb_clientes
DECLARE vresultado VARCHAR(11);
DECLARE valeatorio INT;
DECLARE vmax INT;
SELECT COUNT(*) INTO vmax FROM tb_clientes;
#como la funcion num_aleatorio crea un valor entre 1 y el vmax, si le resto -1
# entonces ahora varia entre 0 y vmax-1, para con el limit poder tomar
SET valeatorio=num_aleatorio(0,vmax);
SELECT DNI INTO vresultado FROM tb_clientes LIMIT valeatorio,1;
RETURN vresultado;
END

*/

#stored procedures
/*CREATE DEFINER=`root`@`localhost` PROCEDURE `venta_ficticia`(fecha DATE,maxitem INT)
BEGIN
DECLARE vcliente VARCHAR(11);
DECLARE vvendedor VARCHAR(5);
DECLARE numfactura INT;
DECLARE codproducto VARCHAR(10);
DECLARE prec FLOAT;
DECLARE contador INT DEFAULT 1;

SELECT MAX(NUMERO) + 1 INTO numfactura FROM tb_facturas;
SET vcliente = f_cliente_aleatorio();
SET vvendedor = f_vendedor_aleatorio();
INSERT INTO tb_facturas (NUMERO, FECHA, DNI, MATRICULA, IMPUESTO) VALUES (numfactura, fecha, vcliente, vvendedor, 0.16);
#CALL for_items(numfactura,maxitem);

WHILE contador <= maxitem DO
SET codproducto=f_producto_aleatorio();
SELECT PRECIO INTO prec FROM tb_productos WHERE CODIGO=codproducto;
INSERT INTO tb_items(NUMERO,CODIGO,CANTIDAD,PRECIO) VALUES (numfactura,codproducto,1,prec);
SET contador=contador+1;
END WHILE;

END 
*/


#consultas para probar la venta ficticia
CALL venta_ficticia("20200101",5);
SELECT * FROM tb_items;
SELECT * FROM tb_facturas;
SELECT count(*) AS cantidad_items FROM tb_items;
SELECT COUNT(*) AS cantidad_facturas FROM tb_facturas;

