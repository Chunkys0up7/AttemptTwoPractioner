/**
 * Custom hook for workflow builder state management
 */
export const useWorkflowBuilder = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  const onConnect = useCallback((params: Edge | Connection) => 
    setEdges((eds) => addEdge(params, eds)), 
    [setEdges]
  );

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

  return {
    nodes,
    edges,
    selectedNode,
    reactFlowInstance,
    onNodesChange,
    onEdgesChange,
    onConnect,
    onDrop,
    setSelectedNode,
  };
};
