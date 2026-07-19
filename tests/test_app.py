from app import create_app


def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_endpoint():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_product_search_returns_expected_product():
    response = client().get("/products?name=Keyboard")
    assert response.status_code == 200
    assert response.get_json() == [[1, "Keyboard", 75]]


def test_search_reflects_input_for_scanner_lab():
    response = client().get("/search?q=security")
    assert response.status_code == 200
    assert b"security" in response.data

