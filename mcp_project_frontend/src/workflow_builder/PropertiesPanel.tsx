import React, { useMemo } from 'react';
import Card from '../common/Card';
import CodeEditor from '../common/CodeEditor';

// Example snippet sets (should be imported or defined elsewhere in real app)
const PYTHON_SNIPPETS = [
  { label: 'Print Hello', documentation: 'Prints Hello World', body: 'print("Hello, World!")' },
  { label: 'For Loop', documentation: 'Basic for loop', body: 'for i in range(10):\n    print(i)' },
];
const TYPESCRIPT_SNIPPETS = [
  { label: 'Log', documentation: 'Console log', body: 'console.log("Hello, World!");' },
  { label: 'Function', documentation: 'TypeScript function', body: 'function greet(name: string): void {\n  console.log(`Hello, ${name}`);\n}' },
];
const SQL_SNIPPETS = [
  { label: 'Select All', documentation: 'Select all rows', body: 'SELECT * FROM table;' },
];
const MARKDOWN_SNIPPETS = [
  { label: 'Header', documentation: 'Markdown header', body: '# Header' },
  { label: 'Link', documentation: 'Markdown link', body: '[Link text](https://example.com)' },
];
const YAML_SNIPPETS = [
  { label: 'Key-Value', documentation: 'YAML key-value', body: 'key: value' },
  { label: 'List', documentation: 'YAML list', body: '- item1\n- item2' },
];
const PLAINTEXT_SNIPPETS = [
  { label: 'TODO', documentation: 'Add a TODO', body: 'TODO: ...' },
];

function getLanguageAndSnippets(key: string) {
  const lower = key.toLowerCase();
  if (lower.includes('python')) return { language: 'python', snippets: PYTHON_SNIPPETS };
  if (lower.includes('typescript') || lower.includes('ts')) return { language: 'typescript', snippets: TYPESCRIPT_SNIPPETS };
  if (lower.includes('sql')) return { language: 'sql', snippets: SQL_SNIPPETS };
  if (lower.includes('markdown') || lower.includes('md')) return { language: 'markdown', snippets: MARKDOWN_SNIPPETS };
  if (lower.includes('yaml') || lower.includes('yml')) return { language: 'yaml', snippets: YAML_SNIPPETS };
  if (lower.includes('code') || lower.includes('script')) return { language: 'python', snippets: PYTHON_SNIPPETS };
  if (lower.includes('config')) return { language: 'yaml', snippets: YAML_SNIPPETS };
  return { language: 'plaintext', snippets: PLAINTEXT_SNIPPETS };
}

// This is a placeholder. In a real app, this would be dynamic based on selected node.
interface PropertiesPanelProps {
  selectedNode?: any; // Replace 'any' with actual node type from React Flow
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ selectedNode }) => {
  return (
    <Card title="Properties" className="h-full">
      {selectedNode ? (
        <div>
          <h4 className="text-sm font-semibold text-neutral-700 mb-1">Node: {selectedNode.data?.name || selectedNode.id}</h4>
          <p className="text-xs text-neutral-500 mb-3">Type: {selectedNode.type}</p>
          
          {/* Dynamic properties based on config */}
          {selectedNode.data?.config && Object.entries(selectedNode.data.config).map(([key, value]) => {
            const { language, snippets } = getLanguageAndSnippets(key);
            const isCode = [
              'code', 'script', 'sql', 'markdown', 'yaml', 'python', 'typescript', 'config'
            ].some(word => key.toLowerCase().includes(word));
            return (
              <div key={key} className="mb-2">
                <label className="block text-xs font-medium text-neutral-600 mb-0.5">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</label>
                {isCode ? (
                  <CodeEditor
                    value={String(value)}
                    language={language}
                    onChange={() => {}}
                    height="120px"
                    snippets={snippets}
                  />
                ) : (
                  <input
                    type="text"
                    defaultValue={String(value)}
                    className="block w-full text-xs p-1.5 border border-neutral-300 rounded-md bg-white text-neutral-900 placeholder-neutral-500 focus:ring-primary focus:border-primary"
                  />
                )}
              </div>
            );
          })}
          {/* Placeholder for more complex config UI */}
          {!selectedNode.data?.config && <p className="text-xs text-neutral-500">No configurable properties for this node type.</p>}

        </div>
      ) : (
        <p className="text-sm text-neutral-500">Select a node or edge to view its properties.</p>
      )}
      <div className="mt-4 p-3 bg-neutral-50 rounded-md">
         <h5 className="text-xs font-semibold text-neutral-600 mb-1">Workflow Settings</h5>
         <label className="block text-xs font-medium text-neutral-600 mb-0.5">Workflow Name</label>
         <input 
            type="text" 
            defaultValue="My New Workflow" 
            className="block w-full text-xs p-1.5 border border-neutral-300 rounded-md bg-white text-neutral-900 placeholder-neutral-500 focus:ring-primary focus:border-primary"
        />
      </div>
    </Card>
  );
};

export default PropertiesPanel;