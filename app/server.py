from flask import Flask, request, jsonify, render_template
from threading import Thread
import uuid
import json
from .agent import IntellectAgent

app = Flask(__name__)

# In-memory storage for running tasks. A real application would use a database.
tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_research', methods=['POST'])
def start_research():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "Topic not provided"}), 400

    topic = data['topic']
    task_id = str(uuid.uuid4())

    agent = IntellectAgent(topic)
    tasks[task_id] = {
        'agent': agent,
        'generator': agent.run_analysis(),
        'status': 'starting',
        'report': None,
        'authorization_needed': False
    }

    # We don't run the agent here directly to avoid blocking.
    # The frontend will poll the status endpoint to drive the process.

    return jsonify({"task_id": task_id})

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # If authorization is needed, we wait until the user authorizes.
    if task['authorization_needed']:
        return jsonify({
            "task_id": task_id,
            "status": "awaiting_authorization",
            "message": "Public Opinion Miner Plugin required."
        })

    try:
        update = next(task['generator'])
        if update.startswith("status:"):
            task['status'] = update.replace("status: ", "")
        elif update.startswith("authorization_required:"):
            task['authorization_needed'] = True
            task['status'] = "awaiting_authorization"
        elif update.startswith("final_update:"):
            final_data = json.loads(update.replace("final_update: ", ""))
            task['report'] = final_data['report']
            task['status'] = final_data['status']

    except StopIteration:
        task['status'] = 'complete'

    return jsonify({
        "task_id": task_id,
        "status": task['status'],
        "report": task.get('report')
    })

@app.route('/authorize_plugin/<task_id>', methods=['POST'])
def authorize_plugin(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task['authorization_needed']:
        task['authorization_needed'] = False
        task['status'] = 'resuming'
        return jsonify({"message": "Plugin authorized. Resuming analysis."})
    else:
        return jsonify({"message": "Plugin authorization not currently required."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
