import React, { useState, useRef, useCallback } from 'react';
import ReactFlow, { ReactFlowProvider, addEdge, MiniMap, Controls, Background, useNodesState, useEdgesState, Connection, Edge, Node } from 'reactflow';
import 'reactflow/dist/style.css';

import ComponentPalette from './workflow_builder/ComponentPalette';
import PropertiesPanel from './workflow_builder/PropertiesPanel';
import Button from './components/common/Button';
import { PlayIcon, WorkflowBuilderIcon, MenuIcon, XIcon } from './components/common/icons';
import { AIComponent } from '@types';

const initialNodes: Node[] = [
  { id: '1', type: 'input', data: { label: 'Start Node' }, position: { x: 250, y: 5 } },
];

const WorkflowBuilderPage: React.FC = () => {
  const [isPaletteOpen, setIsPaletteOpen] = useState(true);
  const [isPropertiesOpen, setIsPropertiesOpen] = useState(true);
  const [isMobileView, setIsMobileView] = useState(window.innerWidth < 1024);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null); // Simplified type

  const onConnect = useCallback((params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      if (!reactFlowWrapper.current || !reactFlowInstance) return;

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');
      const componentDataString = event.dataTransfer.getData('application/componentdata');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const componentData: AIComponent = JSON.parse(componentDataString);

      const newNode: Node = {
        id: `dndnode_${new Date().getTime()}`,
        type,
        position,
        data: { name: componentData.name, componentId: componentData.id, config: {} },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  };

  // Handle window resize
  React.useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 1024;
      setIsMobileView(isMobile);
      if (isMobile) {
        setIsPaletteOpen(false);
        setIsPropertiesOpen(false);
      } else {
        setIsPaletteOpen(true);
        setIsPropertiesOpen(true);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="flex flex-col h-full">
      <header className="mb-6 flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-neutral-800 dark:text-neutral-100">
            Workflow Builder
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400 mt-1">
            Visually construct, configure, and test your AI workflows.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" aria-label="Save workflow">Save</Button>
          <Button variant="secondary" size="sm" aria-label="Validate workflow">Validate</Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<PlayIcon className="w-4 h-4" />}
            aria-label="Run workflow test"
          >
            Run Test
          </Button>
        </div>
      </header>

      {/* Mobile Toolbar */}
      <div className="lg:hidden flex justify-between items-center mb-4 bg-white dark:bg-neutral-800 p-2 rounded-lg shadow-sm">
        <Button
          variant="outline"
          size="sm"
          leftIcon={
            isPaletteOpen ? <XIcon className="w-4 h-4" /> : <MenuIcon className="w-4 h-4" />
          }
          onClick={() => setIsPaletteOpen(!isPaletteOpen)}
          aria-expanded={isPaletteOpen}
          aria-controls="component-palette"
        >
          {isPaletteOpen ? 'Hide Palette' : 'Show Palette'}
        </Button>
        <Button
          variant="outline"
          size="sm"
          leftIcon={
            isPropertiesOpen ? <XIcon className="w-4 h-4" /> : <MenuIcon className="w-4 h-4" />
          }
          onClick={() => setIsPropertiesOpen(!isPropertiesOpen)}
          aria-expanded={isPropertiesOpen}
          aria-controls="properties-panel"
        >
          {isPropertiesOpen ? 'Hide Properties' : 'Show Properties'}
        </Button>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* Component Palette */}
        <aside
          id="component-palette"
          className={`${
            isMobileView
              ? 'fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-200 ease-in-out'
              : 'w-1/4 xl:w-1/5'
          } ${
            isMobileView && !isPaletteOpen ? '-translate-x-full' : ''
          } h-full overflow-y-auto bg-white dark:bg-neutral-800 shadow-lg`}
        >
          <ComponentPalette />
        </aside>

        {/* Main Canvas Area */}
        <main
          ref={reactFlowWrapper}
          className={`${
            isMobileView ? 'w-full' : 'w-1/2 xl:w-3/5'
          } h-full bg-white dark:bg-neutral-800 rounded-lg shadow-lg flex items-center justify-center text-neutral-400 border border-neutral-200 dark:border-neutral-700`}
          role="region"
          aria-label="Workflow canvas"
        >
          <ReactFlowProvider>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              onInit={setReactFlowInstance}
              onDrop={onDrop}
              onDragOver={onDragOver}
              fitView
              className="bg-neutral-50"
            >
              <MiniMap />
              <Controls />
              <Background />
            </ReactFlow>
          </ReactFlowProvider>
          <div className="text-center p-4">
            <WorkflowBuilderIcon className="w-24 h-24 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
            <p className="text-xl font-medium text-neutral-700 dark:text-neutral-300">
              Workflow Canvas Area
            </p>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">
              Drag components from the palette to build your workflow.
            </p>
            <p className="text-xs mt-2 text-neutral-400 dark:text-neutral-500">
              (React Flow integration would go here)
            </p>
          </div>
        </main>

        {/* Properties Panel */}
        <aside
          id="properties-panel"
          className={`${
            isMobileView
              ? 'fixed inset-y-0 right-0 z-50 w-64 transform transition-transform duration-200 ease-in-out'
              : 'w-1/4 xl:w-1/5'
          } ${
            isMobileView && !isPropertiesOpen ? 'translate-x-full' : ''
          } h-full overflow-y-auto bg-white dark:bg-neutral-800 shadow-lg`}
        >
          <PropertiesPanel selectedNode={selectedNode} />
        </aside>
      </div>

      {/* Mobile Overlay */}
      {isMobileView && (isPaletteOpen || isPropertiesOpen) && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => {
            setIsPaletteOpen(false);
            setIsPropertiesOpen(false);
          }}
          aria-hidden="true"
        />
      )}
    </div>
  );
};

export default WorkflowBuilderPage;
