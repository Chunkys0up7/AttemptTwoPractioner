
import React, { useState, useRef, useCallback } from 'react';
// It's recommended to use React Flow or a similar library for the canvas.
// For this example, we'll just show placeholders.
// import ReactFlow, { ReactFlowProvider, addEdge, MiniMap, Controls, Background, useNodesState, useEdgesState, Connection, Edge, Node } from 'reactflow';
// import 'reactflow/dist/style.css';

import ComponentPalette from '../components/workflow_builder/ComponentPalette';
import PropertiesPanel from '../components/workflow_builder/PropertiesPanel';
import Button from '../components/common/Button';
import { PlayIcon, WorkflowBuilderIcon } from '../icons'; // Assuming SaveIcon, ValidateIcon also exist or use text
import { AIComponent } from '../types';

// Mock node data for React Flow (if it were integrated)
// const initialNodes: Node[] = [
//   { id: '1', type: 'input', data: { label: 'Start Node' }, position: { x: 250, y: 5 } },
// ];

const WorkflowBuilderPage: React.FC = () => {
  // const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  // const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  // const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  // const reactFlowWrapper = useRef<HTMLDivElement>(null);
  // const [reactFlowInstance, setReactFlowInstance] = useState<any>(null); // Simplified type

  // const onConnect = useCallback((params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  // const onDragOver = useCallback((event: React.DragEvent) => {
  //   event.preventDefault();
  //   event.dataTransfer.dropEffect = 'move';
  // }, []);

  // const onDrop = useCallback(
  //   (event: React.DragEvent) => {
  //     event.preventDefault();
  //     if (!reactFlowWrapper.current || !reactFlowInstance) return;

  //     const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
  //     const type = event.dataTransfer.getData('application/reactflow');
  //     const componentDataString = event.dataTransfer.getData('application/componentdata');
      
  //     if (typeof type === 'undefined' || !type) {
  //       return;
  //     }

  //     const position = reactFlowInstance.project({
  //       x: event.clientX - reactFlowBounds.left,
  //       y: event.clientY - reactFlowBounds.top,
  //     });
      
  //     const componentData: AIComponent = JSON.parse(componentDataString);

  //     const newNode: Node = {
  //       id: `dndnode_${new Date().getTime()}`, // Ensure unique ID
  //       type, // e.g., 'customComponentNode'
  //       position,
  //       data: { name: componentData.name, componentId: componentData.id, config: {} /* default config */ },
  //     };

  //     setNodes((nds) => nds.concat(newNode));
  //   },
  //   [reactFlowInstance, setNodes]
  // );

  // const onNodeClick = (_: React.MouseEvent, node: Node) => {
  //   setSelectedNode(node);
  // };


  return (
    <div className="flex flex-col h-full">
      <header className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-neutral-800">Workflow Builder</h1>
          <p className="text-neutral-600 mt-1">Visually construct, configure, and test your AI workflows.</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">Save</Button>
          <Button variant="secondary" size="sm">Validate</Button>
          <Button variant="primary" size="sm" leftIcon={<PlayIcon className="w-4 h-4" />}>Run Test</Button>
        </div>
      </header>

      <div className="flex flex-1 gap-6 overflow-hidden">
        <aside className="w-1/4 xl:w-1/5 h-full overflow-y-auto">
          <ComponentPalette />
        </aside>
        
        <main 
          className="w-1/2 xl:w-3/5 h-full bg-white rounded-lg shadow-lg flex items-center justify-center text-neutral-400 border border-neutral-200"
          // ref={reactFlowWrapper}
          // onDrop={onDrop}
          // onDragOver={onDragOver}
        >
          {/* Placeholder for React Flow canvas */}
          {/* <ReactFlowProvider>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              onInit={setReactFlowInstance}
              fitView
              className="bg-neutral-50"
            >
              <MiniMap />
              <Controls />
              <Background />
            </ReactFlow>
          </ReactFlowProvider> */}
          <div className="text-center">
            <WorkflowBuilderIcon className="w-24 h-24 text-neutral-300 mx-auto mb-4" />
            <p className="text-xl font-medium">Workflow Canvas Area</p>
            <p className="text-sm">Drag components from the palette to build your workflow.</p>
            <p className="text-xs mt-2">(React Flow integration would go here)</p>
          </div>
        </main>

        <aside className="w-1/4 xl:w-1/5 h-full overflow-y-auto">
          <PropertiesPanel selectedNode={null /* pass selectedNode here in a real app */} />
        </aside>
      </div>
    </div>
  );
};

export default WorkflowBuilderPage;