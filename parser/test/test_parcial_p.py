from unittest.mock import patch, MagicMock
import parser.parcial_p as parcial_p


@patch("parser.parcial_p.s3_client.get_object")
def test_app(mock_get_object):
    """Prueba para verificar la función principal cuando el HTML es válido."""
    test_html = """
    <html>
        <body>
            <div class="listing-card__information">
                <span class="listing-card__location">Chapinero</span>
                <span class="price">$500,000,000</span>
                <span class="bedrooms">3 Habitaciones</span>
                <span class="bathrooms">2 Baños</span>
                <span class="area">80 m²</span>
            </div>
        </body>
    </html>
    """

    mock_get_object.return_value = {
        "Body": MagicMock(read=lambda: test_html.encode("utf-8"))
    }

    response = parcial_p.app({}, {})
    assert response["statusCode"] == 200
    assert "Archivo CSV guardado correctamente." in response["body"]


@patch(
    "parser.parcial_p.s3_client.put_object",
    side_effect=Exception("S3 no disponible")
)
def test_s3_error(mock_get_object):
    """Prueba para simular fallo de HTML desde S3."""
    response = parcial_p.app({}, {})
    assert response["statusCode"] == 500
    assert "Error al leer HTML de S3" in response["body"]


@patch(
    "parser.parcial_p.s3_client.put_object",
    side_effect=Exception("Error al guardar CSV")
)
@patch("parser.parcial_p.s3_client.get_object")
def test_s3_csv_save_error(mock_get_object, mock_put_object):
    """Prueba para simular un fallo al guardar el CSV en S3."""
    test_html = """
    <html>
        <body>
            <div class="listing-card__information">
                <span class="listing-card__location">Chapinero</span>
                <span class="price">$500,000,000</span>
                <span class="bedrooms">3 Habitaciones</span>
                <span class="bathrooms">2 Baños</span>
                <span class="area">80 m²</span>
            </div>
        </body>
    </html>
    """

    mock_get_object.return_value = {
        "Body": MagicMock(read=lambda: test_html.encode("utf-8"))
    }

    response = parcial_p.app({}, {})
    assert response["statusCode"] == 500
    assert "Error al guardar CSV en S3" in response["body"]
