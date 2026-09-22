'use client';

import { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface KnowledgeBase {
  id: string;
  name: string;
  slug: string;
  description: string;
  status: string;
  is_published: boolean;
  version: string;
  created_at: string;
}

export default function KnowledgeBases() {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newKb, setNewKb] = useState({ name: '', description: '' });

  const fetchKbs = async () => {
    try {
      // Mock data for now
      setKbs([
        {
          id: 'kb_1',
          name: 'Company Knowledge Base',
          slug: 'company-kb',
          description: 'Internal company documentation and knowledge',
          status: 'published',
          is_published: true,
          version: '1.0',
          created_at: new Date().toISOString()
        },
        {
          id: 'kb_2',
          name: 'Product Documentation',
          slug: 'product-docs',
          description: 'Product manuals and user guides',
          status: 'draft',
          is_published: false,
          version: '0.9',
          created_at: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Failed to fetch KBs:', error);
    }
  };

  useState(() => {
    fetchKbs();
  });

  const createKB = async () => {
    try {
      // const response = await axios.post(`${API_URL}/api/v1/knowledge-bases`, newKb);
      // setKbs([...kbs, response.data]);
      setNewKb({ name: '', description: '' });
      setShowCreate(false);
      fetchKbs();
    } catch (error) {
      console.error('Failed to create KB:', error);
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Knowledge Bases</h1>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          {showCreate ? 'Cancel' : 'Create New'}
        </button>
      </div>

      {showCreate && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">Create Knowledge Base</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                value={newKb.name}
                onChange={(e) => setNewKb({ ...newKb, name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                value={newKb.description}
                onChange={(e) => setNewKb({ ...newKb, description: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                rows={3}
              />
            </div>
            <button
              onClick={createKB}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
            >
              Create
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {kbs.map((kb) => (
          <div key={kb.id} className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-semibold">{kb.name}</h3>
                <p className="text-gray-600 text-sm mt-1">{kb.description}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs ${
                kb.is_published 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {kb.status}
              </span>
            </div>
            <div className="mt-4 flex gap-2">
              <button className="text-primary-600 hover:text-primary-800 text-sm">
                Manage Documents
              </button>
              <button className="text-primary-600 hover:text-primary-800 text-sm">
                Configure Metadata
              </button>
              <button className="text-primary-600 hover:text-primary-800 text-sm">
                View Analytics
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}