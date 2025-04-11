import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

interface Device {
  id: number;
  name: string;
  model: string;
  platform_version: string;
  device_id: string;
  accounts: string[];
}

interface Post {
  id: number;
  device_id: number;
  scheduled_time: string;
  caption: string;
  post_type: string;
  status: string;
  account?: string;
}

export default function AdminDashboard() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'all' | 'pending' | 'completed' | 'failed'>('all');

  useEffect(() => {
    fetch('http://localhost:5000/devices')
      .then(res => res.json())
      .then(setDevices);

    fetch('http://localhost:5000/posts')
      .then(res => res.json())
      .then(setPosts);
  }, []);

  const filteredPosts = posts.filter(post => {
    if (selectedDevice) {
      const device = devices.find(d => d.device_id === selectedDevice);
      if (!device || device.id !== post.device_id) return false;
    }

    if (activeTab === 'all') return true;
    if (activeTab === 'pending') return post.status.toLowerCase() === 'pending';
    if (activeTab === 'completed') return post.status.toLowerCase() === 'completed';
    if (activeTab === 'failed') return post.status.toLowerCase() === 'failed';
    return false;
  });

  const formatStatus = (status: string) => {
    switch (status.toLowerCase()) {
      case 'processing':
        return 'En cours';
      case 'pending':
        return 'En attente';
      case 'completed':
        return 'Succès';
      case 'failed':
        return 'Échec';
      default:
        return status.charAt(0).toUpperCase() + status.slice(1);
    }
  };

  const statusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm text-center font-semibold';
      case 'failed':
        return 'bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm text-center font-semibold';
      case 'pending':
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm text-center font-semibold';
      default:
        return 'bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm text-center font-semibold';
    }
  };

  return (
    <div className="p-6 min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">🛠️ Tableau de bord administrateur</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {devices.map(device => (
          <Card key={device.id} className={`cursor-pointer hover:shadow-md transition ${selectedDevice === device.device_id ? 'ring-2 ring-purple-400' : ''}`} onClick={() => setSelectedDevice(device.device_id)}>
            <CardContent className="p-4">
              <div className="font-semibold text-lg text-gray-800">{device.name}</div>
              <div className="text-sm text-gray-500">{device.model} • Android {device.platform_version}</div>
              <div className="text-sm mt-1 text-gray-600">📱 ID: {device.device_id}</div>
              <div className="mt-2 text-sm text-gray-700">
                Comptes: {device.accounts.length > 0 ? device.accounts.join(', ') : 'Aucun'}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="w-full">
        <div className="flex flex-wrap gap-2 mb-6 justify-center">
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'all' ? 'bg-gray-200' : 'bg-white'} hover:bg-gray-100`} onClick={() => setActiveTab('all')}>
            Tous ({posts.length})
          </button>
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'pending' ? 'bg-gray-200' : 'bg-white'} hover:bg-gray-100`} onClick={() => setActiveTab('pending')}>
            ⏳ En attente ({posts.filter(p => p.status.toLowerCase() === 'pending').length})
          </button>
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'completed' ? 'bg-gray-200' : 'bg-white'} hover:bg-gray-100`} onClick={() => setActiveTab('completed')}>
            ✅ Succès ({posts.filter(p => p.status.toLowerCase() === 'completed').length})
          </button>
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'failed' ? 'bg-gray-200' : 'bg-white'} hover:bg-gray-100`} onClick={() => setActiveTab('failed')}>
            ❌ Échec ({posts.filter(p => p.status.toLowerCase() === 'failed').length})
          </button>
        </div>

        <div className="space-y-4">
          {filteredPosts.map(post => (
            <Card key={post.id} className="hover:shadow transition">
              <CardContent className="p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-lg text-gray-800">📸 {post.post_type.toUpperCase()} pour @{post.account}</div>
                    <div className="text-sm text-gray-600">Prévu: {new Date(post.scheduled_time).toLocaleString()}</div>
                  </div>
                  <Badge className={statusColor(post.status)}>
                    {formatStatus(post.status)}
                  </Badge>
                </div>
                <div className="mt-2 text-sm text-gray-500">{post.caption}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
