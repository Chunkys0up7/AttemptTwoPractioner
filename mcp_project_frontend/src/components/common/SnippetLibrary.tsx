import React, { useState, useEffect } from 'react';

export interface Snippet {
  id: string;
  label: string;
  language: string;
  body: string;
  description?: string;
}

interface SnippetLibraryProps {
  onInsertSnippet: (snippet: Snippet) => void;
  onClose: () => void;
}

const SNIPPETS_KEY = 'user_snippets';

function loadSnippets(): Snippet[] {
  try {
    const raw = localStorage.getItem(SNIPPETS_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function saveSnippets(snippets: Snippet[]) {
  localStorage.setItem(SNIPPETS_KEY, JSON.stringify(snippets));
}

export const SnippetLibrary: React.FC<SnippetLibraryProps> = ({ onInsertSnippet, onClose }) => {
  const [snippets, setSnippets] = useState<Snippet[]>([]);
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState<Snippet | null>(null);
  const [newSnippet, setNewSnippet] = useState<Partial<Snippet>>({});

  useEffect(() => {
    setSnippets(loadSnippets());
  }, []);

  const filtered = snippets.filter(s =>
    s.label.toLowerCase().includes(search.toLowerCase()) ||
    (s.description || '').toLowerCase().includes(search.toLowerCase())
  );

  function handleSave(snippet: Snippet) {
    let updated: Snippet[];
    if (snippets.some(s => s.id === snippet.id)) {
      updated = snippets.map(s => (s.id === snippet.id ? snippet : s));
    } else {
      updated = [...snippets, snippet];
    }
    setSnippets(updated);
    saveSnippets(updated);
    setEditing(null);
    setNewSnippet({});
  }

  function handleDelete(id: string) {
    const updated = snippets.filter(s => s.id !== id);
    setSnippets(updated);
    saveSnippets(updated);
  }

  function handleEdit(snippet: Snippet) {
    setEditing(snippet);
    setNewSnippet({ ...snippet });
  }

  function handleNew() {
    setEditing(null);
    setNewSnippet({ id: Date.now().toString(), label: '', language: 'python', body: '', description: '' });
  }

  function handleChange(field: keyof Snippet, value: string) {
    setNewSnippet(prev => ({ ...prev, [field]: value }));
  }

  function handleInsert(snippet: Snippet) {
    onInsertSnippet(snippet);
    onClose();
  }

  return (
    <div role="dialog" aria-modal="true" aria-label="Snippet Library">
      <button onClick={onClose} aria-label="Close">Close</button>
      <h2>Snippet Library</h2>
      <input
        type="text"
        placeholder="Search snippets..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        aria-label="Search snippets"
      />
      <button onClick={handleNew}>New Snippet</button>
      <ul>
        {filtered.map(snippet => (
          <li key={snippet.id}>
            <strong>{snippet.label}</strong> ({snippet.language})
            <button onClick={() => handleInsert(snippet)}>Insert</button>
            <button onClick={() => handleEdit(snippet)}>Edit</button>
            <button onClick={() => handleDelete(snippet.id)}>Delete</button>
            <div>{snippet.description}</div>
          </li>
        ))}
      </ul>
      {(editing || newSnippet.label) && (
        <form
          onSubmit={e => {
            e.preventDefault();
            if (newSnippet.id && newSnippet.label && newSnippet.body && newSnippet.language) {
              handleSave(newSnippet as Snippet);
            }
          }}
        >
          <h3>{editing ? 'Edit Snippet' : 'New Snippet'}</h3>
          <label>
            Label
            <input
              type="text"
              value={newSnippet.label || ''}
              onChange={e => handleChange('label', e.target.value)}
              required
            />
          </label>
          <label>
            Language
            <input
              type="text"
              value={newSnippet.language || ''}
              onChange={e => handleChange('language', e.target.value)}
              required
            />
          </label>
          <label>
            Description
            <input
              type="text"
              value={newSnippet.description || ''}
              onChange={e => handleChange('description', e.target.value)}
            />
          </label>
          <label>
            Body
            <textarea
              value={newSnippet.body || ''}
              onChange={e => handleChange('body', e.target.value)}
              required
            />
          </label>
          <button type="submit">Save</button>
          <button type="button" onClick={() => { setEditing(null); setNewSnippet({}); }}>Cancel</button>
        </form>
      )}
      {/* TODO: Integrate with backend for persistent storage */}
    </div>
  );
}; 