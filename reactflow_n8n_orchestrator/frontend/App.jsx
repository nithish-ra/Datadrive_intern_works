import { useState, useCallback, useRef } from 'react';
import ReactFlow, { 
  ReactFlowProvider,
  Controls, 
  Background, 
  applyNodeChanges, 
  applyEdgeChanges,
  addEdge,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import Sidebar from './Sidebar';
import CustomNode from './CustomNode'; // 1. IMPORT YOUR CUSTOM NODE

// 2. REGISTER THE CUSTOM NODE TYPE
const nodeTypes = { custom: CustomNode };

const initialNodes = [
  { id: '1', type: 'input', data: { label: 'Start Trigger' }, position: { x: 250, y: 50 } },
];

let id = 0;
const getId = () => `dndnode_${id++}`;

export default function App() {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow-type');
      const label = event.dataTransfer.getData('application/reactflow-label');

      if (typeof type === 'undefined' || !type) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode = {
        id: getId(),
        type,
        position,
        data: { label: `${label}` },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance]
  );

  // The upgraded function to save and monitor the workflow
  const onSave = async () => {
    if (reactFlowInstance) {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.type === 'custom') {
            return {
              ...node,
              style: { 
                ...node.style, 
                border: '1px solid #555', // Reset to normal gray border
                boxShadow: 'none'         // Remove the glow
              },
            };
          }
          return node;
        })
      );
      const flow = reactFlowInstance.toObject(); // Grabs all nodes, edges, and viewport data
      
      try {
        const response = await fetch('http://127.0.0.1:8000/api/workflows/save/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(flow),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          // 1. Log the exact data n8n sent back so you can see the AI's summary
          console.log("n8n Execution Data:", data);
          alert("Workflow Executed Successfully!");

          // 2. Loop through the nodes and update their style to glow green!
          setNodes((nds) =>
            nds.map((node) => {
              // We only want to turn the action nodes green, not the Start Trigger
              if (node.type === 'custom') {
                return {
                  ...node,
                  style: { 
                    ...node.style, 
                    border: '2px solid #4CAF50', 
                    boxShadow: '0 0 15px rgba(76, 175, 80, 0.6)' // Green glow
                  },
                };
              }
              return node;
            })
          );

        } else {
          alert("Failed to execute workflow. Check the console.");
          console.error("Save failed:", data);
        }
      } catch (error) {
        alert("Error connecting to the Django backend. Is the server running?");
        console.error("Network error:", error);
      }
    }
  };

  // NEW: Function to reset the canvas
  const onClear = useCallback(() => {
    setNodes(initialNodes); // Resets back to just the Start Trigger
    setEdges([]);           // Removes all connection lines
  }, [setNodes, setEdges]);

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh' }}>
      <ReactFlowProvider>
        
        {/* Pass BOTH functions down into the Sidebar */}
        <Sidebar onSave={onSave} onClear={onClear} />
        
        <div style={{ flexGrow: 1, height: '100%' }} ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes} // 3. TELL REACT FLOW TO USE THE CUSTOM NODE
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            fitView
          >
            <Background color="#ccc" gap={16} />
            <Controls />
          </ReactFlow>
        </div>

      </ReactFlowProvider>
    </div>
  );
}