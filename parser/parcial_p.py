import boto3
import csv
import datetime
from io import StringIO
from bs4 import BeautifulSoup

# Configuración de S3
BUCKET_HTML = "zappa-scrapping"  # Donde está el HTML
BUCKET_CSV = "zappa-parser1"  # Donde guardar el CSV

s3_client = boto3.client("s3")

def app(event, context):
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    html_filename = f"{today}.html"
    csv_filename = f"{today}.csv"

    # Descargar HTML desde S3
    try:
        html_obj = s3_client.get_object(Bucket=BUCKET_HTML, Key=html_filename)
        html_content = html_obj["Body"].read().decode("utf-8")
    except Exception as e:
        return {"statusCode": 500, "body": f"Error al leer HTML de S3: {str(e)}"}

    # Extraer datos del HTML
    soup = BeautifulSoup(html_content, "html.parser")
    properties = []

    for listing in soup.find_all("div", class_="listing-card__information"):  # Identificar cada propiedad
        barrio_elem = listing.find("div", class_="listing-card__location__geo")
        valor_elem = listing.find("span", {"data-test": "price__actual"})
        habitaciones_elem = listing.find("p", {"data-test": "bedrooms"})
        banos_elem = listing.find("p", {"data-test": "bathrooms"})
        metros_elem = listing.find("p", {"data-test": "floor-area"})

        barrio = barrio_elem.text.strip() if barrio_elem else "N/A"
        valor = valor_elem.text.strip() if valor_elem else "N/A"
        num_habitaciones = habitaciones_elem.text.strip().split()[0] if habitaciones_elem else "N/A"
        num_banos = banos_elem.text.strip().split()[0] if banos_elem else "N/A"
        mts2 = metros_elem.text.strip().split()[0] if metros_elem else "N/A"

        properties.append([today, barrio, valor, num_habitaciones, num_banos, mts2])

    # Verifica si se encontraron datos antes de guardar
    if not properties:
        return {"statusCode": 500, "body": "No se encontraron datos en el HTML. Revisa la estructura."}

    # Convertir datos a CSV
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])  # Encabezados
    writer.writerows(properties)

    # Subir CSV a S3
    try:
        s3_client.put_object(
            Bucket=BUCKET_CSV,
            Key=csv_filename,
            Body=csv_buffer.getvalue().encode("utf-8"),
            ContentType="text/csv"
        )
    except Exception as e:
        return {"statusCode": 500, "body": f"Error al guardar CSV en S3: {str(e)}"}

    return {
        "statusCode": 200,
        "body": f"CSV guardado en s3://{BUCKET_CSV}/{csv_filename}"
    }
