'use client';

import { useState } from 'react';

export default function Workflows() {
  const [nodes, setNodes] = useState([
    { id: '1', type: 'source', name: 'PDF Source', position: { x: 100, y: 100 } },
    { id: '2', type: 'process', name: 'Text Extractor', position: { x: 100, y: 200 } },
    { id: '3', type: 'process', name: 'Chunker', position: { x: 100, y: 300 } },
    { id: '4', type: 'index', name: 'Vector Index', position: { x: 100, y: 400 } }
  ]);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Visual Workflow Builder</h1>
        <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
          Save Workflow
        </button>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Component Palette */}
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-4">Components</h3>
          <div className="space-y-2">
            <div className="p-2 bg-blue-50 rounded border border-blue-200 cursor-move">
              Source
            </div>
            <div className="p-2 bg-green-50 rounded border border-green-200 cursor-move">
              Ingestion
            </div>
            <div className="p-2 bg-yellow-50 rounded border border-yellow-200 cursor-move">
              Processing
            </div>
            <div className="p-2 bg-purple-50 rounded border border-purple-200 cursor-move">
              Metadata
            </div>
            <div className="p-2 bg-red-50 rounded border border-red-200 cursor-move">
              Index
            </div>
            <div className="p-2 bg-indigo-50 rounded border border-indigo-200 cursor-move">
              Retrieval
            </div>
            <div className="p-2 bg-pink-50 rounded border border-pink-200 cursor-move">
              RAG
            </div>
          </div>
        </div>

        {/* Canvas */}
        <div className="col-span-3 bg-gray-50 rounded-lg shadow p-4">
          <h3 className="font-semibold mb-4">Workflow Canvas</h3>
          <div className="relative bg-white rounded border-2 border-dashed border-gray-300" style={{ height: '600px' }}>
            {nodes.map((node) => (
              <div
                key={node.id}
                className="absolute bg-white p-3 rounded-lg shadow border-2 border-primary-200"
                style={{ left: node.position.x, top: node.position.y }}
              >
                <div className="text-xs text-primary-600 font-medium">{node.type}</div>
                <div className="text-sm font-semibold">{node.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}