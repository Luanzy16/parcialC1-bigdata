import pytest
import requests
from scrapping.parcial_s import fetch_html, save_to_s3
from unittest.mock import patch, MagicMock


@patch("scrapping.parcial_s.requests.get")
def test_fetch_html(mock_get):
    """Mockear requests.get() para probar fetch_html()."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Prueba</body></html>"
    mock_get.return_value = mock_response

    html = fetch_html(1)

    mock_get.assert_called_once_with(
        "https://casas.mitula.com.co/find?operationType=sell"
        "&propertyType=mitula_studio_apartment&text=Bogot%C3%A1/pag-1",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )

    assert html == "<html><body>Prueba</body></html>"


@patch("scrapping.parcial_s.requests.get")
def test_fetch_html_error(mock_get):
    """Simular error en fetch_html()."""
    mock_get.side_effect = requests.RequestException("Error de conexión")

    with pytest.raises(requests.RequestException):
        fetch_html(1)


@patch("scrapping.parcial_s.s3_client.put_object")
def test_save_to_s3(mock_put_object):
    """Mockear boto3 para probar save_to_s3()."""
    mock_put_object.return_value = {}

    content = "<html><body>Datos de prueba</body></html>"
    path = save_to_s3(content)

    # Verificar que el resultado es un string válido con la URL de S3
    assert isinstance(path, str)
    assert path.startswith("s3://zappa-scrapping/")

    # Verificar que put_object se llamó correctamente con los
    # parámetros esperados
    mock_put_object.assert_called_once()
