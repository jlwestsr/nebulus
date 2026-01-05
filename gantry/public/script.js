function initNebulus() {
    injectSidebar();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNebulus);
} else {
    initNebulus();
}

function injectSidebar() {
    if (document.getElementById('nebulus-sidebar')) return;

    const sidebarHTML = `
        <div id="nebulus-sidebar">
            <div class="sidebar-header">
                <!-- <div class="logo-icon">OI</div> -->
                <div class="logo-text" style="font-size: 1.2rem; margin-left: 10px;">Nebulus</div>
                <div class="toggle-btn" id="sidebar-toggle">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M19 12H5M12 19l-7-7 7-7"/>
                    </svg>
                </div>
            </div>

            <div class="new-chat-btn" onclick="window.location.href='/'">
                <div class="nav-icon">+</div>
                <span>New Chat</span>
            </div>

            <a class="nav-item" href="/">
                <div class="nav-icon">🔍</div>
                <span class="nav-label">Search</span>
            </a>

             <a class="nav-item" href="/notes">
                <div class="nav-icon">📝</div>
                <span class="nav-label">Notes</span>
            </a>

            <a class="nav-item" href="/workspace">
                <div class="nav-icon">❖</div>
                <span class="nav-label">Workspace</span>
            </a>

            <div class="divider"></div>

            <div style="padding: 10px; color: #7d8590; font-size: 0.8rem;" class="nav-label">
                Folders
            </div>
             <div style="padding: 10px; color: #7d8590; font-size: 0.8rem;" class="nav-label">
                Chats
            </div>

             <div class="user-profile">
                <div class="user-avatar">JW</div>
                <span class="nav-label">Jason L West</span>
            </div>
        </div>
    `;

    const sidebarContainer = document.createElement('div');
    sidebarContainer.innerHTML = sidebarHTML;
    document.body.prepend(sidebarContainer.firstElementChild);

    // Initial state check (optional usage of localStorage)
    const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (isCollapsed) {
        document.body.classList.add('sidebar-collapsed');
    }

    // Toggle Logic
    const toggleBtn = document.getElementById('sidebar-toggle');
    toggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('sidebar-collapsed');
        const collapsed = document.body.classList.contains('sidebar-collapsed');
        localStorage.setItem('sidebar-collapsed', collapsed);

        // Update toggle icon rotation
        if (collapsed) {
            toggleBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`;
        } else {
            toggleBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>`;
        }
    });

    //    injectDashboard();

    //    injectDashboard();

    // Fetch models from API for the dropdown
    fetch('/models')
        .then(response => response.json())
        .then(data => {
            if (data.models) {
                let models = data.models;
                // Get current model from the injected div to prioritize it
                const modelData = document.getElementById('model-data');
                const currentModel = modelData ? modelData.dataset.model : null;

                if (currentModel) {
                    // Move current model to the start of the array
                    models = [currentModel, ...models.filter(m => m !== currentModel)];
                } else {
                    // Fallback sort (optional, but good for consistency)
                    models.sort();
                }

                injectModelDropdown(models);
            }
        })
        .catch(err => console.error('Error fetching models:', err));


    // Toast Notification Helper
    function showToast(message) {
        let toast = document.getElementById('model-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'model-toast';
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.className = 'show';
        setTimeout(function () {
            toast.className = toast.className.replace('show', '');
        }, 3000);
    }

    const observer = new MutationObserver(() => {
        const hiddenDiv = document.getElementById('model-data');
        if (hiddenDiv) {
            const modelName = hiddenDiv.getAttribute('data-model');
            if (modelName) {
                // Update dropdown if needed (existing logic)
                const select = document.getElementById('model-selector');
                if (select && select.value !== modelName) {
                    select.value = modelName;

                    // Reorder options to put current at top
                    const options = Array.from(select.options);
                    const currentOpt = options.find(o => o.value === modelName);
                    if (currentOpt) {
                        currentOpt.remove();
                        select.prepend(currentOpt);
                        select.selectedIndex = 0;
                    }
                }

                // Show Toast Alert only if it's a new switch or we want to confirm
                // We use a small debounce or check to avoid spamming on page load
                if (hiddenDiv.getAttribute('data-shown') !== 'true') {
                    showToast(`Model switched to ${modelName}`);
                    hiddenDiv.setAttribute('data-shown', 'true');
                }
            }
        }

        // Ensure the model selector is injected if missing
        injectModelDropdown();
        // Ensure sidebar is injected if missing (e.g. after React hydration)
        injectSidebar();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    function updateModelDropdown(currentModel) {
        const select = document.getElementById('model-selector');
        if (select) {
            select.value = currentModel;
        }
    }

    function injectModelDropdown(models) {
        if (document.getElementById('model-selector-container')) return;

        const container = document.createElement('div');
        container.id = 'model-selector-container';

        const select = document.createElement('select');
        select.id = 'model-selector';

        // Add options
        if (Array.isArray(models)) {
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.text = model;
                select.appendChild(option);
            });
        }

        // Handle change
        select.addEventListener('change', (e) => {
            const newModel = e.target.value;
            const textarea = document.querySelector('textarea');
            if (textarea) {
                // Send command hiddenly if possible, or just type it
                window.setInput(`/model ${newModel}`);

                // Try to trigger send (Chainlit specific)
                setTimeout(() => {
                    // Use robust ID selector found via inspection
                    const sendBtn = document.getElementById('chat-submit');
                    if (sendBtn) {
                        sendBtn.click();
                    } else {
                        // Fallback just in case
                        const fallback = document.querySelector('button[aria-label="Send message"]');
                        if (fallback) fallback.click();
                    }
                }, 100);
            }
        });

        container.appendChild(select);
        document.body.appendChild(container);

        // Set initial value if we have a data attribute somewhere or just default
        const modelData = document.getElementById('model-data');
        if (modelData && modelData.dataset.model) {
            select.value = modelData.dataset.model;
        }
    }

    function injectDashboard() {
        // Basic check if we are in an empty chat (Chainlit usually puts a welcome screen or empty lists)
        // We will blindly inject and hide if we later detect messages
        if (document.getElementById('nebulus-dashboard')) return;

        const dashboardHTML = `
        <div id="nebulus-dashboard">
            <div class="dashboard-content">
                <div class="dashboard-logo">OI</div> <!-- Using text for now as in sidebar -->
                <div class="dashboard-greeting">How can I help you today?</div>

                <div class="suggestions-grid">
                    <div class="suggestion-card" onclick="setInput('Tell me a fun fact about the Roman Empire')">
                        <div class="suggestion-title">Tell me a fun fact</div>
                        <div class="suggestion-desc">about the Roman Empire</div>
                    </div>
                    <div class="suggestion-card" onclick="setInput('Help me study vocabulary for a college entrance exam')">
                        <div class="suggestion-title">Help me study</div>
                        <div class="suggestion-desc">vocabulary for a college entrance exam</div>
                    </div>
                     <div class="suggestion-card" onclick="setInput('Show me a code snippet of a website header')">
                        <div class="suggestion-title">Show me a code snippet</div>
                        <div class="suggestion-desc">of a website sticky header</div>
                    </div>
                </div>
            </div>
        </div>
    `;

        // Try to find the chat container. In Chainlit, it's often dynamic.
        // We'll append to body and use fixed centering for now, z-index high but below sidebar
        const dashboardContainer = document.createElement('div');
        dashboardContainer.innerHTML = dashboardHTML;
        document.body.appendChild(dashboardContainer.firstElementChild);
    }

    // Helper to set React input value robustly
    window.setInput = function (text) {
        const textarea = document.querySelector('#chat-input, textarea');
        if (textarea) {
            // Native setter for React
            const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            nativeTextAreaValueSetter.call(textarea, text);

            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            textarea.focus();

            // Try to trigger send via Enter key first (most reliable for Chat inputs)
            setTimeout(() => {
                const event = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    which: 13,
                    keyCode: 13,
                    bubbles: true,
                    cancelable: true
                });
                textarea.dispatchEvent(event);

                // Fallback click if text remains (simple check)
                setTimeout(() => {
                    if (textarea.value === text) {
                        const sendBtn = document.getElementById('chat-submit');
                        if (sendBtn) sendBtn.click();
                    }
                }, 200);
            }, 100);
        }
    }
}
