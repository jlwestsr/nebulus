document.addEventListener('DOMContentLoaded', () => {
    // Wait for body to be ready
    injectSidebar();
});

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

    injectDashboard();

    // Observer to hide dashboard when messages appear
    const observer = new MutationObserver((mutations) => {
        const messageList = document.querySelector('.step');
        if (messageList) {
            const dashboard = document.getElementById('nebulus-dashboard');
            if (dashboard) dashboard.style.display = 'none';
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
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

window.setInput = function (text) {
    const textarea = document.querySelector('textarea');
    if (textarea) {
        textarea.value = text;
        textarea.focus();
        // Trigger generic input event if needed by frameworks
        textarea.dispatchEvent(new Event('input', { bubbles: true }));

        // Optional: auto-send
        // const sendBtn = document.querySelector('button[aria-label="Send message"]');
        // if(sendBtn) sendBtn.click();
    }
}
