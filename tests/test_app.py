import pytest
import time
from app.server import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_full_analysis_workflow(client):
    """
    Tests the full, asynchronous workflow from starting a task to completion.
    """
    # 1. Start the research task
    response = client.post('/start_research', json={'topic': 'test topic'})
    assert response.status_code == 200
    task_id = response.get_json()['task_id']
    assert task_id

    # 2. Poll the status endpoint until completion
    timeout = 60  # 60-second timeout to prevent infinite loops in tests
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)
        response = client.get(f'/status/{task_id}')
        status_data = response.get_json()
        status = status_data.get('status')

        if status == 'awaiting_authorization':
            # 3. Authorize the plugin if needed
            client.post(f'/authorize_plugin/{task_id}')
        elif status == 'complete':
            # 4. Verify the final report
            assert status_data['report'] is not None
            # A simple check to ensure the report is a JSON string as expected
            assert '"executive_summary"' in status_data['report']
            return # Test success

    assert False, "Test timed out before analysis completed."
