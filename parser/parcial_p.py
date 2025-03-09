import boto3
import csv
import os
import datetime
import logging
from bs4 import BeautifulSoup

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente de S3
s3_client = boto3.client("s3")

def extract_data_from_html(html_content):
    """
    Extrae información de cada casa desde el HTML.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    casas = []

    for casa in soup.find_all("div", class_="casa-item"):
        barrio = casa.find("span", class_="barrio")
        valor = casa.find("span", class_="precio")
        num_habitaciones = casa.find("span", class_="habitaciones")
        num_banos = casa.find("span", class_="banos")
        metros2 = casa.find("span", class_="metros2")

        if None in (barrio, valor, num_habitaciones, num_banos, metros2):
            continue  # Ignorar registros incompletos

        casas.append([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            barrio.text.strip(),
            valor.text.strip(),
            num_habitaciones.text.strip(),
            num_banos.text.strip(),
            metros2.text.strip()
        ])
    
    return casas

def app(event, context):
    """
    Procesa un archivo HTML subido a S3, extrae información y la guarda como CSV.
    """
    try:
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        object_key = event["Records"][0]["s3"]["object"]["key"]
        logger.info(f"Procesando archivo: s3://{bucket_name}/{object_key}")

        # Obtener el archivo HTML desde S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        html_content = response["Body"].read().decode("utf-8")

        # Extraer datos
        casas_data = extract_data_from_html(html_content)

        if not casas_data:
            logger.warning("No se encontraron casas en el archivo HTML.")
            return {"statusCode": 400, "message": "Archivo HTML sin datos válidos."}

        # Crear nombre del archivo CSV
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        output_bucket = "casas-final-xxx"
        output_file = f"{fecha_actual}.csv"
        temp_file = f"/tmp/{output_file}"

        # Escribir CSV en el sistema temporal de Lambda
        with open(temp_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])
            writer.writerows(casas_data)

        # Subir archivo CSV al bucket destino
        s3_client.upload_file(temp_file, output_bucket, output_file)
        logger.info(f"Archivo guardado en s3://{output_bucket}/{output_file}")

        return {"statusCode": 200, "message": f"Archivo guardado en s3://{output_bucket}/{output_file}"}

    except Exception as e:
        logger.error(f"Error procesando el archivo: {str(e)}")
        return {"statusCode": 500, "message": str(e)}
