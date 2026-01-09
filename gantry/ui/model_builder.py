MODEL_BUILDER_HTML = """
<div id="model-builder-modal" class="modal" style="display: none;">
    <div class="modal-content card">
        <div class="card-header">
            <h2>Build Custom Model</h2>
            <button id="close-builder-btn" class="icon-btn">&times;</button>
        </div>
        <div class="card-body">
            <form id="model-builder-form">
                <div class="form-group">
                    <label for="builder-name">Model Name</label>
                    <input type="text" id="builder-name" placeholder="e.g. pirate-bot" required />
                </div>
                <div class="form-group">
                    <label for="builder-base">Base Model</label>
                    <select id="builder-base" required>
                        <!-- Injected by JS -->
                        <option value="">Loading models...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="builder-system">System Prompt</label>
                    <textarea id="builder-system" placeholder="You are a helpful assistant..." rows="4"></textarea>
                </div>
                <div class="form-group">
                    <label>Parameters (Optional)</label>
                    <div class="param-row">
                        <span>Temperature</span>
                        <input type="number" id="builder-temp" step="0.1" min="0" max="2" value="0.7" />
                    </div>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary" id="create-model-btn">Create Model</button>
                </div>
            </form>
            <div id="builder-status" class="status-msg" style="display:none;"></div>
        </div>
    </div>
</div>
"""

MODEL_BUILDER_CSS = """
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}
.modal-content {
    width: 90%;
    max-width: 500px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
}
.form-group {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.form-group input, .form-group select, .form-group textarea {
    padding: 10px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
}
.param-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.param-row input {
    width: 80px;
}
.status-msg {
    margin-top: 15px;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
}
.status-msg.success { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.status-msg.error { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
"""
