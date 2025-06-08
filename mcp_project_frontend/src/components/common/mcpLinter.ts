// mcpLinter.ts
// Linter for MCP scripts (YAML/JSON) to be used with CodeEditor validate prop
import * as yaml from 'js-yaml';
import * as monaco from 'monaco-editor';

const RESERVED_KEYWORDS = ['start', 'end', 'workflow'];

export function lintMcpScript(code: string): monaco.editor.IMarkerData[] {
  const markers: monaco.editor.IMarkerData[] = [];
  let parsed: any = null;
  try {
    parsed = yaml.load(code);
  } catch (err: any) {
    markers.push({
      severity: monaco.MarkerSeverity.Error,
      message: 'Invalid YAML/JSON: ' + err.message,
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 1,
    });
    return markers;
  }
  if (!parsed || typeof parsed !== 'object') {
    markers.push({
      severity: monaco.MarkerSeverity.Error,
      message: 'MCP config must be a YAML/JSON object.',
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 1,
    });
    return markers;
  }
  // Required keys
  ['steps', 'inputs', 'outputs'].forEach(key => {
    if (!(key in parsed)) {
      markers.push({
        severity: monaco.MarkerSeverity.Error,
        message: `Missing required key: ${key}`,
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: 1,
        endColumn: 1,
      });
    }
  });
  // Type checks
  if (parsed.steps && !Array.isArray(parsed.steps)) {
    markers.push({
      severity: monaco.MarkerSeverity.Error,
      message: 'steps must be an array.',
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 1,
    });
  }
  if (parsed.inputs && typeof parsed.inputs !== 'object') {
    markers.push({
      severity: monaco.MarkerSeverity.Error,
      message: 'inputs must be an object or array.',
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 1,
    });
  }
  if (parsed.outputs && typeof parsed.outputs !== 'object') {
    markers.push({
      severity: monaco.MarkerSeverity.Error,
      message: 'outputs must be an object or array.',
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 1,
    });
  }
  // Forbidden patterns: duplicate step names, reserved keywords
  if (Array.isArray(parsed.steps)) {
    const seen = new Set<string>();
    parsed.steps.forEach((step: any, idx: number) => {
      if (!step.name) {
        markers.push({
          severity: monaco.MarkerSeverity.Error,
          message: `Step at index ${idx} is missing a name.`,
          startLineNumber: 1,
          startColumn: 1,
          endLineNumber: 1,
          endColumn: 1,
        });
      } else {
        if (seen.has(step.name)) {
          markers.push({
            severity: monaco.MarkerSeverity.Error,
            message: `Duplicate step name: ${step.name}`,
            startLineNumber: 1,
            startColumn: 1,
            endLineNumber: 1,
            endColumn: 1,
          });
        }
        if (RESERVED_KEYWORDS.includes(step.name)) {
          markers.push({
            severity: monaco.MarkerSeverity.Error,
            message: `Step name '${step.name}' is a reserved keyword.`,
            startLineNumber: 1,
            startColumn: 1,
            endLineNumber: 1,
            endColumn: 1,
          });
        }
        seen.add(step.name);
        // Best practice: warn if missing description
        if (!step.description) {
          markers.push({
            severity: monaco.MarkerSeverity.Warning,
            message: `Step '${step.name}' is missing a description.`,
            startLineNumber: 1,
            startColumn: 1,
            endLineNumber: 1,
            endColumn: 1,
          });
        }
      }
    });
  }
  // Best practice: warn if inputs/outputs are empty
  if (parsed.inputs && Object.keys(parsed.inputs).length === 0) {
    markers.push({
      severity: monaco.MarkerSeverity.Warning,
      message: 'inputs is empty.',
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 1,
    });
  }
  if (parsed.outputs && Object.keys(parsed.outputs).length === 0) {
    markers.push({
      severity: monaco.MarkerSeverity.Warning,
      message: 'outputs is empty.',
      startLineNumber: 1,
      startColumn: 1,
      endLineNumber: 1,
      endColumn: 1,
    });
  }
  return markers;
} 