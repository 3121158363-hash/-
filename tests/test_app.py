import pytest
from app.server import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_start_research(client):
    """Test starting a research task."""
    response = client.post('/start_research', json={'topic': 'test topic'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'task_id' in json_data
