from flask import Flask, request, jsonify, render_template
from .celery_worker import run_analysis_task

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_research', methods=['POST'])
def start_research():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "Topic not provided"}), 400

    topic = data['topic']
    # Submit the task to the Celery queue
    task = run_analysis_task.delay(topic)

    return jsonify({"task_id": task.id})

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    # Query Celery for the task's status
    task = run_analysis_task.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {'status': 'pending'}
    elif task.state == 'PROGRESS':
        response = {'status': task.info.get('status')}
    elif task.state == 'SUCCESS':
        response = {'status': 'complete', 'report': task.info.get('report')}
    else:
        response = {'status': task.state}

    return jsonify(response)

# The authorization endpoint needs a more complex implementation in a Celery
# architecture (e.g., using a database or another messaging system).
# For now, this will be a non-functional placeholder.
@app.route('/authorize_plugin/<task_id>', methods=['POST'])
def authorize_plugin(task_id):
    return jsonify({"message": "Authorization in a distributed system requires a more complex setup. This is a placeholder."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
