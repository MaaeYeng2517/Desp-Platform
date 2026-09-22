'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DashboardStats {
  documents: number;
  chunks: number;
  embeddings: number;
  published: number;
  failed: number;
  processing: number;
  recall: number;
  mrr: number;
  latency: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      // In production, fetch from API
      // const response = await axios.get(`${API_URL}/api/v1/dashboard/stats`);
      // setStats(response.data);
      
      // Mock data for now
      setStats({
        documents: 1240,
        chunks: 38420,
        embeddings: 38420,
        published: 1180,
        failed: 12,
        processing: 48,
        recall: 0.91,
        mrr: 0.87,
        latency: 180
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Documents</h3>
          <p className="text-3xl font-bold mt-2">{stats?.documents}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Chunks</h3>
          <p className="text-3xl font-bold mt-2">{stats?.chunks}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Embeddings</h3>
          <p className="text-3xl font-bold mt-2">{stats?.embeddings}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Document Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>Published</span>
              <span className="font-semibold text-green-600">{stats?.published}</span>
            </div>
            <div className="flex justify-between">
              <span>Failed</span>
              <span className="font-semibold text-red-600">{stats?.failed}</span>
            </div>
            <div className="flex justify-between">
              <span>Processing</span>
              <span className="font-semibold text-yellow-600">{stats?.processing}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Retrieval Performance</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>Recall</span>
              <span className="font-semibold">{(stats?.recall || 0) * 100}%</span>
            </div>
            <div className="flex justify-between">
              <span>MRR</span>
              <span className="font-semibold">{stats?.mrr}</span>
            </div>
            <div className="flex justify-between">
              <span>Latency</span>
              <span className="font-semibold">{stats?.latency} ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}