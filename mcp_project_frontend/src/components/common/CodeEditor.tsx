import React, { useRef, useState } from 'react';
import MonacoEditor, { OnChange, OnMount } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';

interface CodeSnippet {
  label: string;
  documentation: string;
  body: string;
}

interface CodeEditorProps {
  value: string;
  language: string;
  onChange: (value: string | undefined) => void;
  height?: string;
  options?: Record<string, any>;
  onFileUpload?: (content: string, file: File) => void;
  /**
   * Optional custom validation function. Receives the code value and returns an array of Monaco IMarkerData.
   * These will be shown as inline errors/warnings in the editor.
   */
  validate?: (value: string) => monaco.editor.IMarkerData[];
  /**
   * Optional array of code snippets/templates to register for the language.
   */
  snippets?: CodeSnippet[];
  /**
   * Enable auto-format on save (Ctrl+S/Cmd+S). Default: true.
   */
  formatOnSave?: boolean;
  /**
   * Enable advanced Python IntelliSense via LSP (requires a running Python language server and WebSocket proxy). Default: false.
   */
  enablePythonLsp?: boolean;
}

const defaultOptions = {
  selectOnLineNumbers: true,
  minimap: { enabled: false },
  fontSize: 14,
  scrollBeyondLastLine: false,
  wordWrap: 'on' as const,
  automaticLayout: true,
  formatOnPaste: true,
  formatOnType: true,
  lineNumbers: 'on' as const,
  theme: 'vs-dark',
};

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  language,
  onChange,
  height = '300px',
  options = {},
  onFileUpload,
  validate,
  snippets = [],
  formatOnSave = true,
  enablePythonLsp = false,
}) => {
  const editorRef = useRef<any>(null);
  const [showSnippetMenu, setShowSnippetMenu] = useState(false);

  const handleEditorDidMount: OnMount = (editor, monacoInstance) => {
    editorRef.current = editor;
    // Run custom validation if provided
    if (validate && value) {
      const model = editor.getModel();
      if (model) {
        const markers = validate(value);
        monacoInstance.editor.setModelMarkers(model, 'owner', markers);
      }
    }
  };

  // Run validation on value change
  React.useEffect(() => {
    if (validate && editorRef.current && value !== undefined) {
      const model = editorRef.current.getModel?.();
      if (model) {
        const markers = validate(value);
        monaco.editor.setModelMarkers(model, 'owner', markers);
      }
    }
  }, [value, validate]);

  // Register snippets on mount or language/snippets change
  React.useEffect(() => {
    if (snippets.length > 0 && monaco.languages && monaco.languages.registerCompletionItemProvider) {
      const disposable = monaco.languages.registerCompletionItemProvider(language, {
        provideCompletionItems: (model, position) => {
          const suggestions = snippets.map((snippet, i) => ({
            label: snippet.label,
            kind: monaco.languages.CompletionItemKind.Snippet,
            documentation: snippet.documentation,
            insertText: snippet.body,
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            sortText: 'zzz' + i,
            range: new monaco.Range(position.lineNumber, 1, position.lineNumber, position.column),
          }));
          return { suggestions };
        },
      });
      return () => disposable.dispose();
    }
  }, [language, JSON.stringify(snippets)]);

  // Register format on save
  React.useEffect(() => {
    if (!formatOnSave) return;
    const editor = editorRef.current;
    if (!editor) return;
    const model = editor.getModel?.();
    if (!model) return;
    const disposable = editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
      () => {
        editor.getAction('editor.action.formatDocument').run();
      }
    );
    return () => {
      if (disposable && disposable.dispose) disposable.dispose();
    };
  }, [formatOnSave, language]);

  // --- Python LSP Integration ---
  React.useEffect(() => {
    let disposeLsp: (() => void) | undefined;
    if (enablePythonLsp && language === 'python') {
      (async () => {
        try {
          // Dynamically import monaco-python and LSP client
          const monacoPy = await import('monaco-python');
          // @ts-ignore
          monacoPy.loadPyodide(); // Loads Pyodide for Monaco Python (optional, fallback)
          // Set up LSP connection
          const { MonacoLanguageClient, CloseAction, ErrorAction, createConnection } = await import('monaco-languageclient');
          const ReconnectingWebSocket = (await import('reconnecting-websocket')).default;
          const url = 'ws://localhost:3001'; // Python LSP WebSocket endpoint
          const webSocket = new ReconnectingWebSocket(url);
          webSocket.onopen = () => {
            const connection = createConnection(webSocket as any);
            const languageClient = new MonacoLanguageClient({
              name: 'Python Language Client',
              clientOptions: {
                documentSelector: ['python'],
                errorHandler: {
                  error: () => ErrorAction.Continue,
                  closed: () => CloseAction.Restart,
                },
              },
              connectionProvider: {
                get: () => Promise.resolve(connection),
              },
            });
            languageClient.start();
            disposeLsp = () => languageClient.stop();
          };
        } catch (err) {
          // eslint-disable-next-line no-console
          console.error('Failed to initialize Python LSP:', err);
        }
      })();
    }
    return () => {
      if (disposeLsp) disposeLsp();
    };
  }, [enablePythonLsp, language]);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        if (onFileUpload) {
          onFileUpload(content, file);
        } else {
          onChange(content);
        }
      };
      reader.readAsText(file);
    }
  };

  const insertSnippet = (body: string) => {
    const editor = editorRef.current;
    if (editor) {
      editor.focus();
      editor.trigger('keyboard', 'type', { text: body });
    }
    setShowSnippetMenu(false);
  };

  return (
    <div onDrop={handleDrop} onDragOver={e => e.preventDefault()} style={{ border: '1px solid #e5e7eb', borderRadius: 6, position: 'relative' }}>
      {snippets.length > 0 && (
        <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}>
          <button
            type="button"
            className="px-2 py-1 bg-primary text-white rounded text-xs hover:bg-primary-dark focus:outline-none"
            aria-haspopup="true"
            aria-expanded={showSnippetMenu}
            aria-controls="snippet-menu"
            onClick={() => setShowSnippetMenu(v => !v)}
          >
            Insert Snippet
          </button>
          {showSnippetMenu && (
            <div id="snippet-menu" className="absolute right-0 mt-2 w-64 bg-white border border-neutral-200 rounded shadow-lg z-20">
              <ul className="max-h-60 overflow-y-auto">
                {snippets.map((snippet, i) => (
                  <li key={i}>
                    <button
                      type="button"
                      className="w-full text-left px-4 py-2 hover:bg-neutral-100 text-sm"
                      onClick={() => insertSnippet(snippet.body)}
                    >
                      <span className="font-semibold">{snippet.label}</span>
                      <div className="text-xs text-neutral-500">{snippet.documentation}</div>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      <MonacoEditor
        value={value}
        language={language}
        onChange={onChange as OnChange}
        height={height}
        options={{ ...defaultOptions, ...options }}
        onMount={handleEditorDidMount}
      />
      <input
        type="file"
        accept=".py,.ts,.js,.json,.sql,.txt,.md"
        style={{ display: 'none' }}
        onChange={e => {
          const file = e.target.files?.[0];
          if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
              const content = event.target?.result as string;
              if (onFileUpload) {
                onFileUpload(content, file);
              } else {
                onChange(content);
              }
            };
            reader.readAsText(file);
          }
        }}
        id="code-editor-file-upload"
      />
      <label htmlFor="code-editor-file-upload" style={{ cursor: 'pointer', display: 'block', marginTop: 8, color: '#2563eb', fontSize: 13 }}>
        Upload file
      </label>
    </div>
  );
};

export default CodeEditor; 