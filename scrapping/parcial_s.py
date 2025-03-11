import requests
import boto3
import datetime

BUCKET_NAME = "zappa-scrapping"
BASE_URL = (
    "https://casas.mitula.com.co/find?"
    "operationType=sell&propertyType=mitula_studio_apartment"
    "&text=Bogot%C3%A1"
)

s3_client = boto3.client("s3")


def fetch_html(page):
    """Descarga el HTML de una página específica."""
    url = f"{BASE_URL}/pag-{page}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def save_to_s3(content):
    """Guarda el contenido HTML en S3."""
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    s3_path = f"{today}.html"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_path,
        Body=content.encode("utf-8"),
        ContentType="text/html"
    )
    return f"s3://{BUCKET_NAME}/{s3_path}"


def app(event, context):
    full_html = ""
    for page in range(1, 11):
        try:
            full_html += fetch_html(page) + "\n\n"
        except requests.RequestException as e:
            print(f"Error descargando página {page}: {e}")

    s3_path = save_to_s3(full_html)
    return {"statusCode": 200, "body": f"Archivo guardado en {s3_path}"}
