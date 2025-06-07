import React, { useRef } from 'react';
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
}) => {
  const editorRef = useRef<any>(null);

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

  return (
    <div onDrop={handleDrop} onDragOver={e => e.preventDefault()} style={{ border: '1px solid #e5e7eb', borderRadius: 6 }}>
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