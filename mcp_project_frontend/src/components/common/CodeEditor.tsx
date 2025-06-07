import React, { useRef } from 'react';
import MonacoEditor, { OnChange, OnMount } from '@monaco-editor/react';

interface CodeEditorProps {
  value: string;
  language: string;
  onChange: (value: string | undefined) => void;
  height?: string;
  options?: Record<string, any>;
  onFileUpload?: (content: string, file: File) => void;
}

const defaultOptions = {
  selectOnLineNumbers: true,
  minimap: { enabled: false },
  fontSize: 14,
  scrollBeyondLastLine: false,
  wordWrap: 'on',
  automaticLayout: true,
  formatOnPaste: true,
  formatOnType: true,
  lineNumbers: 'on',
  theme: 'vs-dark',
};

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  language,
  onChange,
  height = '300px',
  options = {},
  onFileUpload,
}) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount: OnMount = (editor) => {
    editorRef.current = editor;
  };

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