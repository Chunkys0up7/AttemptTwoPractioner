import { renderHook, act } from '@testing-library/react-hooks';
import { useWorkflowBuilder } from '../useWorkflowBuilder';
import { Node, Edge } from '../../types/workflow';

describe('useWorkflowBuilder', () => {
  const initialNodes: Node[] = [
    {
      id: '1',
      type: 'start',
      position: { x: 0, y: 0 },
      data: { name: 'Start', componentId: 'start', config: {} },
    },
  ];

  test('initializes with correct state', () => {
    const { result } = renderHook(() => useWorkflowBuilder());
    expect(result.current.nodes).toEqual([]);
    expect(result.current.edges).toEqual([]);
    expect(result.current.selectedNode).toBeNull();
  });

  test('handles node changes', () => {
    const { result } = renderHook(() => useWorkflowBuilder());
    act(() => {
      result.current.onNodesChange(initialNodes);
    });
    expect(result.current.nodes).toEqual(initialNodes);
  });

  test('handles edge changes', () => {
    const { result } = renderHook(() => useWorkflowBuilder());
    const edge: Edge = {
      id: '1-2',
      source: '1',
      target: '2',
    };
    act(() => {
      result.current.onEdgesChange([edge]);
    });
    expect(result.current.edges).toEqual([edge]);
  });

  test('handles node selection', () => {
    const { result } = renderHook(() => useWorkflowBuilder());
    const node = initialNodes[0];
    act(() => {
      result.current.setSelectedNode(node);
    });
    expect(result.current.selectedNode).toEqual(node);
  });

  test('handles node deselection', () => {
    const { result } = renderHook(() => useWorkflowBuilder());
    const node = initialNodes[0];
    act(() => {
      result.current.setSelectedNode(node);
      result.current.setSelectedNode(null);
    });
    expect(result.current.selectedNode).toBeNull();
  });

  test('handles node connection', () => {
    const { result } = renderHook(() => useWorkflowBuilder());
    const source = '1';
    const target = '2';
    act(() => {
      result.current.onConnect({ source, target });
    });
    expect(result.current.edges).toHaveLength(1);
    expect(result.current.edges[0].source).toBe(source);
    expect(result.current.edges[0].target).toBe(target);
  });

  test('handles node drop', () => {
    const { result } = renderHook(() => useWorkflowBuilder());
    const event = {
      preventDefault: jest.fn(),
      dataTransfer: {
        getData: jest.fn()
          .mockReturnValueOnce('start')
          .mockReturnValueOnce(JSON.stringify({
            name: 'Start',
            id: 'start',
          })),
      },
      clientX: 100,
      clientY: 100,
    } as unknown as React.DragEvent;

    act(() => {
      result.current.onDrop(event);
    });

    expect(result.current.nodes).toHaveLength(1);
    expect(result.current.nodes[0].data.name).toBe('Start');
  });
});
