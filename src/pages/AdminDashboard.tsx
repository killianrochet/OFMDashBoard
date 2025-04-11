import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

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

  const filteredPosts = posts.filter(p => {
    if (selectedDevice) {
      const device = devices.find(d => d.device_id === selectedDevice);
      if (!device || device.id !== p.device_id) return false;
    }
  
    if (activeTab === 'pending') {
      return p.status === 'pending' || p.status === 'processing';
    } else if (activeTab === 'completed') {
      return p.status === 'completed';
    } else if (activeTab === 'failed') {
      return p.status === 'failed';
    }
  
    return true;
  });

  const statusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'pending':
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">🛠️ Tableau de bord administrateur</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {devices.map(device => (
          <Card key={device.id} className="cursor-pointer hover:shadow-md" onClick={() => setSelectedDevice(device.device_id)}>
            <CardContent className="p-4">
              <div className="font-semibold text-lg">{device.name}</div>
              <div className="text-sm text-gray-500">{device.model} • Android {device.platform_version}</div>
              <div className="text-sm mt-1">📱 ID: {device.device_id}</div>
              <div className="mt-2 text-sm text-gray-700">
                Comptes: {device.accounts.length > 0 ? device.accounts.join(', ') : 'Aucun'}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="w-full">
        <div className="flex gap-2 mb-4">
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'all' ? 'bg-gray-200' : ''}`} onClick={() => setActiveTab('all')}>Tous</button>
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'pending' ? 'bg-gray-200' : ''}`} onClick={() => setActiveTab('pending')}>⏳ En attente</button>
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'completed' ? 'bg-gray-200' : ''}`} onClick={() => setActiveTab('completed')}>✅ Succès</button>
          <button className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === 'failed' ? 'bg-gray-200' : ''}`} onClick={() => setActiveTab('failed')}>❌ Échec</button>
        </div>

        <div className="space-y-2">
          {filteredPosts.map(post => (
            <Card key={post.id}>
              <CardContent className="p-4">
                <div className="flex justify-between">
                  <div>
                    <div className="font-medium">📸 {post.post_type.toUpperCase()} pour @{post.account}</div>
                    <div className="text-sm text-gray-600">Prévu: {new Date(post.scheduled_time).toLocaleString()}</div>
                  </div>
                  <Badge className={statusColor(post.status)}>
                    {post.status === 'processing' ? 'en cours' : post.status}
                  </Badge>
                </div>
                <div className="mt-1 text-sm text-gray-500">{post.caption}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
