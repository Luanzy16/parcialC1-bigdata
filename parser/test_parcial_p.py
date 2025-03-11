import pytest
import boto3
import csv
from io import StringIO
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from datetime import datetime
from parcial_p import app  # Importamos la función desde parcial_p.py

# Obtener la fecha del día en que se ejecuta la prueba
HOY = datetime.today().strftime("%Y-%m-%d")
S3_KEY = f"{HOY}.html"

# HTML de prueba simulado
TEST_HTML = """
<html>
<body>
    <div class="listing-card__information">
        <div class="listing-card__location__geo">Chapinero</div>
        <span data-test="price__actual">$500,000,000</span>
        <p data-test="bedrooms">3 Habitaciones</p>
        <p data-test="bathrooms">2 Baños</p>
        <p data-test="floor-area">80 m²</p>
    </div>
</body>
</html>
"""

# Prueba 1: Mockear la descarga de HTML desde S3
@patch("parcial_p.s3_client.get_object")
def test_download_html(mock_get_object):
    mock_response = MagicMock()
    mock_response["Body"].read.return_value = TEST_HTML.encode("utf-8")
    mock_get_object.return_value = mock_response

    event = {}
    context = {}

    response = app(event, context)
    
    assert response["statusCode"] == 200
    assert "CSV guardado en s3://" in response["body"]

    mock_get_object.assert_called_once_with(Bucket="zappa-scrapping", Key=S3_KEY)  # Se usa la fecha dinámica



# Prueba 2: Simular fallo al descargar HTML de S3
@patch("parcial_p.s3_client.get_object", side_effect=Exception("S3 no disponible"))
def test_download_html_fail(mock_get_object):
    event = {}
    context = {}

    response = app(event, context)

    assert response["statusCode"] == 500
    assert "Error al leer HTML de S3" in response["body"]


# Prueba 3: Simular subida de CSV a S3
@patch("parcial_p.s3_client.put_object")
@patch("parcial_p.s3_client.get_object", return_value={"Body": MagicMock(read=lambda: TEST_HTML.encode("utf-8"))})
def test_upload_csv(mock_get_object, mock_put_object):
    event = {}
    context = {}

    response = app(event, context)

    assert response["statusCode"] == 200
    assert "CSV guardado en s3://" in response["body"]

    mock_put_object.assert_called_once()
