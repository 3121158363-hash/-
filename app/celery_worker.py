from celery import Celery
from app.agent import IntellectAgent
import json

# Configure Celery
celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery_app.task(bind=True)
def run_analysis_task(self, topic):
    """
    This is the background task that will be executed by a Celery worker.
    """
    agent = IntellectAgent(topic)

    # We will use Celery's state update mechanism to report progress
    for update in agent.run_analysis():
        if update.startswith("status:"):
            self.update_state(state='PROGRESS', meta={'status': update.replace("status: ", "")})
        elif update.startswith("authorization_required:"):
            # In a real system, you'd need a more complex mechanism to handle this.
            # For now, we'll just log it and move on.
            self.update_state(state='PENDING_AUTH', meta={'status': 'Awaiting Authorization'})
            # This will require manual intervention in this simplified architecture.
        elif update.startswith("final_update:"):
            final_data = json.loads(update.replace("final_update: ", ""))
            return {'status': 'SUCCESS', 'report': final_data['report']}

    return {'status': 'COMPLETE', 'report': agent.report}
