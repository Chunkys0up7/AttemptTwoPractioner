import React, { memo } from 'react';
import { useWorkflowBuilder } from './useWorkflowBuilder';
import { WorkflowBuilderProps } from '../../types/workflow';

/**
 * Memoized version of the WorkflowBuilder component
 * @param props - WorkflowBuilderProps
 * @returns Memoized WorkflowBuilder component
 */
const MemoizedWorkflowBuilder: React.FC<WorkflowBuilderProps> = memo((props) => {
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

  const renderNodes = React.useMemo(() => {
    return nodes.map((node) => (
      <div
        key={node.id}
        className="workflow-node"
        data-node-id={node.id}
      >
        {node.data.name}
      </div>
    ));
  }, [nodes]);

  const renderEdges = React.useMemo(() => {
    return edges.map((edge) => (
      <div
        key={edge.id}
        className="workflow-edge"
        data-edge-id={edge.id}
      />
    ));
  }, [edges]);

  return (
    <div className="workflow-builder">
      <div className="node-list">{renderNodes}</div>
      <div className="edge-list">{renderEdges}</div>
      {selectedNode && (
        <div className="selected-node-info">
          <h3>{selectedNode.data.name}</h3>
        </div>
      )}
    </div>
  );
});

MemoizedWorkflowBuilder.displayName = 'MemoizedWorkflowBuilder';

export default MemoizedWorkflowBuilder;
