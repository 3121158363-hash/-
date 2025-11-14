# src/intellect_agent/tasks.py
from celery import Celery, Task
from celery.signals import worker_ready
import logging
from intellect_agent.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Configure Celery
celery_app = Celery(
    'tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_track_started=True,
)

class AnalysisTask(Task):
    """A Celery Task that provides progress updates."""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.error(f'{task_id} failed: {exc}')

@celery_app.task(bind=True, base=AnalysisTask)
def run_analysis_task(self, topic):
    """
    The background task that runs the IntellectAgent analysis.
    Updates its state with progress reports from the agent.
    """
    from intellect_agent.agent import IntellectAgent
    agent = IntellectAgent(topic)
    final_report = None

    for update in agent.run_analysis():
        if update.startswith('status:'):
            # Report progress
            self.update_state(state='PROGRESS', meta={'status': update})
        elif update.startswith('final_update:'):
            # Capture the final report
            final_data_json = update.replace('final_update:', '', 1)
            final_report = final_data_json # The result is the final report string

    return final_report
