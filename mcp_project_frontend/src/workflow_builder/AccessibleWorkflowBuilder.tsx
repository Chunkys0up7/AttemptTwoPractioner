import React, { useRef, useEffect } from 'react';
import { useWorkflowBuilder } from './useWorkflowBuilder';
import { WorkflowBuilderProps } from '../../types/workflow';
import { WorkflowErrorBoundary } from '../../components/error/WorkflowErrorBoundary';

/**
 * Accessible version of the WorkflowBuilder component
 * @param props - WorkflowBuilderProps
 * @returns Accessible WorkflowBuilder component
 */
const AccessibleWorkflowBuilder: React.FC<WorkflowBuilderProps> = (props) => {
  const {
    nodes,
    edges,
    selectedNode,
    reactFlowInstance,
    onNodesChange,
    onEdgesChange,
    onConnect,
    onDrop,
    setSelectedNode,
  } = useWorkflowBuilder();

  const canvasRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setSelectedNode(null);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [setSelectedNode]);

  const focusNode = (nodeId: string) => {
    const node = document.querySelector(`[data-node-id="${nodeId}"]`);
    if (node) {
      node.focus();
    }
  };

  return (
    <WorkflowErrorBoundary>
      <div
        ref={canvasRef}
        role="application"
        aria-label="Workflow builder canvas"
        onKeyDown={(e) => {
          if (e.key === 'Tab') {
            e.preventDefault();
            const nodes = document.querySelectorAll('[data-node-id]');
            const currentIndex = Array.from(nodes).findIndex(
              (n) => n.getAttribute('data-node-id') === selectedNode?.id
            );
            const nextIndex = currentIndex === nodes.length - 1 ? 0 : currentIndex + 1;
            focusNode(nodes[nextIndex].getAttribute('data-node-id')!);
          }
        }}
      >
        <div className="node-list" aria-label="Available workflow nodes">
          {nodes.map((node) => (
            <div
              key={node.id}
              role="button"
              tabIndex={0}
              aria-label={`Node ${node.data.name}`}
              aria-selected={selectedNode?.id === node.id}
              onClick={() => setSelectedNode(node)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  setSelectedNode(node);
                }
              }}
            >
              {node.data.name}
            </div>
          ))}
        </div>
        <div className="edge-list" aria-label="Workflow connections">
          {edges.map((edge) => (
            <div
              key={edge.id}
              role="presentation"
              aria-label={`Connection from ${edge.source} to ${edge.target}`}
            />
          ))}
        </div>
        {selectedNode && (
          <div
            className="selected-node-info"
            role="region"
            aria-label={`Properties for ${selectedNode.data.name}`}
          >
            <h3>{selectedNode.data.name}</h3>
          </div>
        )}
      </div>
    </WorkflowErrorBoundary>
  );
};

export default AccessibleWorkflowBuilder;
