document.addEventListener('DOMContentLoaded', () => {
    loadModels();
    loadTools();
    loadKnowledge();

    // Event Listeners
    document.getElementById('refresh-models-btn').addEventListener('click', loadModels);
    document.getElementById('pull-model-btn').addEventListener('click', pullModel);
});

async function loadModels() {
    const list = document.getElementById('model-list');
    list.innerHTML = '<div class="spinner">Loading models...</div>';

    try {
        const response = await fetch('/api/workspace/models');
        const data = await response.json();

        if (data.models && data.models.length > 0) {
            list.innerHTML = '';
            data.models.forEach(model => {
                const item = document.createElement('div');
                item.className = 'list-item';

                // Parse size to GB
                const sizeGB = (model.size / (1024 * 1024 * 1024)).toFixed(2);

                item.innerHTML = `
                    <div class="list-item-content">
                        <span class="item-title">${model.name}</span>
                        <span class="item-meta">${sizeGB} GB • ${model.details?.family || 'Unknown'}</span>
                    </div>
                    <button class="icon-btn delete-model-btn" data-name="${model.name}" title="Delete">🗑️</button>
                `;
                list.appendChild(item);
            });

            // Attach delete handlers
            document.querySelectorAll('.delete-model-btn').forEach(btn => {
                btn.addEventListener('click', (e) => deleteModel(e.target.dataset.name));
            });
        } else {
            list.innerHTML = '<div style="padding:10px; color:var(--text-secondary)">No models found. Pull one!</div>';
        }
    } catch (e) {
        list.innerHTML = `<div style="color:var(--danger)">Error loading models: ${e.message}</div>`;
    }
}

async function pullModel() {
    const input = document.getElementById('pull-model-input');
    const name = input.value.trim();
    if (!name) return;

    const btn = document.getElementById('pull-model-btn');
    const originalText = btn.innerText;
    btn.innerText = 'Pulling...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/workspace/models/pull', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        });

        const data = await response.json();

        if (response.ok) {
            alert(`Model ${name} pull triggered successfully!`);
            input.value = '';
            // Refresh list after a delay (since pull is async/background in reality, but here we waited)
            loadModels();
        } else {
            alert(`Error pulling model: ${data.error}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

async function deleteModel(name) {
    if (!confirm(`Are you sure you want to delete ${name}?`)) return;

    try {
        const response = await fetch(`/api/workspace/models/${name}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadModels();
        } else {
            const data = await response.json();
            alert(`Error deleting model: ${data.error}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

async function loadTools() {
    const list = document.getElementById('tool-list');
    list.innerHTML = '<div class="spinner">Loading tools...</div>';

    try {
        const response = await fetch('/api/workspace/tools');
        const data = await response.json();

        if (data.tools) {
            list.innerHTML = '';
            data.tools.forEach(tool => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                     <div class="list-item-content">
                        <span class="item-title">${tool.name}</span>
                        <span class="item-meta">${tool.description}</span>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" ${tool.enabled ? 'checked' : ''} disabled>
                        <span class="slider round"></span>
                    </label>
                `;
                list.appendChild(item);
            });
        }
    } catch (e) {
        list.innerHTML = `<div style="color:var(--danger)">Error loading tools: ${e.message}</div>`;
    }
}

async function loadKnowledge() {
    const list = document.getElementById('knowledge-list');
    list.innerHTML = '<div class="spinner">Loading knowledge...</div>';

    try {
        const response = await fetch('/api/workspace/knowledge');
        const data = await response.json();

        if (data.collections) {
            list.innerHTML = '';
            data.collections.forEach(col => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                     <div class="list-item-content">
                        <span class="item-title">${col.name}</span>
                        <span class="item-meta">${col.count} documents</span>
                    </div>
                    <span class="status-badge ${col.status}">${col.status}</span>
                `;
                list.appendChild(item);
            });
        }
    } catch (e) {
        list.innerHTML = `<div style="color:var(--danger)">Error loading knowledge: ${e.message}</div>`;
    }
}
