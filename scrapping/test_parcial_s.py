import pytest
import requests
from parcial_s import fetch_html, save_to_s3
from unittest.mock import patch, MagicMock

# Prueba 1: Mockear requests.get() para probar fetch_html()
@patch("parcial_s.requests.get")
def test_fetch_html(mock_get):
    # Configurar la respuesta simulada
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Prueba</body></html>"
    mock_get.return_value = mock_response

    # Llamar a la función
    html = fetch_html(1)

    # Validar que se hizo la petición correcta
    mock_get.assert_called_once_with(
        "https://casas.mitula.com.co/find?operationType=sell&propertyType=mitula_studio_apartment&text=Bogot%C3%A1/pag-1",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )
    
    # Validar que el HTML retornado es el esperado
    assert html == "<html><body>Prueba</body></html>"

# Prueba 2: Simular error en fetch_html()
@patch("parcial_s.requests.get")
def test_fetch_html_error(mock_get):
    # Simular un error de conexión
    mock_get.side_effect = requests.RequestException("Error de conexión")

    # Verificar que la excepción se lanza correctamente
    with pytest.raises(requests.RequestException):
        fetch_html(1)

# Prueba 3: Mockear boto3 para probar save_to_s3()
@patch("parcial_s.s3_client.put_object")
def test_save_to_s3(mock_put_object):
    # Simular una respuesta exitosa de AWS S3
    mock_put_object.return_value = {}

    content = "<html><body>Datos de prueba</body></html>"
    path = save_to_s3(content)

    # Verificar que la función genera una ruta válida
    assert "s3://zappa-scrapping/" in path

    # Verificar que put_object se llamó correctamente
    mock_put_object.assert_called_once()
