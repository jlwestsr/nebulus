/**
 * Nebulus Gantry Client Script
 * Refactored for modularity and maintainability.
 */

const Nebulus = {
    state: {
        cachedModels: [],
        username: "Guest",
        sidebarCollapsed: localStorage.getItem('sidebar-collapsed') === 'true'
    },

    init: function () {
        // Prevent running on login page
        if (window.location.pathname === '/login') return;

        // Add active class for CSS scoping
        document.body.classList.add('nebulus-active');

        // Initialize all modules
        this.Theme.init();
        this.Sidebar.init();
        this.Search.init();

        // Chat-specific modules
        if (this.Utils.isChatPage()) {
            this.Chat.init();
            this.Models.init();
            this.Dashboard.checkAndInject();
        }

        // Global Event Observers
        this.setupObservers();
    },

    setupObservers: function () {
        let timeout;
        const observer = new MutationObserver(() => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Re-inject critical UI if lost (e.g. React hydration)
                this.Sidebar.inject();

                if (this.Utils.isChatPage()) {
                    this.Models.injectDropdown();
                    this.Dashboard.checkAndInject();
                    // Check for Model Switch data
                    this.Models.checkForSwitch();
                    // Restore missing copy buttons
                    this.Actions.ensureCopyButtons();
                    // Fix layering overlap
                    const chatCont = document.querySelector('div[role="presentation"].flex-col.relative');
                    if (chatCont) chatCont.style.paddingTop = '80px';

                    // Check for Bulk Delete Success Message
                    // We look for the specific success text in the latest message
                    // Check for Bulk Delete Success Message via ID
                    const bulkDeleteMarker = document.getElementById('bulk-delete-success-marker');
                    if (bulkDeleteMarker && !bulkDeleteMarker.hasAttribute('data-processed')) {
                        console.log("[Nebulus] Bulk delete detected, refreshing sidebar...");
                        this.Sidebar.refresh();
                        bulkDeleteMarker.setAttribute('data-processed', 'true');
                    }
                }
            }, 500); // Increased timeout to 500ms to allow render
        });
        // Remove subtree: true to prevent deep recursion
        observer.observe(document.body, { childList: true, subtree: true });
    },

    /* =========================================
       Templates
       ========================================= */
    Templates: {
        getSidebar: (recentChatsHTML, user) => `
            <div id="nebulus-sidebar">
                <div class="sidebar-header">
                    <img src="/public/sidebar_logo.png" alt="Logo" class="sidebar-logo-img">
                    <div class="logo-text">NEBULUS</div>
                    <div class="toggle-btn" id="sidebar-toggle">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                    </div>
                </div>

                <div class="new-chat-container">
                     <div class="new-chat-btn" onclick="window.location.href='/'">
                        <span class="icon-plus">+</span>
                        <span>New chat</span>
                    </div>
                </div>

                <div class="sidebar-scroll-area">
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">My Stuff</div>
                        <div class="my-stuff-grid">
                            <div class="stuff-item" title="Nebulus">
                                 <div class="stuff-icon gradient-1">N</div>
                            </div>
                             <div class="stuff-item" title="Gantry">
                                 <div class="stuff-icon gradient-2">G</div>
                            </div>
                             <div class="stuff-item" title="Knowledge">
                                 <div class="stuff-icon gradient-3">K</div>
                            </div>
                        </div>
                    </div>

                    <div class="sidebar-section">
                         <div class="nav-item" onclick="window.location.href='/workspace'">
                            <div class="nav-icon">${Nebulus.Icons.grid}</div>
                            <span class="nav-label">Manage Workspaces</span>
                        </div>
                    </div>

                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Chats</div>
                         <div class="nav-item" onclick="Nebulus.Search.open(event)">
                            <div class="nav-icon">${Nebulus.Icons.search}</div>
                            <span class="nav-label">Search chats</span>
                        </div>
                        <div id="recent-chats-list" class="recent-chats-list">
                            ${recentChatsHTML || '<div style="padding: 10px; color: #555; font-size: 0.7rem;" class="nav-label">No recent chats</div>'}
                        </div>
                    </div>
                </div>

                <div class="sidebar-footer">

                     <div class="user-profile">
                        <div class="user-avatar">${Nebulus.Utils.getInitials(user.full_name || user.username)}</div>
                        <span class="nav-label">${user.full_name || user.username}</span>
                    </div>
                </div>
            </div>
        `,

        getDashboard: (modelName, username = "User") => `
            <div id="nebulus-dashboard">
                <div class="dashboard-content">
                     <div class="dashboard-greeting">
                         <span id="dashboard-greeting-text" class="gradient-text">Hi ${username}</span><br>
                         <span>Where should we start?</span>
                    </div>

                     <div class="input-pill-container">
                        <div class="input-pill-label">Ask Nebulus</div>
                        <div class="input-pill">
                             <div class="icon-btn">${Nebulus.Icons.plus}</div>
                             <input type="text" id="dashboard-input" placeholder="Type something..." autocomplete="off">
                             <div class="right-actions">
                                  <div class="icon-btn" title="Attach file">${Nebulus.Icons.paperclip}</div>
                                  <div class="icon-btn" id="dashboard-submit">${Nebulus.Icons.send}</div>
                             </div>
                        </div>
                    </div>

                    <div class="suggestions-grid">
                        <div class="suggestion-pill" onclick="Nebulus.Chat.setInput('Create image')">
                            <span class="emoji">🎨</span> Create image
                        </div>
                        <div class="suggestion-pill" onclick="Nebulus.Chat.setInput('Create video')">
                            <span class="emoji">🎥</span> Create video
                        </div>
                        <div class="suggestion-pill" onclick="Nebulus.Chat.setInput('Write anything')">
                            <span class="emoji">✍️</span> Write anything
                        </div>
                        <div class="suggestion-pill" onclick="Nebulus.Chat.setInput('Help me learn')">
                            <span class="emoji">🎓</span> Help me learn
                        </div>
                         <div class="suggestion-pill" onclick="Nebulus.Chat.setInput('Boost my day')">
                            <span class="emoji">🚀</span> Boost my day
                        </div>
                         <div class="suggestion-pill" onclick="Nebulus.Chat.setInput('Stay organized')">
                            <span class="emoji">📅</span> Stay organized
                        </div>
                    </div>
                </div>
            </div>
        `,

        getSearchModal: () => `
            <div id="search-modal-overlay">
                <div id="search-modal">
                    <div class="search-header">
                        ${Nebulus.Icons.search}
                        <input type="text" id="search-input" placeholder="Search chats..." autocomplete="off">
                    </div>
                    <div class="search-results" id="search-results">
                        <div style="text-align:center; padding: 20px; color: #555;">Type to search...</div>
                    </div>
                </div>
            </div>
        `
    },

    Icons: {
        chevronLeft: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>`,
        chevronRight: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`,
        moon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`,
        sun: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`,
        search: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7d8590" stroke-width="2" style="margin-right: 10px;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
        plus: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
        send: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`,
        fileText: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
        paperclip: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>`,
        image: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>`,
        grid: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>`,
        copy: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg>`,
        check: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check"><polyline points="20 6 9 17 4 12"></polyline></svg>`
    },

    /* =========================================
       Modules
       ========================================= */
    Sidebar: {
        init: function () {
            this.inject();
            this.applyState();
        },

        inject: function () {
            if (document.getElementById('nebulus-sidebar')) return;

            // Fetch data
            Promise.all([
                fetch('/api/history').then(res => res.json()),
                fetch('/me').then(res => res.json())
            ]).then(([history, user]) => {
                // Personalization Logic
                const firstName = (user.full_name || user.username || "User").split(' ')[0];
                Nebulus.state.firstName = firstName;

                // Update Dashboard Greeting if present
                const greetingEl = document.getElementById('dashboard-greeting-text');
                if (greetingEl) {
                    greetingEl.textContent = `Hi ${firstName}`;
                }

                this.render(history, user);
            }).catch(err => {
                console.error("Failed to load sidebar data", err);
                this.render([], { full_name: "Guest", username: "guest" });
            });
        },

        render: function (history, user) {
            // Check if already rendered during async wait
            if (document.getElementById('nebulus-sidebar')) return;

            const recentChatsHTML = history.map(chat => `
                <div class="nav-item sub-item" onclick="window.location.href='/?chat_id=${chat.id}'">
                    <span class="nav-label">${chat.title}</span>
                    <div class="chat-options-btn" onclick="Nebulus.Sidebar.showContextMenu(event, '${chat.id}')">⋮</div>
                </div>
            `).join('');

            const sidebarContainer = document.createElement('div');
            sidebarContainer.innerHTML = Nebulus.Templates.getSidebar(recentChatsHTML, user);
            document.body.prepend(sidebarContainer.firstElementChild);

            this.setupEvents();
        },

        showContextMenu: function (event, chatId) {
            event.stopPropagation();
            this.closeContextMenu();

            const menu = document.createElement('div');
            menu.className = 'context-menu';
            menu.id = 'active-context-menu';

            const options = [
                { label: 'Share', icon: '➦', action: 'share' },
                { label: 'Rename', icon: '✎', action: 'rename' },
                { label: 'Delete', icon: '🗑', action: 'delete' }
            ];

            options.forEach(opt => {
                const item = document.createElement('div');
                item.className = 'context-menu-item';
                item.innerHTML = `<span class="menu-icon">${opt.icon}</span><span>${opt.label}</span>`;
                item.onclick = (e) => {
                    e.stopPropagation();
                    this.handleMenuAction(opt.action, chatId);
                    this.closeContextMenu();
                };
                menu.appendChild(item);
            });

            document.body.appendChild(menu);

            // Positioning
            const rect = event.target.getBoundingClientRect();
            menu.style.top = `${rect.bottom + 5}px`;
            menu.style.left = `${rect.left}px`;
        },

        closeContextMenu: function () {
            const existing = document.getElementById('active-context-menu');
            if (existing) existing.remove();
        },

        refresh: function () {
            // Fetch updated data first
            fetch('/api/history')
                .then(res => res.json())
                .then(history => {
                    const listContainer = document.getElementById('recent-chats-list');
                    if (listContainer) {
                        const recentChatsHTML = history.map(chat => `
                            <div class="nav-item sub-item" onclick="window.location.href='/?chat_id=${chat.id}'">
                                <span class="nav-label">${chat.title}</span>
                                <div class="chat-options-btn" onclick="Nebulus.Sidebar.showContextMenu(event, '${chat.id}')">⋮</div>
                            </div>
                        `).join('');

                        listContainer.innerHTML = recentChatsHTML || '<div style="padding: 10px; color: #555; font-size: 0.7rem;" class="nav-label">No recent chats</div>';
                    } else {
                        // Fallback to full re-injection if list not found for some reason
                        const sidebar = document.getElementById('nebulus-sidebar');
                        if (sidebar) sidebar.remove();
                        this.inject();
                    }
                })
                .catch(err => console.error("Failed to refresh sidebar", err));
        },

        handleMenuAction: function (action, chatId) {
            if (action === 'share') {
                const url = window.location.origin + '/?chat_id=' + chatId;
                navigator.clipboard.writeText(url).then(() => {
                    Nebulus.Utils.showToast('Link copied to clipboard');
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    Nebulus.Utils.showToast('Failed to copy link');
                });
            } else if (action === 'rename') {
                // Fetch current name first? Easier to just leave blank or generic
                // Or better: pass current name via data attribute if feasible.
                // For now, empty prompt is standard.
                Nebulus.Modal.prompt("Rename Chat", "Enter a new name for this chat:", "", (newName) => {
                    if (newName && newName.trim()) {
                        fetch(`/api/chats/${chatId}/rename`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ title: newName.trim() })
                        })
                            .then(res => res.json())
                            .then(data => {
                                if (data.status === 'success') {
                                    this.refresh();
                                    Nebulus.Utils.showToast('Chat renamed');
                                } else {
                                    Nebulus.Utils.showToast('Failed to rename chat');
                                }
                            })
                            .catch(e => Nebulus.Utils.showToast('Error renaming chat'));
                    }
                });
            } else if (action === 'delete') {
                Nebulus.Modal.confirm("Delete Chat", "Are you sure you want to delete this chat? This action cannot be undone.", () => {
                    fetch(`/api/chats/${chatId}`, {
                        method: 'DELETE'
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'success') {
                                this.refresh();
                                Nebulus.Utils.showToast('Chat deleted');
                                // If current chat, redirect to home
                                const urlParams = new URLSearchParams(window.location.search);
                                if (urlParams.get('chat_id') === chatId) {
                                    window.location.href = '/';
                                }
                            } else {
                                Nebulus.Utils.showToast('Failed to delete chat');
                            }
                        })
                        .catch(e => Nebulus.Utils.showToast('Error deleting chat'));
                });
            }
        },


        setupEvents: function () {
            const toggleBtn = document.getElementById('sidebar-toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => this.toggle());
            }

            // Close context menu on global click
            document.addEventListener('click', () => this.closeContextMenu());
        },

        toggle: function () {
            document.body.classList.toggle('sidebar-collapsed');
            const collapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', collapsed);

            const toggleBtn = document.getElementById('sidebar-toggle');
            if (toggleBtn) {
                toggleBtn.innerHTML = collapsed ? Nebulus.Icons.chevronRight : Nebulus.Icons.chevronLeft;
            }
        },

        applyState: function () {
            if (Nebulus.state.sidebarCollapsed) {
                document.body.classList.add('sidebar-collapsed');
            }
        }
    },

    Actions: {
        ensureCopyButtons: function () {
            // Updated footer selector based on subagent findings
            // Updated footer selector based on subagent findings + alternative Chainlit class
            const footers = document.querySelectorAll('.items-center.flex-wrap, .cl-message-footer');

            footers.forEach(footer => {
                // Must have a Regenerate button to be an assistant message we care about
                const buttons = Array.from(footer.querySelectorAll('button'));
                const hasRegen = buttons.some(b => b.innerText.includes('Regenerate'));
                const alreadyHasCopy = footer.querySelector('.lucide-copy') || footer.querySelector('.custom-copy-btn');

                if (hasRegen && !alreadyHasCopy) {
                    this.injectCopyButton(footer);
                }
            });
        },

        injectCopyButton: function (container) {
            const btn = document.createElement('button');
            btn.className = 'custom-copy-btn';
            btn.style.padding = '4px';
            btn.style.marginRight = '8px';
            btn.style.borderRadius = '4px';
            btn.style.display = 'flex';
            btn.style.alignItems = 'center';
            btn.style.justifyContent = 'center';
            btn.style.cursor = 'pointer';
            btn.style.border = 'none';
            btn.style.background = 'transparent';
            btn.style.color = 'var(--text-secondary)';
            btn.innerHTML = Nebulus.Icons.copy;
            btn.title = "Copy message";

            btn.onclick = (e) => {
                e.stopPropagation();
                const msgEl = container.closest('.flex.flex-col');
                if (msgEl) {
                    const contentEl = msgEl.querySelector('.message-content');
                    if (contentEl) {
                        let text = contentEl.innerText;
                        // Strip token usage footer if present
                        const tokenIdx = text.lastIndexOf('\n\n---\nTokens:');
                        if (tokenIdx !== -1) {
                            text = text.substring(0, tokenIdx).trim();
                        }

                        navigator.clipboard.writeText(text).then(() => {
                            btn.innerHTML = Nebulus.Icons.check;
                            setTimeout(() => btn.innerHTML = Nebulus.Icons.copy, 2000);
                        });
                    }
                }
            };

            container.prepend(btn);
        }
    },

    Dashboard: {
        checkAndInject: function () {
            const urlParams = new URLSearchParams(window.location.search);
            const initialChatId = urlParams.get('chat_id');

            // Strategy:
            // 1. If Deep Link exists, load history (hide dashboard).
            // 2. If NO Deep Link, show dashboard.

            if (initialChatId) {
                // We let the Chat module handle the loading logic, ensuring Dashboard is hidden
                // Only load if not already loaded?
                // We rely on the fact that if dashboard is present, we must be in 'new chat' mode unless URL says otherwise.
                if (!this.hasAutoLoaded) {
                    // Small delay to ensure ws connection
                    this.hasAutoLoaded = true;
                    setTimeout(() => Nebulus.Chat.loadHistory(initialChatId), 500);
                }
                this.hide();
            } else {
                this.inject();
            }
        },

        inject: function () {
            // Defensive Check: Never inject dashboard if we are in a chat view
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('chat_id')) return;

            if (document.getElementById('nebulus-dashboard')) return;

            // Try to find current model from selector or state
            let currentModel = "Llama 3.1";
            const selector = document.getElementById('model-selector');
            if (selector) currentModel = selector.value;

            const dashboardContainer = document.createElement('div');
            dashboardContainer.innerHTML = Nebulus.Templates.getDashboard(currentModel);
            const dashboardEl = dashboardContainer.firstElementChild;
            dashboardEl.style.display = 'flex'; // Explicitly show it
            document.body.appendChild(dashboardEl);

            // Add Input Listener
            const input = document.getElementById('dashboard-input');
            const submitBtn = document.getElementById('dashboard-submit');

            const handleSubmit = () => {
                const val = input.value.trim();
                if (val) {
                    Nebulus.Chat.setInput(val);
                    Nebulus.Dashboard.hide();
                }
            };


            if (input) {
                input.focus();
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                    }
                });
            }

            if (submitBtn) {
                submitBtn.addEventListener('click', handleSubmit);
            }

            // Wire up Attachment Buttons (Plus and FileText)
            const plusBtn = dashboardEl.querySelector('.input-pill .icon-btn:first-child');
            const fileBtn = dashboardEl.querySelector('.right-actions .icon-btn:first-child');

            const triggerNativeUpload = () => {
                const nativeFileInput = document.querySelector('input[type="file"]');
                if (nativeFileInput) {
                    // Remove any existing listener to prevent duplicates (though typically valid for this lifecycle)
                    // Better: just add a listener that checks if dashboard is visible.
                    nativeFileInput.addEventListener('change', () => {
                        if (nativeFileInput.files && nativeFileInput.files.length > 0) {
                            Nebulus.Dashboard.hide();
                            // Also focus the main chat input
                            setTimeout(() => {
                                const chatInput = document.getElementById('chat-input');
                                if (chatInput) chatInput.focus();
                            }, 300);
                        }
                    }, { once: true }); // Use once to avoid stacking if clicked multiple times without reload

                    nativeFileInput.click();
                } else {
                    Nebulus.Utils.showToast("Upload not available");
                }
            };

            if (plusBtn) plusBtn.addEventListener('click', triggerNativeUpload);
            if (fileBtn) fileBtn.addEventListener('click', triggerNativeUpload);
        },

        hide: function () {
            const dashboard = document.getElementById('nebulus-dashboard');
            if (dashboard) dashboard.style.display = 'none';
        }
    },

    Chat: {
        init: function () {
            this.setupCommandInterception();
        },

        setupCommandInterception: function () {
            // Document-level delegation for robust handling
            const handler = (e) => {
                // 1. Identify the input element
                let input = document.getElementById('chat-input') || document.getElementById('dashboard-input');
                // Fallback: Try finding by active element if it's a textarea
                if (!input && document.activeElement && (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT')) {
                    input = document.activeElement;
                }

                if (!input) return;

                const val = input.value.trim();
                if (val !== '/clear_all') return;

                // 2. Check Triggers
                let isTrigger = false;

                // Case A: Enter Key
                if (e.type === 'keydown' && e.key === 'Enter' && !e.shiftKey) {
                    isTrigger = true;
                }

                // Case B: Click on Submit Button
                if (e.type === 'click') {
                    // Start from target and loop up to find button
                    let el = e.target;
                    while (el && el !== document.body) {
                        // Check for common submission indicators
                        if (el.id === 'chat-submit' || el.id === 'dashboard-submit' || el.type === 'submit' || el.getAttribute('role') === 'button') {
                            // Ensure it's inside the chat/input area (approximate)
                            isTrigger = true;
                            break;
                        }
                        el = el.parentElement;
                    }
                }
                if (isTrigger) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();

                    console.log("[Nebulus] Intercepted /clear_all");

                    Nebulus.Modal.confirm(
                        "Delete All Chats",
                        "Are you sure you want to delete all chat history? This action cannot be undone.",
                        () => this.handleClearAll()
                    );
                }
            };

            // Capture phase is essential to beat React/Chainlit listeners
            document.addEventListener('keydown', handler, true);
            document.addEventListener('click', handler, true);
        },

        handleClearAll: function () {
            // Optimistic UI update or wait for success? Wait for success to be safe.
            fetch('/api/chats', { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Clear Input
                        const input = document.getElementById('chat-input');
                        if (input) input.value = '';

                        // Clear Sidebar
                        const list = document.getElementById('recent-chats-list');
                        if (list) list.innerHTML = '<div style="padding: 10px; color: #555; font-size: 0.7rem;" class="nav-label">No recent chats</div>';

                        Nebulus.Utils.showToast("All chats deleted");

                        // Redirect to home if current page is a chat?
                        const urlParams = new URLSearchParams(window.location.search);
                        if (urlParams.get('chat_id')) {
                            window.location.href = '/';
                        }
                    } else {
                        Nebulus.Utils.showToast("Failed to delete chats");
                    }
                })
                .catch(err => {
                    console.error(err);
                    Nebulus.Utils.showToast("Error deleting chats");
                });
        },

        loadHistory: function (chatId) {
            // 1. Update URL (Safe to do even if already there)
            const newUrl = `/?chat_id=${chatId}`;
            history.pushState({ chat_id: chatId }, "", newUrl);

            // 2. Hide Dashboard
            Nebulus.Dashboard.hide();

            // 3. Send Command
            if (window.setInput) { // Chainlit internal or our wrapper
                // Use our wrapper logic or direct call
                Nebulus.Chat.setInput(`/load_history ${chatId}`);
            } else {
                console.error("setInput not found");
            }
        },

        setInput: function (text) {
            const textarea = document.querySelector('#chat-input, textarea');
            if (textarea) {
                const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeTextAreaValueSetter.call(textarea, text);
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.focus();
                if (Nebulus.Dashboard) Nebulus.Dashboard.hide();

                // Ensure dashboard is hidden (Safety Net)
                if (Nebulus.Dashboard) Nebulus.Dashboard.hide();

                setTimeout(() => {
                    const event = new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', which: 13, keyCode: 13, bubbles: true, cancelable: true });
                    textarea.dispatchEvent(event);
                    setTimeout(() => {
                        if (textarea.value === text) {
                            const sendBtn = document.getElementById('chat-submit');
                            if (sendBtn) sendBtn.click();
                        }
                    }, 200);
                }, 100);
            }
        }
    },

    Search: {
        init: function () {
            // Exposed for onclick events
            window.openSearchModal = this.open.bind(this);
        },

        open: function (e) {
            if (e) e.preventDefault();
            this.inject();
            const overlay = document.getElementById('search-modal-overlay');
            overlay.classList.add('open');
            document.getElementById('search-input').focus();
        },

        inject: function () {
            if (document.getElementById('search-modal-overlay')) return;

            const div = document.createElement('div');
            div.innerHTML = Nebulus.Templates.getSearchModal();
            document.body.appendChild(div.firstElementChild);

            this.setupEvents();
        },

        setupEvents: function () {
            const overlay = document.getElementById('search-modal-overlay');
            const input = document.getElementById('search-input');

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) overlay.classList.remove('open');
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && overlay.classList.contains('open')) overlay.classList.remove('open');
            });

            let timeout;
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                const val = e.target.value;
                if (val.length < 2) {
                    document.getElementById('search-results').innerHTML = '<div style="text-align:center; padding: 20px; color: #555;">Type to search...</div>';
                    return;
                }
                timeout = setTimeout(() => this.perform(val), 300);
            });
        },

        perform: function (query) {
            const resultsContainer = document.getElementById('search-results');
            resultsContainer.innerHTML = '<div style="text-align:center; padding: 20px; color: #7d8590;">Searching...</div>';

            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => this.renderResults(data, resultsContainer))
                .catch(err => {
                    console.error("Search failed", err);
                    resultsContainer.innerHTML = '<div style="text-align:center; padding: 20px; color: #fa3860;">Search failed.</div>';
                });
        },

        renderResults: function (data, container) {
            if (!data || data.length === 0) {
                container.innerHTML = '<div style="text-align:center; padding: 20px; color: #7d8590;">No results found.</div>';
                return;
            }
            container.innerHTML = data.map(item => `
                <div class="search-result-item" onclick="window.location.href='/?chat_id=${item.chat_id}'">
                    <div class="result-title">${item.title}</div>
                    <div class="result-snippet">${Nebulus.Utils.escapeHtml(item.snippet)}</div>
                    <div class="result-meta">${new Date(item.created_at).toLocaleDateString()}</div>
                </div>
            `).join('');
        }
    },

    Models: {
        init: function () {
            this.injectDropdown();
        },

        checkForSwitch: function () {
            const hiddenDiv = document.getElementById('model-data');
            if (hiddenDiv) {
                const modelName = hiddenDiv.getAttribute('data-model');
                if (modelName) {
                    const select = document.getElementById('model-selector');
                    if (select && select.value !== modelName) {
                        select.value = modelName;
                        // Put current at top
                        const options = Array.from(select.options);
                        const currentOpt = options.find(o => o.value === modelName);
                        if (currentOpt) {
                            currentOpt.remove();
                            select.prepend(currentOpt);
                            select.selectedIndex = 0;
                        }
                    }

                    // Also update Dashboard text if visible
                    const dashboardDisplay = document.querySelector('.current-model-display');
                    if (dashboardDisplay) {
                        dashboardDisplay.textContent = modelName;
                    }

                    // Toast
                    if (hiddenDiv.getAttribute('data-shown') !== 'true') {
                        Nebulus.Utils.showToast(`Model switched to ${modelName}`);
                        hiddenDiv.setAttribute('data-shown', 'true');
                    }
                }
            }
        },

        injectDropdown: function (models) {
            if (document.getElementById('model-selector-container')) return;

            // If models not provided, try cache or fetch
            if (!models) {
                if (Nebulus.state.cachedModels.length > 0) {
                    models = Nebulus.state.cachedModels;
                } else {
                    // Fetch
                    fetch('/models')
                        .then(res => res.json())
                        .then(data => {
                            if (data.models) {
                                // Simple sort or logic here
                                Nebulus.state.cachedModels = data.models.sort();
                                this.injectDropdown(Nebulus.state.cachedModels);
                            }
                        })
                        .catch(err => console.error(err));
                    return; // Wait for async
                }
            }

            if (!models || models.length === 0) return;

            const container = document.createElement('div');
            container.id = 'model-selector-container';
            const select = document.createElement('select');
            select.id = 'model-selector';

            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.text = model;
                select.appendChild(option);
            });

            select.addEventListener('change', (e) => this.switchModel(e.target.value));

            container.appendChild(select);
            document.body.appendChild(container); // Append

            // Set initial
            const modelData = document.getElementById('model-data');
            if (modelData && modelData.dataset.model) {
                select.value = modelData.dataset.model;
            }
        },

        switchModel: function (newModel) {
            fetch('/api/model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: newModel })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        Nebulus.Utils.showToast(`Switched to ${newModel}`);
                        const hiddenDiv = document.getElementById('model-data');
                        if (hiddenDiv) {
                            hiddenDiv.setAttribute('data-model', newModel);
                            hiddenDiv.setAttribute('data-shown', 'true');
                        }
                    } else {
                        Nebulus.Utils.showToast("Failed to switch model");
                    }
                })
                .catch(err => Nebulus.Utils.showToast("Error switching model"));
        }
    },

    Theme: {
        init: function () {
            this.injectToggle();
            this.observe();
        },

        observe: function () {
            const themeObserver = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        const isDark = document.documentElement.classList.contains('dark');
                    }
                });
            });
            themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
        },

        injectToggle: function () {
            if (document.getElementById('floating-theme-toggle')) return;

            const toggleBtn = document.createElement('div');
            toggleBtn.id = 'floating-theme-toggle';
            toggleBtn.className = 'theme-toggle-btn';

            const storedTheme = localStorage.getItem('vite-ui-theme');
            const isDark = storedTheme === 'dark';

            if (isDark && !document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.add('dark');
            } else if (!isDark && document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
            }

            toggleBtn.innerHTML = isDark ? Nebulus.Icons.sun : Nebulus.Icons.moon;
            toggleBtn.title = "Toggle Theme";

            toggleBtn.onclick = () => this.toggle();

            document.body.appendChild(toggleBtn);
        },

        toggle: function () {
            const currentIsDark = document.documentElement.classList.contains('dark');
            const newIsDark = !currentIsDark;
            document.documentElement.classList.toggle('dark', newIsDark);

            // Update floating toggle icon
            const btn = document.getElementById('floating-theme-toggle');
            if (btn) {
                btn.innerHTML = newIsDark ? Nebulus.Icons.sun : Nebulus.Icons.moon;
            }

            localStorage.setItem('vite-ui-theme', newIsDark ? 'dark' : 'light');
            window.dispatchEvent(new Event('storage'));
        }
    },

    Utils: {
        isChatPage: function () {
            // Returns true only for the root chat page
            return window.location.pathname === '/';
        },

        escapeHtml: function (text) {
            if (!text) return "";
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        },

        getInitials: function (name) {
            return name.match(/(\b\S)?/g).join("").match(/(^\S|\S$)?/g).join("").toUpperCase();
        },

        showToast: function (message) {
            let toast = document.getElementById('model-toast');
            if (!toast) {
                toast = document.createElement('div');
                toast.id = 'model-toast';
                document.body.appendChild(toast);
            }
            toast.textContent = message;
            toast.className = 'show';
            setTimeout(() => {
                toast.className = toast.className.replace('show', '');
            }, 3000);
        }
    },

    Modal: {
        confirm: function (title, message, onConfirm) {
            this.create({
                title,
                message,
                buttons: [
                    { label: 'Cancel', class: 'btn-modal-secondary', onClick: () => this.close() },
                    { label: 'Delete', class: 'btn-modal-primary', onClick: () => { this.close(); onConfirm(); } }
                ]
            });
        },

        prompt: function (title, message, initialValue, onConfirm) {
            this.create({
                title,
                message,
                input: { value: initialValue, placeholder: 'Enter value...' },
                buttons: [
                    { label: 'Cancel', class: 'btn-modal-secondary', onClick: () => this.close() },
                    { label: 'Save', class: 'btn-modal-primary', onClick: (val) => { this.close(); onConfirm(val); } }
                ]
            });
        },

        create: function (config) {
            this.close(); // Close any existing

            const backdrop = document.createElement('div');
            backdrop.className = 'nebulus-modal-backdrop';
            backdrop.id = 'nebulus-active-modal';

            const modal = document.createElement('div');
            modal.className = 'nebulus-modal';

            // Title
            if (config.title) {
                const title = document.createElement('div');
                title.className = 'modal-title';
                title.textContent = config.title;
                modal.appendChild(title);
            }

            // Message
            if (config.message) {
                const msg = document.createElement('div');
                msg.className = 'modal-message';
                msg.textContent = config.message;
                modal.appendChild(msg);
            }

            // Input
            let inputEl = null;
            if (config.input) {
                inputEl = document.createElement('input');
                inputEl.type = 'text';
                inputEl.className = 'modal-input';
                inputEl.value = config.input.value || '';
                inputEl.placeholder = config.input.placeholder || '';
                modal.appendChild(inputEl);
                setTimeout(() => inputEl.focus(), 100);
            }

            // Actions
            const actions = document.createElement('div');
            actions.className = 'modal-actions';

            config.buttons.forEach(btn => {
                const button = document.createElement('button');
                button.type = 'button'; // Critical: Prevent form submission interception
                button.className = btn.class || 'btn-modal-secondary';
                button.textContent = btn.label;
                button.onclick = () => btn.onClick(inputEl ? inputEl.value : null);
                actions.appendChild(button);
            });

            modal.appendChild(actions);
            backdrop.appendChild(modal);
            document.body.appendChild(backdrop);

            // Animate in
            requestAnimationFrame(() => backdrop.classList.add('visible'));

            // Enter key support for input
            if (inputEl) {
                inputEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        const saveBtn = config.buttons.find(b => b.label === 'Save');
                        if (saveBtn) saveBtn.onClick(inputEl.value);
                    }
                });
            }
        },

        close: function () {
            const el = document.getElementById('nebulus-active-modal');
            if (el) {
                el.classList.remove('visible');
                setTimeout(() => el.remove(), 200);
            }
        }
    }
};

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Nebulus.init());
} else {
    Nebulus.init();
}

// Global Exports for Legacy/Inline Compatibility
window.Nebulus = Nebulus;
window.loadChatHistory = Nebulus.Chat.loadHistory;
window.setInput = Nebulus.Chat.setInput;
