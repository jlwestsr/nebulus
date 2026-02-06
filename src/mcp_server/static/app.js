document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('task-table-body');
    const modal = document.getElementById('modal');
    const addBtn = document.getElementById('add-task-btn');
    const closeBtn = document.getElementById('close-modal');
    const form = document.getElementById('add-task-form');

    // Load Tasks
    fetchTasks();

    function fetchTasks() {
        fetch('/api/tasks')
            .then(res => res.json())
            .then(tasks => renderTasks(tasks))
            .catch(err => console.error('Error fetching tasks:', err));
    }

    function renderTasks(tasks) {
        tableBody.innerHTML = '';
        if (tasks.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="empty">No scheduled tasks found.</td></tr>';
            return;
        }

        tasks.forEach(task => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${task.title}</strong><br><small>${task.prompt.substring(0, 40)}...</small></td>
                <td><code>${task.schedule}</code></td>
                <td>${formatDate(task.next_run)}</td>
                <td>${task.recipients.join(', ')}</td>
                <td>
                    <button class="btn primary sm" onclick="runTask('${task.id}')">Run</button>
                    <button class="btn danger sm" onclick="deleteTask('${task.id}')">Delete</button>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Run Task
    window.runTask = function (id) {
        fetch(`/api/tasks/${id}/run`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.error) alert(data.error);
                else alert(data.message);
            });
    };

    // Add Task
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = document.getElementById('title').value;
        const prompt = document.getElementById('prompt').value;
        const schedule = document.getElementById('schedule').value;
        const recipientsStr = document.getElementById('recipients').value;
        const recipients = recipientsStr.split(',').map(e => e.trim()).filter(e => e);

        fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, prompt, schedule, recipients })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    modal.classList.add('hidden');
                    form.reset();
                    fetchTasks();
                }
            });
    });

    // Delete Task
    window.deleteTask = function (id) {
        if (!confirm('Are you sure you want to delete this task?')) return;

        fetch(`/api/tasks/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(() => fetchTasks());
    };

    // Modal Logic
    addBtn.onclick = () => modal.classList.remove('hidden');
    closeBtn.onclick = () => modal.classList.add('hidden');
    window.onclick = (e) => {
        if (e.target == modal) modal.classList.add('hidden');
    };

    function formatDate(dateStr) {
        if (!dateStr || dateStr === 'None') return 'Not Scheduled';
        return new Date(dateStr).toLocaleString();
    }
});
