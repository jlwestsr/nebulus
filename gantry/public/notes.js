document.addEventListener('DOMContentLoaded', () => {
    const listContainer = document.getElementById('notes-list');
    const editorContainer = document.getElementById('notes-editor');
    const emptyState = document.getElementById('empty-state');
    const titleInput = document.getElementById('note-title');
    const contentInput = document.getElementById('note-content');
    const saveBtn = document.getElementById('save-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const newNoteBtn = document.getElementById('new-note-btn');
    const navNewBtn = document.querySelector('.new-chat-btn'); // Sidebar btn override? No, distinct.

    let notes = [];
    let currentNoteId = null;

    // Load Notes
    fetchNotes();

    // Event Listeners
    if (newNoteBtn) newNoteBtn.addEventListener('click', createNewNote);
    if (saveBtn) saveBtn.addEventListener('click', saveCurrentNote);
    if (deleteBtn) deleteBtn.addEventListener('click', deleteCurrentNote);

    // Auto-save logic (debounce)
    let timeoutId;
    const autoSave = () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            if (currentNoteId) saveCurrentNote(true);
        }, 2000);
    };

    titleInput.addEventListener('input', autoSave);
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
        newBtn.className = 'note-item';
        newBtn.style.textAlign = 'center';
        newBtn.style.color = '#F80061';
        newBtn.textContent = '+ New Note';
        newBtn.onclick = createNewNote;
        listContainer.appendChild(newBtn);

        if (notes.length === 0) {
            // listContainer.innerHTML += '<div style="padding:10px; color:#555;">No notes yet.</div>';
        }

        notes.forEach(note => {
            const el = document.createElement('div');
            el.className = `note-item ${currentNoteId === note.id ? 'active' : ''}`;
            el.onclick = () => loadNote(note.id);

            const title = document.createElement('div');
            title.style.fontWeight = '500';
            title.textContent = note.title || 'Untitled';

            const date = document.createElement('div');
            date.className = 'date';
            date.textContent = new Date(note.updated_at).toLocaleDateString();

            el.appendChild(title);
            el.appendChild(date);
            listContainer.appendChild(el);
        });
    }

    function loadNote(id) {
        currentNoteId = id;
        const note = notes.find(n => n.id === id);
        if (!note) return;

        titleInput.value = note.title;
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
            body: JSON.stringify({ title: 'Untitled Note', content: '' })
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
                editorContainer.style.display = 'none';
                emptyState.style.display = 'flex';
                renderNotesList();
            })
            .catch(err => alert('Error deleting note'));
    }

});
