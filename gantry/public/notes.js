document.addEventListener('DOMContentLoaded', () => {
    const listContainer = document.getElementById('notes-list');
    const editorContainer = document.getElementById('notes-editor');
    const emptyState = document.getElementById('empty-state');
    const titleInput = document.getElementById('note-title');
    const categoryInput = document.getElementById('note-category');
    const contentInput = document.getElementById('note-content');
    const saveBtn = document.getElementById('save-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const newNoteBtn = document.getElementById('new-note-btn');
    const navNewBtn = document.querySelector('.new-chat-btn');

    let notes = [];
    let currentNoteId = null;
    let isPreviewMode = false;
    let isDirty = false;

    // State for expanded/collapsed categories (true = expanded)
    let categoryStates = {};

    const previewBtn = document.getElementById('preview-btn');
    const previewContainer = document.getElementById('note-preview');

    // Configure Marked with Highlight.js
    if (window.marked && window.hljs) {
        marked.setOptions({
            highlight: function (code, lang) {
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, { language }).value;
            },
            langPrefix: 'hljs language-'
        });
    }

    // Load Notes
    fetchNotes();

    // Event Listeners
    if (newNoteBtn) newNoteBtn.addEventListener('click', createNewNote);
    if (saveBtn) saveBtn.addEventListener('click', () => saveCurrentNote(false));
    if (deleteBtn) deleteBtn.addEventListener('click', deleteCurrentNote);

    if (previewBtn) {
        previewBtn.addEventListener('click', () => {
            isPreviewMode = !isPreviewMode;
            if (isPreviewMode) {
                // Show Preview
                const rawContent = contentInput.value;
                previewContainer.innerHTML = marked.parse(rawContent);
                if (window.hljs) hljs.highlightAll();
                contentInput.style.display = 'none';
                previewContainer.style.display = 'block';
                previewBtn.textContent = 'Edit';
            } else {
                // Show Editor
                contentInput.style.display = 'block';
                previewContainer.style.display = 'none';
                previewBtn.textContent = 'Preview';
                contentInput.focus();
            }
        });
    }

    // Auto-save logic (debounce)
    let timeoutId;
    const autoSave = () => {
        isDirty = true;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            if (currentNoteId) saveCurrentNote(true);
        }, 2000);
    };

    // Auto-save Interval Failsafe (Every 30s)
    setInterval(() => {
        if (currentNoteId && isDirty) {
            console.log('Interval auto-save triggered');
            saveCurrentNote(true);
        }
    }, 30000);

    titleInput.addEventListener('input', autoSave);
    categoryInput.addEventListener('input', autoSave);
    contentInput.addEventListener('input', autoSave);


    function fetchNotes() {
        fetch('/api/notes')
            .then(res => res.json())
            .then(data => {
                notes = data;
                renderNotesList();
            })
            .catch(err => console.error("Failed to load notes", err));
    }

    function renderNotesList() {
        listContainer.innerHTML = '';

        // Add "New Note" at top of list for convenience
        const newBtn = document.createElement('div');
        newBtn.className = 'note-item text-accent';
        newBtn.style.textAlign = 'center';
        newBtn.textContent = '+ New Note';
        newBtn.onclick = createNewNote;
        listContainer.appendChild(newBtn);

        if (notes.length === 0) {
            // listContainer.innerHTML += '<div style="padding:10px; color:#555;">No notes yet.</div>';
        }

        // Group notes by category
        const grouped = notes.reduce((acc, note) => {
            const cat = note.category || 'Uncategorized';
            if (!acc[cat]) acc[cat] = [];
            acc[cat].push(note);
            return acc;
        }, {});

        // Render categories
        Object.keys(grouped).sort().forEach(cat => {
            // Default to expanded if state not set
            if (categoryStates[cat] === undefined) {
                categoryStates[cat] = true;
            }
            const isExpanded = categoryStates[cat];

            const catHeader = document.createElement('div');
            catHeader.className = 'category-header';
            catHeader.innerHTML = `
                <span>${cat}</span>
                <span class="category-toggle-icon" style="transform: rotate(${isExpanded ? '90deg' : '180deg'})">▶</span>
            `;

            catHeader.onclick = () => {
                categoryStates[cat] = !isExpanded;
                renderNotesList();
            };

            listContainer.appendChild(catHeader);

            if (isExpanded) {
                grouped[cat].forEach(note => {
                    const el = document.createElement('div');
                    el.className = `note-item ${currentNoteId === note.id ? 'active' : ''}`;
                    el.style.paddingLeft = '20px'; // Indent
                    el.onclick = () => loadNote(note.id);

                    const title = document.createElement('div');
                    title.style.fontWeight = '500';
                    title.textContent = note.title || 'Untitled';

                    const date = document.createElement('div');
                    date.className = 'date';
                    date.textContent = new Date(note.updated_at).toLocaleDateString();

                    const snippet = document.createElement('div');
                    snippet.className = 'snippet';
                    // Simple truncation
                    const raw = note.content || '';
                    snippet.textContent = raw.slice(0, 60) + (raw.length > 60 ? '...' : '');

                    el.appendChild(title);
                    el.appendChild(date);
                    el.appendChild(snippet);
                    listContainer.appendChild(el);
                });
            }
        });
    }

    function loadNote(id) {
        // If switching notes, save the previous one immediately if dirty
        if (currentNoteId && isDirty) {
            saveCurrentNote(true);
        }

        currentNoteId = id;
        isDirty = false;

        // Reset preview mode on load
        isPreviewMode = false;
        if (previewBtn) previewBtn.textContent = 'Preview';
        contentInput.style.display = 'block';
        if (previewContainer) previewContainer.style.display = 'none';

        const note = notes.find(n => n.id === id);
        if (!note) return;

        titleInput.value = note.title;
        categoryInput.value = note.category || '';
        contentInput.value = note.content;

        editorContainer.style.display = 'flex';
        emptyState.style.display = 'none';

        // Re-render list to show active state
        renderNotesList();
    }

    function createNewNote() {
        fetch('/api/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'Untitled Note', content: '', category: 'Uncategorized' })
        })
            .then(res => res.json())
            .then(note => {
                notes.unshift(note);
                loadNote(note.id);
            })
            .catch(err => alert('Error creating note'));
    }

    function saveCurrentNote(silent = false) {
        if (!currentNoteId) return;

        const updatedData = {
            title: titleInput.value,
            category: categoryInput.value || 'Uncategorized',
            content: contentInput.value
        };

        // Optimistic update
        const noteIdx = notes.findIndex(n => n.id === currentNoteId);
        if (noteIdx > -1) {
            notes[noteIdx] = { ...notes[noteIdx], ...updatedData, updated_at: new Date().toISOString() };
            renderNotesList(); // Update sidebar title immediately
        }

        if (!silent) {
            saveBtn.textContent = 'Saving...';
            saveBtn.disabled = true;
        }

        fetch(`/api/notes/${currentNoteId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        })
            .then(res => res.json())
            .then(data => {
                isDirty = false;
                if (!silent) {
                    saveBtn.textContent = 'Saved';
                    setTimeout(() => {
                        saveBtn.textContent = 'Save Note';
                        saveBtn.disabled = false;
                    }, 1000);
                }
            })
            .catch(err => {
                console.error(err);
                if (!silent) saveBtn.textContent = 'Error';
            });
    }

    function deleteCurrentNote() {
        if (!currentNoteId) return;
        if (!confirm('Are you sure you want to delete this note?')) return;

        fetch(`/api/notes/${currentNoteId}`, {
            method: 'DELETE'
        })
            .then(res => res.json())
            .then(() => {
                notes = notes.filter(n => n.id !== currentNoteId);
                currentNoteId = null;
                isDirty = false;
                editorContainer.style.display = 'none';
                emptyState.style.display = 'flex';
                renderNotesList();
            })
            .catch(err => alert('Error deleting note'));
    }

});
