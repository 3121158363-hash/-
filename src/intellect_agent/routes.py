# src/intellect_agent/routes.py
from flask import Blueprint, request, jsonify, current_app
from intellect_agent.tasks import run_analysis_task

main = Blueprint('main', __name__)

@main.route('/start_analysis', methods=['POST'])
def start_analysis():
    """
    Starts a new market analysis task.
    Expects a JSON payload with a 'topic' key.
    """
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    topic = data['topic']
    task = run_analysis_task.delay(topic)

    return jsonify({"task_id": task.id}), 202

@main.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """
    Retrieves the status and result of a running task.
    """
    task = run_analysis_task.AsyncResult(task_id)

    response = {
        'state': task.state,
        'info': task.info,
    }

    # If the task is finished, include the final result
    if task.state == 'SUCCESS':
        response['result'] = task.result

    return jsonify(response)
