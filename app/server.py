from flask import Flask, request, jsonify, render_template
from multiprocessing import Process, Manager
import uuid
import json
from .agent import IntellectAgent

app = Flask(__name__)

# Use a multiprocessing Manager to create a shared dictionary for tasks
manager = Manager()
tasks = manager.dict()

def run_agent_in_background(task_id, topic, tasks_dict):
    """
    This function runs in a separate process, consumes the agent's generator,
    and updates the shared tasks dictionary.
    """
    agent = IntellectAgent(topic)
    tasks_dict[task_id] = {
        'status': 'starting',
        'report': None,
        'authorization_needed': False
    }

    for update in agent.run_analysis():
        task = tasks_dict[task_id] # Get the latest version of the task
        if update.startswith("status:"):
            task['status'] = update.replace("status: ", "")
        elif update.startswith("authorization_required:"):
            task['authorization_needed'] = True
            task['status'] = "awaiting_authorization"
            tasks_dict[task_id] = task # Update the dict
            # Pause until authorized by the main process
            while task.get('authorization_needed'):
                pass # This is a simple spin-lock; a real app might use an Event
            # After authorization, the main process will have updated the dict
            task = tasks_dict[task_id] # Re-fetch the task state
        elif update.startswith("final_update:"):
            final_data = json.loads(update.replace("final_update: ", ""))
            task['report'] = final_data['report']
            task['status'] = final_data['status']
        tasks_dict[task_id] = task # Update the dict after each change

    task = tasks_dict[task_id]
    task['status'] = 'complete'
    tasks_dict[task_id] = task


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

    # Spawn a new process to run the agent's analysis
    process = Process(target=run_agent_in_background, args=(task_id, topic, tasks))
    process.start()

    return jsonify({"task_id": task_id})

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = tasks.get(task_id)
    if not task:
        # It might take a moment for the task to be created in the background process
        return jsonify({"status": "initializing"}), 202

    return jsonify({
        "task_id": task_id,
        "status": task.get('status'),
        "report": task.get('report')
    })

@app.route('/authorize_plugin/<task_id>', methods=['POST'])
def authorize_plugin(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task.get('authorization_needed'):
        # Update the shared dictionary to un-pause the background process
        task['authorization_needed'] = False
        task['status'] = 'resuming'
        tasks[task_id] = task
        return jsonify({"message": "Plugin authorized. Resuming analysis."})
    else:
        return jsonify({"message": "Plugin authorization not currently required."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
