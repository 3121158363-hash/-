import pytest
import time
from unittest.mock import patch, MagicMock
from app.server import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('app.server.run_analysis_task')
def test_full_analysis_workflow_with_mock_celery(mock_run_analysis_task, client):
    """
    Tests the full, asynchronous workflow with a mocked Celery task.
    """
    # Arrange
    mock_task = MagicMock()
    mock_task.id = "test_task_id"
    mock_run_analysis_task.delay.return_value = mock_task

    # 1. Start the research task
    response = client.post('/start_research', json={'topic': 'test topic'})
    assert response.status_code == 200
    task_id = response.get_json()['task_id']
    assert task_id == "test_task_id"

    # 2. Simulate Celery task progression
    # To make the mock serializable, we'll patch the AsyncResult object itself
    # to return a dictionary from the .info attribute.
    with patch('app.server.run_analysis_task.AsyncResult') as mock_async_result:
        mock_instance = mock_async_result.return_value

        # Simulate PROGRESS state
        mock_instance.state = 'PROGRESS'
        mock_instance.info = {'status': 'Analyzing trends...'}
        response = client.get(f'/status/{task_id}')
        assert response.get_json()['status'] == 'Analyzing trends...'

        # Simulate SUCCESS state
        mock_instance.state = 'SUCCESS'
        mock_instance.info = {'status': 'complete', 'report': '{"executive_summary": "Test summary."}'}
        response = client.get(f'/status/{task_id}')
        assert response.get_json()['status'] == 'complete'
        assert "Test summary." in response.get_json()['report']
