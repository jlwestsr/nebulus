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

    // Fetch data in parallel
    Promise.all([
        fetch('/api/history').then(res => res.json()),
        fetch('/me').then(res => res.json())
    ]).then(([history, user]) => {
        renderSidebar(history, user);
    }).catch(err => {
        console.error("Failed to load sidebar data", err);
        // Fallback or empty state
        renderSidebar([], { full_name: "Guest", username: "guest" });
    });

    function renderSidebar(history, user) {
        // Group history by folders (logic to be improved later, flat for now or "Recent")
        let recentChatsHTML = history.map(chat => `
            <a class="nav-item sub-item" href="/?chat_id=${chat.id}">
                <span class="nav-label">${chat.title}</span>
            </a>
        `).join('');

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

                <div class="nav-item" onclick="window.openSearchModal(event)">
                    <div class="nav-icon">🔍</div>
                    <span class="nav-label">Search</span>
                </div>

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
                    Recent Chats
                </div>
                <div class="scroll-area">
                    ${recentChatsHTML || '<div style="padding: 10px; color: #555; font-size: 0.8rem;" class="nav-label">No recent chats</div>'}
                </div>

                 <div class="user-profile">
                    <div class="user-avatar">${getInitials(user.full_name || user.username)}</div>
                    <span class="nav-label">${user.full_name || user.username}</span>
                </div>
            </div>
        `;

        const sidebarContainer = document.createElement('div');
        sidebarContainer.innerHTML = sidebarHTML;
        document.body.prepend(sidebarContainer.firstElementChild);

        setupSidebarEvents();
    }

    function getInitials(name) {
        return name.match(/(\b\S)?/g).join("").match(/(^\S|\S$)?/g).join("").toUpperCase();
    }

    function setupSidebarEvents() {
        // Initial state check (optional usage of localStorage)
        const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        if (isCollapsed) {
            document.body.classList.add('sidebar-collapsed');
        }

        // Toggle Logic
        const toggleBtn = document.getElementById('sidebar-toggle');
        if (toggleBtn) {
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
        }
    }

    //    injectDashboard();

    //    injectDashboard();

    let cachedModels = [];

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

                cachedModels = models; // Cache for observer
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
        // Use cache if no args provided (e.g. from observer)
        if (!models) models = cachedModels;

        // If still no models (fetch hasn't returned yet), do nothing.
        // The fetch callback will call us later.
        if (!models || models.length === 0) return;

        if (document.getElementById('model-selector-container')) return;

        const container = document.createElement('div');
        container.id = 'model-selector-container';

        const select = document.createElement('select');
        select.id = 'model-selector';

        // Add options
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.text = model;
            select.appendChild(option);
        });

        // Handle change
        select.addEventListener('change', (e) => {
            const newModel = e.target.value;

            // Backend Update via API (No page refresh, no chat clutter)
            fetch('/api/model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: newModel })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        showToast(`Switched to ${newModel}`);

                        // Update source of truth so Observer doesn't revert it
                        const hiddenDiv = document.getElementById('model-data');
                        if (hiddenDiv) {
                            hiddenDiv.setAttribute('data-model', newModel);
                            hiddenDiv.setAttribute('data-shown', 'true'); // Prevent toast duplicate
                        }
                    } else {
                        console.error("Model switch failed", data);
                        showToast("Failed to switch model");
                    }
                })
                .catch(err => {
                    console.error("Model switch error", err);
                    showToast("Error switching model");
                });
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

    // Search Logic
    window.openSearchModal = function (e) {
        console.log("Opening Search Modal");
        if (e) e.preventDefault();
        injectSearchModal(); // Ensure it exists
        const overlay = document.getElementById('search-modal-overlay');
        overlay.classList.add('open');
        document.getElementById('search-input').focus();
    };

    function injectSearchModal() {
        if (document.getElementById('search-modal-overlay')) return;

        const modalHTML = `
            <div id="search-modal-overlay">
                <div id="search-modal">
                    <div class="search-header">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7d8590" stroke-width="2" style="margin-right: 10px;">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                        <input type="text" id="search-input" placeholder="Search chats..." autocomplete="off">
                    </div>
                    <div class="search-results" id="search-results">
                        <div style="text-align:center; padding: 20px; color: #555;">Type to search...</div>
                    </div>
                </div>
            </div>
        `;
        const div = document.createElement('div');
        div.innerHTML = modalHTML;
        document.body.appendChild(div.firstElementChild);

        // Bind events
        const overlay = document.getElementById('search-modal-overlay');
        const input = document.getElementById('search-input');

        // Close on background click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('open');
            }
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && overlay.classList.contains('open')) {
                overlay.classList.remove('open');
            }
        });

        // Debounced Search
        let timeout;
        input.addEventListener('input', (e) => {
            clearTimeout(timeout);
            const val = e.target.value;
            if (val.length < 2) {
                document.getElementById('search-results').innerHTML = '<div style="text-align:center; padding: 20px; color: #555;">Type to search...</div>';
                return;
            }
            timeout = setTimeout(() => performSearch(val), 300);
        });
    }

    function performSearch(query) {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = '<div style="text-align:center; padding: 20px; color: #7d8590;">Searching...</div>';

        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                if (!data || data.length === 0) {
                    resultsContainer.innerHTML = '<div style="text-align:center; padding: 20px; color: #7d8590;">No results found.</div>';
                    return;
                }
                renderSearchResults(data);
            })
            .catch(err => {
                console.error("Search failed", err);
                resultsContainer.innerHTML = '<div style="text-align:center; padding: 20px; color: #fa3860;">Search failed.</div>';
            });
    }

    function renderSearchResults(results) {
        const container = document.getElementById('search-results');
        container.innerHTML = results.map(item => `
            <div class="search-result-item" onclick="window.location.href='/?chat_id=${item.chat_id}'">
                <div class="result-title">${item.title}</div>
                <div class="result-snippet">${escapeHtml(item.snippet)}</div>
                <div class="result-meta">${new Date(item.created_at).toLocaleDateString()}</div>
            </div>
        `).join('');
    }

    function escapeHtml(text) {
        if (!text) return "";
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}
