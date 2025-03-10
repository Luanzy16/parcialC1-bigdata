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

    for listing in soup.find_all("div", class_="listing"):  # Ajusta la clase según HTML real
        title = listing.find("h2").text.strip() if listing.find("h2") else "N/A"
        price = listing.find("span", class_="price").text.strip() if listing.find("span", class_="price") else "N/A"
        location = listing.find("span", class_="location").text.strip() if listing.find("span", class_="location") else "N/A"
        
        properties.append([title, price, location])

    # Convertir datos a CSV
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Título", "Precio", "Ubicación"])  # Encabezados
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
