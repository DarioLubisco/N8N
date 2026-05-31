# -*- coding: utf-8 -*-
import os
import pyodbc
from dotenv import load_dotenv
from ftplib import FTP
import time
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

def load_config():
    """Carga la configuración desde el archivo .env."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Imp_Inv_Dronena.env')
    load_dotenv(env_path)
    config = {
        'db_server': os.getenv('DB_SERVER'),
        'db_database': os.getenv('DB_DATABASE'),
        'db_username': os.getenv('DB_USERNAME'),
        'db_password': os.getenv('DB_PASSWORD'),
        'db_driver': os.getenv('DB_DRIVER'),
        'ftp_uri': os.getenv('INPUT_FILE_FTP'),
        'input_file': os.getenv('INPUT_FILE_NAME'),
        'file_attempts': int(os.getenv('FILE_ATTEMPTS', 5)),
        'file_delay': int(os.getenv('FILE_DELAY', 3)),
        'sql_attempts': int(os.getenv('SQL_ATTEMPTS', 5)),
        'sql_delay': int(os.getenv('SQL_DELAY', 3)),
        'table_name': '[Procurement].[Inventario_Dronena]'
    }
    return config

def extract_from_ftp(config):
    """Extrae el archivo de inventario desde el servidor FTP."""
    ftp_uri = config.get('ftp_uri')
    ftp_password = os.getenv('INPUT_FILE_FTP_PASSWORD', '')
    if not ftp_uri:
        logging.error("La variable INPUT_FILE_FTP no está definida en el archivo .env o está vacía.")
        return False
    try:
        ftp_url = ftp_uri.replace('ftp://', '')
        ftp_user, ftp_rest = ftp_url.split('@')
        ftp_host, ftp_path = ftp_rest.split('/', 1)
    except (ValueError, TypeError):
        logging.error("El formato de 'INPUT_FILE_FTP' en el archivo .env no es válido.")
        return False
    # Directorio de descarga local
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    local_filename = os.path.join(download_dir, config['input_file'])
    
    remote_path = f"/{ftp_path}/{config['input_file']}"
    for attempt in range(config['file_attempts']):
        try:
            logging.info(f"Intento {attempt + 1} de {config['file_attempts']}: Conectando a FTP {ftp_host}...")
            with FTP(ftp_host) as ftp:
                ftp.login(user=ftp_user, passwd=ftp_password)
                logging.info(f"Descargando '{remote_path}' a '{local_filename}'...")
                with open(local_filename, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {remote_path}', local_file.write)
            logging.info("Descarga FTP completada con éxito.")
            return True
        except Exception as e:
            logging.error(f"Error en la descarga FTP: {e}")
            if attempt < config['file_attempts'] - 1:
                logging.info(f"Reintentando en {config['file_delay']} segundos...")
                time.sleep(config['file_delay'])
            else:
                logging.error("Se superó el número máximo de reintentos para la descarga FTP.")
                return False

def validate_product(product):
    """Valida los datos de un producto antes de cargar."""
    try:
        # Validaciones básicas
        if not product[0]:  # codigo_barras
            return False
        if product[3] < 0 or product[4] < 0:  # precio, cantidad
            return False
        return True
    except Exception:
        return False

def transform_fixed_width_file(file_path):
    """Transforma el archivo de ancho fijo en una lista de productos válidos."""
    products = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            header_line = f.readline()
            col_specs = [
                ('codigo', 0, 7), ('descripcion', 7, 48), ('precio', 48, 63),
                ('cantidad', 63, 75), ('dcto', 75, 82), ('margenfar', 82, 93),
                ('dcto_ufi', 93, 104), ('empaque', 104, 112), ('dcto_empque', 112, 120),
                ('codbarras', 120, 137), ('tipo', 137, 142), ('codprov', 142, 152),
                ('lote', 152, 182), ('fecha_exp', 182, 193), ('regulado', 193, 202),
                ('cadena_frio', 202, 215), ('dcto_comer', 215, 226), ('dcto_pp', 226, 236),
                ('original', 236, 246), ('umf', 246, 250), ('fechaingreso', 250, 263),
                ('adm', 263, 266)
            ]
            for line in f:
                if not line.strip():
                    continue
                try:
                    codbarras = line[col_specs[9][1]:col_specs[9][2]].strip()
                    if codbarras:
                        product = (
                            codbarras,
                            line[col_specs[0][1]:col_specs[0][2]].strip(),
                            line[col_specs[1][1]:col_specs[1][2]].strip(),
                            float(line[col_specs[2][1]:col_specs[2][2]].strip() or 0.0),
                            int(line[col_specs[3][1]:col_specs[3][2]].strip() or 0),
                            float(line[col_specs[4][1]:col_specs[4][2]].strip() or 0.0),
                            float(line[col_specs[5][1]:col_specs[5][2]].strip() or 0.0),
                            float(line[col_specs[6][1]:col_specs[6][2]].strip() or 0.0),
                            int(line[col_specs[7][1]:col_specs[7][2]].strip() or 0),
                            float(line[col_specs[8][1]:col_specs[8][2]].strip() or 0.0),
                            line[col_specs[10][1]:col_specs[10][2]].strip(),
                            line[col_specs[11][1]:col_specs[11][2]].strip(),
                            line[col_specs[12][1]:col_specs[12][2]].strip(),
                            line[col_specs[13][1]:col_specs[13][2]].strip(),
                            line[col_specs[14][1]:col_specs[14][2]].strip(),
                            line[col_specs[15][1]:col_specs[15][2]].strip(),
                            float(line[col_specs[16][1]:col_specs[16][2]].strip() or 0.0),
                            float(line[col_specs[17][1]:col_specs[17][2]].strip() or 0.0),
                            line[col_specs[18][1]:col_specs[18][2]].strip(),
                            int(line[col_specs[19][1]:col_specs[19][2]].strip() or 0),
                            line[col_specs[20][1]:col_specs[20][2]].strip(),
                            int(line[col_specs[21][1]:col_specs[21][2]].strip() or 0),
                        )
                        if validate_product(product):
                            products.append(product)
                        else:
                            logging.warning(f"Producto inválido: {product}")
                except (ValueError, IndexError) as e:
                    logging.error(f"Error procesando la línea: {line.strip()} -> {e}")
    except FileNotFoundError:
        logging.error(f"El archivo '{file_path}' no fue encontrado.")
        return []
    return products

def load_to_sql(config, products):
    """Carga los productos en la base de datos SQL Server usando MERGE."""
    conn_str = (
        f"DRIVER={{{config['db_driver']}}};"
        f"SERVER={config['db_server']};"
        f"DATABASE={config['db_database']};"
        f"UID={config['db_username']};"
        f"PWD={config['db_password']};"
    )
    table_name = config['table_name']
    for attempt in range(config['sql_attempts']):
        try:
            logging.info(f"Intento {attempt + 1} de {config['sql_attempts']}: Conectando a SQL Server...")
            with pyodbc.connect(conn_str) as cnxn:
                cursor = cnxn.cursor()
                logging.info("Conexión a SQL Server exitosa.")
                create_table_sql = f"""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'{table_name}') AND type in (N'U'))
                CREATE TABLE {table_name} (
                    id INT IDENTITY(1,1) PRIMARY KEY, codigo_barras VARCHAR(50) NOT NULL UNIQUE,
                    codigo VARCHAR(20), descripcion VARCHAR(255), precio DECIMAL(18, 2), cantidad INT,
                    dcto DECIMAL(10, 2), margen_far DECIMAL(10, 2), dcto_ufi DECIMAL(10, 2),
                    empaque INT, dcto_empaque DECIMAL(10, 2), tipo VARCHAR(5), cod_prov VARCHAR(20),
                    lote VARCHAR(50), fecha_exp VARCHAR(10), regulado VARCHAR(5), cadena_frio VARCHAR(5),
                    dcto_comer DECIMAL(10, 2), dcto_pp DECIMAL(10, 2), original VARCHAR(20), umf INT,
                    fecha_ingreso VARCHAR(20), adm INT
                )
                """
                cursor.execute(create_table_sql)
                cnxn.commit()
                merge_sql = f"""
                MERGE {table_name} AS T
                USING (VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)) 
                    AS S (codigo_barras, codigo, descripcion, precio, cantidad, dcto, margen_far, dcto_ufi,
                          empaque, dcto_empaque, tipo, cod_prov, lote, fecha_exp, regulado, cadena_frio,
                          dcto_comer, dcto_pp, original, umf, fecha_ingreso, adm)
                ON T.codigo_barras = S.codigo_barras
                WHEN MATCHED THEN
                    UPDATE SET
                        T.codigo=S.codigo, T.descripcion=S.descripcion, T.precio=S.precio, T.cantidad=S.cantidad,
                        T.dcto=S.dcto, T.margen_far=S.margen_far, T.dcto_ufi=S.dcto_ufi, T.empaque=S.empaque,
                        T.dcto_empaque=S.dcto_empaque, T.tipo=S.tipo, T.cod_prov=S.cod_prov, T.lote=S.lote,
                        T.fecha_exp=S.fecha_exp, T.regulado=S.regulado, T.cadena_frio=S.cadena_frio,
                        T.dcto_comer=S.dcto_comer, T.dcto_pp=S.dcto_pp, T.original=S.original, T.umf=S.umf,
                        T.fecha_ingreso=S.fecha_ingreso, T.adm=S.adm
                WHEN NOT MATCHED BY TARGET THEN
                    INSERT (codigo_barras, codigo, descripcion, precio, cantidad, dcto, margen_far, dcto_ufi,
                            empaque, dcto_empaque, tipo, cod_prov, lote, fecha_exp, regulado, cadena_frio,
                            dcto_comer, dcto_pp, original, umf, fecha_ingreso, adm)
                    VALUES (S.codigo_barras, S.codigo, S.descripcion, S.precio, S.cantidad, S.dcto, S.margen_far,
                            S.dcto_ufi, S.empaque, S.dcto_empaque, S.tipo, S.cod_prov, S.lote, S.fecha_exp,
                            S.regulado, S.cadena_frio, S.dcto_comer, S.dcto_pp, S.original, S.umf, S.fecha_ingreso, S.adm);
                """
                logging.info(f"Procesando {len(products)} registros para la base de datos...")
                cursor.fast_executemany = True
                cursor.executemany(merge_sql, products)
                cnxn.commit()
                logging.info(f"¡Éxito! Se han insertado/actualizado {len(products)} registros en la tabla {table_name}.")
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            logging.error(f"Error de base de datos ({sqlstate}): {ex}")
            if attempt < config['sql_attempts'] - 1:
                logging.info(f"Reintentando en {config['sql_delay']} segundos...")
                time.sleep(config['sql_delay'])
            else:
                logging.error("Se superó el número máximo de reintentos para la conexión a SQL.")
                return False
    return False

def archive_file(file_path):
    """Mueve el archivo procesado a una carpeta de histórico (Trazabilidad)."""
    try:
        archive_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'archive')
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        archive_path = os.path.join(archive_dir, f"{name}_{timestamp}{ext}")
        os.rename(file_path, archive_path)
        logging.info(f"Trazabilidad: Archivo movido a {archive_path}")
    except Exception as e:
        logging.error(f"Error al archivar el archivo: {e}")

def etl_main():
    """Orquesta el proceso ETL completo."""
    config = load_config()
    if extract_from_ftp(config):
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        local_filename = os.path.join(download_dir, config['input_file'])
        product_data = transform_fixed_width_file(local_filename)
        if product_data:
            if load_to_sql(config, product_data):
                archive_file(local_filename)
        else:
            logging.warning("No se encontraron datos de productos para procesar.")
    else:
        logging.error("No se pudo extraer el archivo desde FTP.")

if __name__ == "__main__":
    etl_main()


