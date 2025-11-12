document.addEventListener('DOMContentLoaded', () => {
    const topicInput = document.getElementById('topic-input');
    const startResearchBtn = document.getElementById('start-research-btn');
    const researchFeed = document.getElementById('research-feed');

    const authModal = document.getElementById('auth-modal');
    const authorizeBtn = document.getElementById('authorize-btn');
    const denyBtn = document.getElementById('deny-btn');

    let currentTaskForAuth = null;

    const API = {
        startResearch: (topic) => {
            return fetch('/start_research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            }).then(res => res.json());
        },
        getStatus: (taskId) => {
            return fetch(`/status/${taskId}`).then(res => res.json());
        },
        authorizePlugin: (taskId) => {
            return fetch(`/authorize_plugin/${taskId}`, { method: 'POST' }).then(res => res.json());
        }
    };

    const pollStatus = (taskId, card) => {
        const interval = setInterval(async () => {
            const data = await API.getStatus(taskId);
            updateCard(card, data);

            if (data.status === 'awaiting_authorization') {
                currentTaskForAuth = taskId;
                authModal.style.display = 'flex';
                clearInterval(interval);
            } else if (data.status === 'complete') {
                clearInterval(interval);
            }
        }, 3000);
    };

    const createCard = (topic, taskId) => {
        const card = document.createElement('div');
        card.className = 'research-card';
        card.dataset.taskId = taskId;
        card.innerHTML = `
            <div class="card-header">
                <h2>${topic}</h2>
            </div>
            <div class="card-body">
                <div class="status-section">
                    <strong>Status:</strong> <span class="status-badge running">Initializing...</span>
                </div>
                <div class="report-section" style="display: none;">
                    <h3>Final Report</h3>
                    <pre></pre>
                </div>
            </div>
        `;
        researchFeed.prepend(card);
        return card;
    };

    const updateCard = (card, data) => {
        const statusBadge = card.querySelector('.status-badge');
        statusBadge.textContent = data.status.replace(/_/g, ' ');

        if (data.status === 'awaiting_authorization') {
            statusBadge.className = 'status-badge auth-needed';
        } else if (data.status === 'complete') {
            statusBadge.className = 'status-badge complete';
            const reportSection = card.querySelector('.report-section');
            reportSection.style.display = 'block';
            card.querySelector('pre').textContent = JSON.stringify(data.report, null, 2);
        } else {
            statusBadge.className = 'status-badge running';
        }
    };

    startResearchBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        if (!topic) {
            alert('Please enter a topic.');
            return;
        }

        const data = await API.startResearch(topic);
        if (data.task_id) {
            const card = createCard(topic, data.task_id);
            pollStatus(data.task_id, card);
        } else {
            alert('Failed to start research task.');
        }
        topicInput.value = '';
    });

    authorizeBtn.addEventListener('click', async () => {
        if (currentTaskForAuth) {
            await API.authorizePlugin(currentTaskForAuth);
            const card = document.querySelector(`[data-task-id="${currentTaskForAuth}"]`);
            pollStatus(currentTaskForAuth, card); // Resume polling
            currentTaskForAuth = null;
            authModal.style.display = 'none';
        }
    });

    denyBtn.addEventListener('click', () => {
        alert("Analysis cannot proceed without authorization. The task is halted.");
        currentTaskForAuth = null;
        authModal.style.display = 'none';
    });
});
