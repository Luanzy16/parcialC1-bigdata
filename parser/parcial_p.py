import csv
import boto3
from bs4 import BeautifulSoup
from datetime import datetime


s3_client = boto3.client("s3")
S3_BUCKET = "zappa-scrapping"
S3_KEY = "datos.csv"


def app(event, context):
    """Función principal para procesar HTML de S3 y extraer propiedades."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key="index.html")
        html = response["Body"].read().decode("utf-8")

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error al leer HTML de S3: {str(e)}"
        }

    soup = BeautifulSoup(html, "html.parser")
    today = datetime.today().strftime("%Y-%m-%d")
    properties = []

    for listing in soup.find_all("div", class_="listing-card__information"):
        barrio_elem = listing.find("span", class_="listing-card__location")
        valor_elem = listing.find("span", class_="price")
        habitaciones_elem = listing.find("span", class_="bedrooms")
        banos_elem = listing.find("span", class_="bathrooms")
        mts2_elem = listing.find("span", class_="area")

        barrio = barrio_elem.text.strip() if barrio_elem else "N/A"
        valor = valor_elem.text.strip() if valor_elem else "N/A"
        num_habitaciones = (
            habitaciones_elem.text.strip().split()[0]
            if habitaciones_elem else "N/A"
        )
        num_banos = banos_elem.text.strip() if banos_elem else "N/A"
        mts2 = mts2_elem.text.strip() if mts2_elem else "N/A"

        properties.append([
            today, barrio, valor, num_habitaciones, num_banos, mts2
        ])

    if not properties:
        return {
            "statusCode": 500,
            "body": "No se encontraron datos en el HTML. Revisa la estructura."
        }

    csv_buffer = csv.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["FechaDescarga", "Barrio", "Valor",
                     "NumHabitaciones", "NumBanos", "mts2"])

    for prop in properties:
        writer.writerow(prop)

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET, Key=S3_KEY, Body=csv_buffer.getvalue()
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error al guardar CSV en S3: {str(e)}"
        }

    return {"statusCode": 200, "body": "Archivo CSV guardado correctamente."}
