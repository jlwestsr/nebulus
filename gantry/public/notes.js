/**
 * Nebulus Notes Module
 * Refactored to Nebulus.Notes namespace
 */

if (!window.Nebulus) window.Nebulus = {};

Nebulus.Notes = {
    state: {
        notes: [],
        currentNoteId: null,
        isPreviewMode: false,
        isDirty: false,
        categoryStates: {},
        timeoutId: null
    },

    init: function () {
        this.cacheDOM();
        this.bindEvents();
        this.configureMarkdown();
        this.fetchNotes();
        this.startAutoSaveInterval();
    },

    cacheDOM: function () {
        this.dom = {
            listContainer: document.getElementById('notes-list'),
            editorContainer: document.getElementById('notes-editor'),
            emptyState: document.getElementById('empty-state'),
            titleInput: document.getElementById('note-title'),
            categoryInput: document.getElementById('note-category'),
            contentInput: document.getElementById('note-content'),
            saveBtn: document.getElementById('save-btn'),
            deleteBtn: document.getElementById('delete-btn'),
            newNoteBtn: document.getElementById('new-note-btn'),
            previewBtn: document.getElementById('preview-btn'),
            previewContainer: document.getElementById('note-preview')
        };
    },

    bindEvents: function () {
        const d = this.dom;
        if (d.newNoteBtn) d.newNoteBtn.addEventListener('click', () => this.createNewNote());
        if (d.saveBtn) d.saveBtn.addEventListener('click', () => this.saveCurrentNote(false));
        if (d.deleteBtn) d.deleteBtn.addEventListener('click', () => this.deleteCurrentNote());
        if (d.previewBtn) d.previewBtn.addEventListener('click', () => this.togglePreview());

        // Auto-save triggers
        const autoSaveHandler = () => this.handleAutoSaveInput();
        if (d.titleInput) d.titleInput.addEventListener('input', autoSaveHandler);
        if (d.categoryInput) d.categoryInput.addEventListener('input', autoSaveHandler);
        if (d.contentInput) d.contentInput.addEventListener('input', autoSaveHandler);
    },

    configureMarkdown: function () {
        if (window.marked && window.hljs) {
            marked.setOptions({
                highlight: function (code, lang) {
                    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                    return hljs.highlight(code, { language }).value;
                },
                langPrefix: 'hljs language-'
            });
        }
    },

    fetchNotes: function () {
        fetch('/api/notes')
            .then(res => res.json())
            .then(data => {
                this.state.notes = data;
                this.renderNotesList();
            })
            .catch(err => console.error("Failed to load notes", err));
    },

    renderNotesList: function () {
        const container = this.dom.listContainer;
        if (!container) return;

        container.innerHTML = '';

        // "New Note" Button in List
        const newBtn = document.createElement('div');
        newBtn.className = 'note-item text-accent';
        newBtn.style.textAlign = 'center';
        newBtn.textContent = '+ New Note';
        newBtn.onclick = () => this.createNewNote();
        container.appendChild(newBtn);

        const grouped = this.state.notes.reduce((acc, note) => {
            const cat = note.category || 'Uncategorized';
            if (!acc[cat]) acc[cat] = [];
            acc[cat].push(note);
            return acc;
        }, {});

        Object.keys(grouped).sort().forEach(cat => {
            // Default expanded
            if (this.state.categoryStates[cat] === undefined) {
                this.state.categoryStates[cat] = true;
            }
            const isExpanded = this.state.categoryStates[cat];

            const catHeader = document.createElement('div');
            catHeader.className = 'category-header';
            catHeader.innerHTML = `
                <span>${cat}</span>
                <span class="category-toggle-icon" style="transform: rotate(${isExpanded ? '90deg' : '180deg'})">▶</span>
            `;
            catHeader.onclick = () => {
                this.state.categoryStates[cat] = !isExpanded;
                this.renderNotesList();
            };
            container.appendChild(catHeader);

            if (isExpanded) {
                grouped[cat].forEach(note => {
                    const el = document.createElement('div');
                    el.className = `note-item ${this.state.currentNoteId === note.id ? 'active' : ''}`;
                    el.style.paddingLeft = '20px';
                    el.onclick = () => this.loadNote(note.id);

                    const title = document.createElement('div');
                    title.style.fontWeight = '500';
                    title.textContent = note.title || 'Untitled';

                    const date = document.createElement('div');
                    date.className = 'date';
                    date.textContent = new Date(note.updated_at).toLocaleDateString();

                    const snippet = document.createElement('div');
                    snippet.className = 'snippet';
                    const raw = note.content || '';
                    snippet.textContent = raw.slice(0, 60) + (raw.length > 60 ? '...' : '');

                    el.appendChild(title);
                    el.appendChild(date);
                    el.appendChild(snippet);
                    container.appendChild(el);
                });
            }
        });
    },

    loadNote: function (id) {
        if (this.state.currentNoteId && this.state.isDirty) {
            this.saveCurrentNote(true);
        }

        this.state.currentNoteId = id;
        this.state.isDirty = false;
        this.state.isPreviewMode = false;

        const d = this.dom;
        if (d.previewBtn) d.previewBtn.textContent = 'Preview';
        if (d.contentInput) d.contentInput.style.display = 'block';
        if (d.previewContainer) d.previewContainer.style.display = 'none';

        const note = this.state.notes.find(n => n.id === id);
        if (!note) return;

        if (d.titleInput) d.titleInput.value = note.title;
        if (d.categoryInput) d.categoryInput.value = note.category || '';
        if (d.contentInput) d.contentInput.value = note.content;

        if (d.editorContainer) d.editorContainer.style.display = 'flex';
        if (d.emptyState) d.emptyState.style.display = 'none';

        this.renderNotesList();
    },

    createNewNote: function () {
        fetch('/api/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'Untitled Note', content: '', category: 'Uncategorized' })
        })
            .then(res => res.json())
            .then(note => {
                this.state.notes.unshift(note);
                this.loadNote(note.id);
            })
            .catch(err => alert('Error creating note'));
    },

    saveCurrentNote: function (silent = false) {
        if (!this.state.currentNoteId) return;

        const d = this.dom;
        const updatedData = {
            title: d.titleInput.value,
            category: d.categoryInput.value || 'Uncategorized',
            content: d.contentInput.value
        };

        // Optimistic update
        const idx = this.state.notes.findIndex(n => n.id === this.state.currentNoteId);
        if (idx > -1) {
            this.state.notes[idx] = { ...this.state.notes[idx], ...updatedData, updated_at: new Date().toISOString() };
            this.renderNotesList();
        }

        if (!silent && d.saveBtn) {
            d.saveBtn.textContent = 'Saving...';
            d.saveBtn.disabled = true;
        }

        fetch(`/api/notes/${this.state.currentNoteId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        })
            .then(res => res.json())
            .then(data => {
                this.state.isDirty = false;
                if (!silent && d.saveBtn) {
                    d.saveBtn.textContent = 'Saved';
                    setTimeout(() => {
                        d.saveBtn.textContent = 'Save Note';
                        d.saveBtn.disabled = false;
                    }, 1000);
                }
            })
            .catch(err => {
                console.error(err);
                if (!silent && d.saveBtn) d.saveBtn.textContent = 'Error';
            });
    },

    deleteCurrentNote: function () {
        if (!this.state.currentNoteId) return;
        if (!confirm('Are you sure you want to delete this note?')) return;

        fetch(`/api/notes/${this.state.currentNoteId}`, {
            method: 'DELETE'
        })
            .then(res => res.json())
            .then(() => {
                this.state.notes = this.state.notes.filter(n => n.id !== this.state.currentNoteId);
                this.state.currentNoteId = null;
                this.state.isDirty = false;

                if (this.dom.editorContainer) this.dom.editorContainer.style.display = 'none';
                if (this.dom.emptyState) this.dom.emptyState.style.display = 'flex';

                this.renderNotesList();
            })
            .catch(err => alert('Error deleting note'));
    },

    togglePreview: function () {
        this.state.isPreviewMode = !this.state.isPreviewMode;
        const d = this.dom;

        if (this.state.isPreviewMode) {
            const rawContent = d.contentInput.value;
            d.previewContainer.innerHTML = marked.parse(rawContent);
            if (window.hljs) hljs.highlightAll();
            d.contentInput.style.display = 'none';
            d.previewContainer.style.display = 'block';
            d.previewBtn.textContent = 'Edit';
        } else {
            d.contentInput.style.display = 'block';
            d.previewContainer.style.display = 'none';
            d.previewBtn.textContent = 'Preview';
            d.contentInput.focus();
        }
    },

    handleAutoSaveInput: function () {
        this.state.isDirty = true;
        clearTimeout(this.state.timeoutId);
        this.state.timeoutId = setTimeout(() => {
            if (this.state.currentNoteId) this.saveCurrentNote(true);
        }, 2000);
    },

    startAutoSaveInterval: function () {
        setInterval(() => {
            if (this.state.currentNoteId && this.state.isDirty) {
                console.log('Interval auto-save triggered');
                this.saveCurrentNote(true);
            }
        }, 30000);
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Only init if we are on the notes page (check for container)
    if (document.getElementById('notes-list')) {
        Nebulus.Notes.init();
    }
});
