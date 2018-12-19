from test.unit import client


def test_api_key_missing(client):
    response = client.get('/location/ping')  # Missing API Key
    assert response.status_code == 401
