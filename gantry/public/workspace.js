/**
 * Nebulus Workspace Module
 * Refactored to Nebulus.Workspace namespace
 */

if (!window.Nebulus) window.Nebulus = {};

Nebulus.Workspace = {
    init: function () {
        this.Models.load();
        this.Tools.load();
        this.Knowledge.load();
        this.bindEvents();
    },

    bindEvents: function () {
        const refreshBtn = document.getElementById('refresh-models-btn');
        const pullBtn = document.getElementById('pull-model-btn');
        const openBuilderBtn = document.getElementById('open-builder-btn');
        const closeBuilderBtn = document.getElementById('close-builder-btn');
        const builderForm = document.getElementById('model-builder-form');

        if (refreshBtn) refreshBtn.addEventListener('click', () => this.Models.load());
        if (pullBtn) pullBtn.addEventListener('click', () => this.Models.pull());

        if (openBuilderBtn) openBuilderBtn.addEventListener('click', () => this.Builder.open());
        if (closeBuilderBtn) closeBuilderBtn.addEventListener('click', () => this.Builder.close());
        if (builderForm) builderForm.addEventListener('submit', (e) => this.Builder.submit(e));
    },

    Models: {
        load: async function () {
            const list = document.getElementById('model-list');
            if (!list) return;
            list.innerHTML = '<div class="spinner">Loading models...</div>';

            try {
                const response = await fetch('/api/workspace/models');
                const data = await response.json();

                if (data.models && data.models.length > 0) {
                    list.innerHTML = '';
                    data.models.forEach(model => {
                        const item = document.createElement('div');
                        item.className = 'list-item';
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

                    // Attach Handlers
                    document.querySelectorAll('.delete-model-btn').forEach(btn => {
                        btn.addEventListener('click', (e) => this.delete(e.target.dataset.name));
                    });
                } else {
                    list.innerHTML = '<div style="padding:10px; color:var(--text-secondary)">No models found. Pull one!</div>';
                }
            } catch (e) {
                list.innerHTML = `<div style="color:var(--danger)">Error loading models: ${e.message}</div>`;
            }
        },

        pull: async function () {
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
                    this.load();
                } else {
                    alert(`Error pulling model: ${data.error}`);
                }
            } catch (e) {
                alert(`Error: ${e.message}`);
            } finally {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        },

        delete: async function (name) {
            if (!confirm(`Are you sure you want to delete ${name}?`)) return;

            try {
                const response = await fetch(`/api/workspace/models/${name}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.load();
                } else {
                    const data = await response.json();
                    alert(`Error deleting model: ${data.error}`);
                }
            } catch (e) {
                alert(`Error: ${e.message}`);
            }
        }
    },

    Tools: {
        load: async function () {
            const list = document.getElementById('tool-list');
            if (!list) return;
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
    },

    Builder: {
        open: function () {
            const modal = document.getElementById('model-builder-modal');
            if (modal) {
                modal.style.display = 'flex';
                this.populateBaseModels();
            }
        },

        close: function () {
            const modal = document.getElementById('model-builder-modal');
            if (modal) modal.style.display = 'none';
        },

        populateBaseModels: async function () {
            const select = document.getElementById('builder-base');
            if (!select) return;

            try {
                // Use the existing models endpoint (raw list)
                const response = await fetch('/models');
                const data = await response.json();

                if (data.raw) {
                    select.innerHTML = data.raw.map(m => `<option value="${m}">${m}</option>`).join('');
                } else {
                    select.innerHTML = '<option value="">Error loading models</option>';
                }
            } catch (e) {
                select.innerHTML = '<option value="">Error loading models</option>';
            }
        },

        submit: async function (e) {
            e.preventDefault();
            const btn = document.getElementById('create-model-btn');
            const status = document.getElementById('builder-status');

            const formData = {
                name: document.getElementById('builder-name').value,
                base: document.getElementById('builder-base').value,
                system: document.getElementById('builder-system').value,
                parameters: {
                    temperature: parseFloat(document.getElementById('builder-temp').value)
                }
            };

            btn.disabled = true;
            btn.innerText = 'Creating...';
            status.style.display = 'none';

            try {
                const response = await fetch('/api/models/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const result = await response.json();

                status.style.display = 'block';
                if (response.ok) {
                    status.className = 'status-msg success';
                    status.innerText = 'Model created successfully!';
                    setTimeout(() => {
                        this.close();
                        Nebulus.Workspace.Models.load();
                    }, 1500);
                } else {
                    status.className = 'status-msg error';
                    status.innerText = 'Error: ' + (result.error || 'Unknown error');
                }
            } catch (err) {
                status.style.display = 'block';
                status.className = 'status-msg error';
                status.innerText = 'Error: ' + err.message;
            } finally {
                btn.disabled = false;
                btn.innerText = 'Create Model';
            }
        }
    },

    Knowledge: {
        load: async function () {
            const list = document.getElementById('knowledge-list');
            if (!list) return;
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
    }
};

// Initialize if on workspace page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('model-list')) {
        Nebulus.Workspace.init();
    }
});
